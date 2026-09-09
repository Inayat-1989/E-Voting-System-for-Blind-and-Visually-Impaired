import json
import os
import time
import uuid

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
from pydantic import BaseModel
from gtts import gTTS
from faster_whisper import WhisperModel

from .models import Voter

# ---------- Lazy-loaded models/clients ----------

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print("DEBUG: Whisper model loaded as 'base'")
    return _whisper_model


def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables.")
    return genai.Client(api_key=api_key)


class UserIntentSchema(BaseModel):
    action: str  # "login", "help", "repeat", "incomplete_cnic", or "unknown"
    cnic: str


SCRIPTED_MESSAGES = {
    "welcome": "Khush aamdeed. Apna shanakhti card number bolein, jo terah numbers ka hota hai.",
    "help": "Apna shanakhti card number bolein. Jaise char do ek zero one do teen char panch che saat aath zero ek.",
    "repeat": "Theek hai, dobara bolein. Apna shanakhti card number saaf saaf bolein.",
    "unknown": "Samajh nahi aaya. Sirf apna shanakhti card number bolein.",
    "silence": "Awaz samajh nahi aayi. Dobara koshish karein.",
    "login_success": "Aap ki tasdeeq ho gayi hai. Khush aamdeed.",
    "login_not_found": "Yeh number hamare paas mojood nahi hai.",
    "max_attempts": "Baar baar koshish ke bawajood tasdeeq nahi hui. Bara-e-karam staff se baat karein.",
    "incomplete_cnic": "Apka CNIC number pura nahi hai. Bara-e-marbani pura CNIC number bolein.",
}

MAX_ATTEMPTS = 3
print(f"DEBUG: MAX_ATTEMPTS is set to {MAX_ATTEMPTS}")


def generate_urdu_tts(text_prompt):
    """Generates Urdu speech audio using gTTS and returns a URL the browser can play."""
    tts = gTTS(text=text_prompt, lang="ur")
    audio_filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
    output_dir = os.path.join("static", "accounts", "audio")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, audio_filename)
    tts.save(file_path)
    return f"/static/accounts/audio/{audio_filename}"


def login_voter(request):
    if request.method == "POST":
        cnic_input = request.POST.get("cnic", "").strip()
        voter = Voter.objects.filter(cnic=cnic_input).first()
        if not voter:
            messages.error(request, "No voter found with that CNIC.")
            return render(request, "accounts/login.html")
        if not request.session.session_key:
            request.session.create()
        voter.current_session_key = request.session.session_key
        request.session["voter_id"] = voter.id
        voter.save()
        messages.success(request, "You are a verified Disabled User. Welcome!")
        return redirect("elections")

    return render(request, "accounts/login.html")


def start_voice_login(request):
    """Called once when the voter clicks Start. Resets the attempt counter and speaks the welcome message."""
    request.session["voice_attempts"] = 0
    audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["welcome"])
    return JsonResponse({
        "status": "info",
        "message": SCRIPTED_MESSAGES["welcome"],
        "audio_url": audio_url,
        "continue_listening": True
    })


@csrf_exempt
def process_speech(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({"status": "error", "message": "No audio file provided."}, status=400)

    temp_dir = os.path.join("files", "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.webm")

    with open(temp_path, "wb+") as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    try:
        # ---------- Whisper (Speech to Text) ----------
        whisper_start = time.time()
        model = get_whisper_model()
        segments, info = model.transcribe(temp_path, language="ur")
        user_text = "".join(segment.text for segment in segments).strip()
        print(f"DEBUG: Whisper took {time.time() - whisper_start:.1f} seconds")

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not user_text:
            audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["silence"])
            return JsonResponse({
                "status": "error", "action": "silence",
                "message": SCRIPTED_MESSAGES["silence"], "audio_url": audio_url,
                "continue_listening": True
            }, status=400)

        # ---------- Gemini (Intent classification) ----------
        prompt = f"""
        Classify the voter's spoken text during a voice-based login screen:
        "{user_text}"

        Rules:
        1. If the text contains exactly a 13-digit CNIC (digits only, no dashes; convert
           spoken words/numbers to numeric digits), set action="login" and cnic to those digits.
        2. If the text contains some digits but fewer than 13, set action="incomplete_cnic"
           and cnic to whatever digits were found.
        3. If the voter sounds confused, lost, or is asking what to do / how this works,
           set action="help" and cnic to "".
        4. If the voter is asking you to repeat or say the instructions again,
           set action="repeat" and cnic to "".
        5. Otherwise, set action="unknown" and cnic to "".
        """

        gemini_start = time.time()
        gemini_client = get_gemini_client()
        intent_data = None
        last_error = None

        for attempt in range(3):
            try:
                gemini_response = gemini_client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=UserIntentSchema,
                    ),
                )
                intent_data = json.loads(gemini_response.text)
                break
            except Exception as e:
                last_error = e

        print(f"DEBUG: Gemini took {time.time() - gemini_start:.1f} seconds")

        if intent_data is None:
            raise last_error

        action = intent_data.get("action")
        cnic_input = intent_data.get("cnic", "")
        attempts = request.session.get("voice_attempts", 0)

        # ---------- Routing ----------

        if action == "login" and cnic_input:
            voter = Voter.objects.filter(cnic=cnic_input).first()

            if voter:
                if not request.session.session_key:
                    request.session.create()
                voter.current_session_key = request.session.session_key
                request.session["voter_id"] = voter.id
                voter.save()
                request.session["voice_attempts"] = 0

                audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["login_success"])
                return JsonResponse({
                    "status": "success",
                    "action": "login",
                    "cnic": cnic_input,
                    "voter_id": voter.id,
                    "message": SCRIPTED_MESSAGES["login_success"],
                    "audio_url": audio_url,
                    "transcription": user_text,
                    "continue_listening": False,
                    "redirect_url": "/elections/"
                })
            else:
                attempts += 1
                request.session["voice_attempts"] = attempts
                if attempts >= MAX_ATTEMPTS:
                    audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["max_attempts"])
                    return JsonResponse({
                        "status": "error", "action": "max_attempts",
                        "message": SCRIPTED_MESSAGES["max_attempts"],
                        "audio_url": audio_url, "continue_listening": False
                    }, status=404)

                audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["login_not_found"])
                return JsonResponse({
                    "status": "error",
                    "action": "login_failed",
                    "cnic": cnic_input,
                    "message": SCRIPTED_MESSAGES["login_not_found"],
                    "audio_url": audio_url,
                    "transcription": user_text,
                    "continue_listening": True
                }, status=404)

        elif action in ("help", "repeat", "unknown", "incomplete_cnic"):
            attempts += 1
            request.session["voice_attempts"] = attempts
            if attempts >= MAX_ATTEMPTS:
                audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["max_attempts"])
                return JsonResponse({
                    "status": "error", "action": "max_attempts",
                    "message": SCRIPTED_MESSAGES["max_attempts"],
                    "audio_url": audio_url, "continue_listening": False
                }, status=400)

            audio_url = generate_urdu_tts(SCRIPTED_MESSAGES[action])
            return JsonResponse({
                "status": "info",
                "action": action,
                "message": SCRIPTED_MESSAGES[action],
                "audio_url": audio_url,
                "transcription": user_text,
                "continue_listening": True
            })

        audio_url = generate_urdu_tts(SCRIPTED_MESSAGES["unknown"])
        return JsonResponse({
            "status": "error", "action": "unknown",
            "message": SCRIPTED_MESSAGES["unknown"],
            "audio_url": audio_url, "transcription": user_text,
            "continue_listening": True
        }, status=400)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def logout_voter(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")
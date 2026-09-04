import json
import os 
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI  # OpenAI client for Whisper API
from google import genai
from google.genai import types
from pydantic import BaseModel
from .models import Voter
from elevenlabs.client import ElevenLabs

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
gemini_client = genai.Client()
eleven_client = ElevenLabs()

import os
from django.shortcuts import render, redirect
from django.contrib import messages
from openai import OpenAI

def get_openai_client():
    """
    Safely retrieves the OpenAI API key and instantiates the client.
    Fails only when an API call is attempted, not during server startup.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment variables.")
    return OpenAI(api_key=api_key)

def analyze_vote_view(request):
    """
    Example view utilizing the OpenAI client safely.
    """
    if request.method == "POST":
        user_input = request.POST.get("prompt", "")
        
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}]
            )
            result = response.choices[0].message.content
            return render(request, "accounts/result.html", {"result": result})
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("home")
        except Exception as e:
            messages.error(request, f"OpenAI API Error: {str(e)}")
            return redirect("home")

    return render(request, "accounts/analyze.html")

# Schema for structured JSON output from Gemini

class UserIntentSchema(BaseModel):
    action: str  # e.g., "login", "help", "unknown"
    cnic: str    # Cleaned CNIC string with digits only, e.g., "4210112345671"


def generate_urdu_tts(text_prompt):
    """Generates audio file using ElevenLabs Urdu voice model and returns relative URL."""
    audio_stream = eleven_client.generate(
        text=text_prompt,
        voice="Rachel",  # Select an Urdu-supported voice ID or custom voice from your ElevenLabs dashboard
        model="eleven_multilingual_v2"
    )
    
    # Save audio file to static directory for playback
    audio_filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
    output_dir = os.path.join("static", "accounts", "audio")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, audio_filename)
    
    with open(file_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
            
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


@csrf_exempt
def process_speech(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    audio_file = request.FILES.get("audio")
    if not audio_file:
        return JsonResponse({"status": "error", "message": "No audio file provided."}, status=400)

    # 1. Save temporary audio file
    temp_dir = os.path.join("files", "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, audio_file.name)

    with open(temp_path, "wb+") as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    try:
        # 2. OpenAI Whisper API (Speech to Text)
        with open(temp_path, "rb") as audio:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio,
                language="ur"
            )
        user_text = transcription.text.strip()

        # Clean up audio file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # 3. Gemini Flash API (Intent Extraction & CNIC Parsing)
        prompt = f"""
        Extract the user's login intent and CNIC number from this spoken text:
        "{user_text}"
        
        Rules:
        1. Extract the 13-digit CNIC if present (digits only, no dashes). 
           Convert spoken Urdu digits or text numbers (e.g., 'چار دو ایک zero') to numeric digits.
        2. Set 'action' to 'login' if user intends to log in or provided CNIC numbers.
        3. If no CNIC digits are detected, set 'action' to 'unknown' and 'cnic' to empty string "".
        """

        gemini_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UserIntentSchema,
            ),
        )

        # Parse Gemini JSON response
        intent_data = json.loads(gemini_response.text)

        # 4. Perform Voter Lookup and Session Creation
        if intent_data.get("action") == "login" and intent_data.get("cnic"):
            cnic_input = intent_data["cnic"]
            voter = Voter.objects.filter(cnic=cnic_input).first()

            if voter:
                if not request.session.session_key:
                    request.session.create()
                voter.current_session_key = request.session.session_key
                request.session["voter_id"] = voter.id
                voter.save()

                return JsonResponse({
                    "status": "success",
                    "action": "login",
                    "cnic": cnic_input,
                    "voter_id": voter.id,
                    "message": "Voter authenticated successfully.",
                    "transcription": user_text
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "action": "login_failed",
                    "cnic": cnic_input,
                    "message": f"No voter found with CNIC {cnic_input}.",
                    "transcription": user_text
                }, status=404)

        return JsonResponse({
            "status": "error",
            "action": "unknown",
            "message": "Could not extract valid CNIC or login intent.",
            "transcription": user_text
        }, status=400)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def logout_voter(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")

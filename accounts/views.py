from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Voter


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


@csrf_exempt  # Use proper CSRF tokens in production
def process_speech(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "")

            # TODO: Add your custom backend logic here
            # (e.g., save to database, run NLP, trigger an action)
            response_text = f"Backend received your speech: '{user_text}'"

            return JsonResponse({"status": "success", "message": response_text})
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)


def logout_voter(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")

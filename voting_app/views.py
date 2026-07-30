from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Candidate, Election, Vote, Voter


def home(request):
    return render(request, "login.html")


# def register_voter(request):
#     if request.method == "POST":
#         full_name = request.POST.get("full_name", "").strip()
#         cnic = request.POST.get("cnic", "").strip()
#         email = request.POST.get("email", "").strip()
#         is_disabled = request.POST.get("is_disabled") == "on"

#         if not full_name or not cnic or not email:
#             messages.error(request, "Full name, CNIC and email are required.")
#             return redirect("register")

#         if len(cnic) != 13 or not cnic.isdigit():
#             messages.error(request, "CNIC must be exactly 13 digits.")
#             return redirect("register")

#         # if not is_disabled:
#         #     messages.error(request, "Only disabled voters can register for this system.")
#         #     return redirect("register")

#         voter, created = Voter.objects.get_or_create(
#             cnic=cnic,
#             defaults={"full_name": full_name, "email": email, "is_disabled": True, "is_verified": False},
#         )
#         if not created:
#             voter.full_name = full_name
#             voter.email = email
#             voter.is_disabled = True
#             voter.is_verified = False
#             voter.save()

#         token = voter.generate_verification_token()
#         voter.save()
#         verification_link = f"http://127.0.0.1:8000/verify/{token}/"
#         send_mail(
#             subject="Verify your e-voting account",
#             message=f"Hello {voter.full_name},\n\nPlease verify your account by clicking: {verification_link}",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[voter.email],
#             fail_silently=False,
#         )

#         messages.success(request, "Registration successful. A verification link has been sent to your email.")
#         return redirect("login")

#     return render(request, "register.html")


# def verify_email(request, token):
#     voter = Voter.objects.filter(verification_token=token).first()
#     if not voter:
#         messages.error(request, "The verification link is invalid or expired.")
#         return redirect("home")

#     voter.is_verified = True
#     voter.verification_token = ""
#     voter.save()
#     messages.success(request, "Your email has been verified. You can now log in.")
#     return redirect("login")


def login_voter(request):
    if request.method == "POST":
        cnic = request.POST.get("cnic", "").strip()
        voter = Voter.objects.filter(cnic=cnic).first() #we are going to fetch/comapre the cnic of this post value to the database value.
        if not voter:
            messages.error(request, "No voter found with that CNIC.")
            return render(request, "login.html")

        voter.is_verified = True
        token = voter.generate_verification_token()
        voter.save()
        # verification_link = f"http://127.0.0.1:8000/verify-login/{token}/"
        # send_mail(
        #     subject="Login verification",
        #     message=f"Hello {voter.full_name},\n\nUse this link to access your account: {verification_link}",
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[voter.email],
        #     fail_silently=False,
        # )
        # messages.success(request, "A login verification link has been sent to your email.")
        # request.session["pending_cnic"] = voter.cnic

        request.session["voter_id"] = voter.id
        voter.verification_token = ""
        voter.save()
        messages.success(request, "You are a verified Disabled User. Welcome!")
        return redirect("elections")

    return render(request, "login.html")


# def verify_login(request, token):
#     voter = Voter.objects.filter(verification_token=token).first()
#     if not voter:
#         messages.error(request, "The login link is invalid or expired.")
#         return redirect("home")

#     request.session["voter_id"] = voter.id
#     voter.verification_token = ""
#     voter.save()
#     messages.success(request, "Login successful.")
#     return redirect("elections")


@csrf_exempt # Use proper CSRF tokens in production
def process_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_text = data.get('text', '')
            
            # TODO: Add your custom backend logic here 
            # (e.g., save to database, run NLP, trigger an action)
            response_text = f"Backend received your speech: '{user_text}'"
            
            return JsonResponse({'status': 'success', 'message': response_text})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)



def logout_voter(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")


def elections_list(request):
    if not request.session.get("voter_id"):
        messages.error(request, "Please log in first.")
        return redirect("login")

    elections = Election.objects.all().prefetch_related("candidates")
    return render(request, "elections.html", {"elections": elections})


def vote(request, election_id):
    if not request.session.get("voter_id"):
        messages.error(request, "Please log in first.")
        return redirect("login")

    voter = Voter.objects.get(id=request.session["voter_id"])
    election = Election.objects.get(id=election_id)

    if not voter.is_disabled:
        messages.error(request, "Only disabled voters are allowed to vote in this system.")
        return render(request, "vote.html", {"election": election, "voter": voter, "allowed": False})

    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        candidate = Candidate.objects.filter(id=candidate_id, election=election).first()
        if not candidate:
            messages.error(request, "Please select a valid candidate.")
            return render(request, "vote.html", {"election": election, "voter": voter, "allowed": True})
        if Vote.objects.filter(election=election, voter=voter).exists():
            messages.error(request, "You have already voted in this election.")
            return render(request, "vote.html", {"election": election, "voter": voter, "allowed": True})
        Vote.objects.create(election=election, voter=voter, candidate=candidate)
        messages.success(request, "Your vote was recorded.")
        return render(request, "vote.html", {"election": election, "voter": voter, "allowed": True, "submitted": True})

    return render(request, "vote.html", {"election": election, "voter": voter, "allowed": True})

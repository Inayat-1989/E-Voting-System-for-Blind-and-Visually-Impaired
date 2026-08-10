from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User

# Create your views here.
# def home(request):
#     return render(request, "accounts/login.html")

def login_voter(request):
    render(request, "accounts/login.html")
    if request.method == "POST":
        cnic = request.POST.get("cnic", "").strip()
        voter = User.objects.filter(cnic=cnic).first() #we are going to fetch/comapre the cnic of this post value to the database value.
        if not voter:
            messages.error(request, "No voter found with that CNIC.")
            return render(request, "accounts/login.html")
        request.session["voter_id"] = voter.id
        voter.save()
        messages.success(request, "You are a verified Disabled User. Welcome!")
        return redirect("elections")

    return render(request, "accounts/login.html")   

@csrf_exempt
def process_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_text = data.get('text', '')

            cnic = ''.join(ch for ch in user_text if ch.isdigit())

            print("SPEECH VIEW HIT — raw text:", repr(user_text))      # ← add
            print("SPEECH VIEW — cleaned cnic:", repr(cnic))           # ← add

            exists = User.objects.filter(cnic=cnic).exists()

            print("SPEECH VIEW — exists:", exists)                     # ← add

            if exists:
                return JsonResponse({'verified': True, 'message': 'Verified voter'})
            else:
                return JsonResponse({'verified': False, 'message': 'No voter found with that CNIC'})

        except json.JSONDecodeError:
            return JsonResponse({'verified': False, 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'verified': False, 'message': 'Only POST allowed'}, status=405)

def logout_voter(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("login")


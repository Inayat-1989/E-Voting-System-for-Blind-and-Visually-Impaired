from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User

# Create your views here.
def home(request):
    return render(request, "accounts/login.html")

def login_voter(request):
    if request.method == "POST":
        cnic = request.POST.get("cnic", "").strip()
        voter = User.objects.filter(cnic=cnic).first() #we are going to fetch/comapre the cnic of this post value to the database value.
        if not voter:
            messages.error(request, "No voter found with that CNIC.")
            return render(request, "accounts/login.html")
        request.session["voter_id"] = voter.id
        voter.save()
        messages.success(request, "You are a verified Disabled User. Welcome!")
        return render(request, "voting_app/elections.html")

    return render(request, "accounts/login.html")   

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
    return redirect("accounts/login")
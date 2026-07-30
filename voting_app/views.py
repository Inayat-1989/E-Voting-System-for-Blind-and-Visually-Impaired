from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Candidate, Election, Vote, Voter


def elections_list(request):
    if not request.session.get("voter_id"):
        messages.error(request, "Please log in first.")
        return redirect("account/login")

    # .prefetch_related("candidates")
    elections = Election.objects.all()
    if elections:
        print("Da ana koas di")
        for election in elections:
            print(election.title)
    else:
        print("Za was sa wakam")
    return render(request, "voting_app/elections.html", {"elections": elections})


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

from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import BallotBox, Candidate, Election, PollingStation, Constituency
from accounts.models import Voter
from .decorators import voter_required
import re


@voter_required
def elections_list(request):
    voter_id = request.session.get("voter_id")
    if not voter_id:
        messages.error(request, "Please log in first.")
        return redirect("account/login")

    election = Election.objects.first()
    return render(request, "voting_app/elections.html", {"election": election})


def assembly_types(request, title):
    voter = Voter.objects.get(id=request.session.get("voter_id"))
    return render(
        request,
        "voting_app/assembly_types.html",
        {"election_title": title, "voter": voter},
    )


@voter_required
def show_candidates(request, title, assembly):
    election = Election.objects.filter(title=title, election_type=assembly).first()
    print(election)
    voter_id = request.session.get("voter_id")
    voter = Voter.objects.get(id=voter_id)
    candidates = None
    if assembly == "NATIONAL":
        candidates = Candidate.objects.filter(
            constituency=voter.assigned_constituency_na, assembly_type=assembly
        )
    elif assembly == "PROVINCIAL":
        candidates = Candidate.objects.filter(
            constituency=voter.assigned_constituency_pa, assembly_type=assembly
        )
    else:
        messages.error(request, "Invalid Assembly Type")
        return render(request, "voting_app/elections.html")
    if not candidates:
        messages.error(request, "No such candidates exists!")
        return render(request, "voting_app/elections.html")
    return render(
        request,
        "voting_app/vote.html",
        {"election_id": election.pk, "candidates": candidates, "voter_id": voter.id},
    )


@voter_required
def vote_view(request):
    """Handles automated constituency matching, ballot box auto-generation,

    and secure vote recording for the logged-in voter.
    """
    if request.method != "POST":
        messages.error("Method is not POST!")
        return render(request, "voting_app/elections.html")
    election = Election.objects.get(pk=request.POST.get("election_id"))
    candidate = Candidate.objects.get(candidate_id=request.POST.get("candidate_id"))
    voter = Voter.objects.get(id=request.session.get("voter_id"))
    election_type = election.election_type
    ballot_box = None
    polling_station = None
    constituency = None
    constituency_id = re.sub(r"[^0-9]", "", voter.assigned_constituency_na)
    polling_station, created = PollingStation.objects.get_or_create(
        station_id=f"PS-{constituency_id}",
        defaults={
            "election": election,
            "station_id": f"PS-{constituency_id}",
            "location_name": "Government Building",
            "constituency_na": voter.assigned_constituency_na,
            "constituency_pa": voter.assigned_constituency_pa,
            "is_connected_to_central_server": True,
        },
    )
    polling_station.save()
    if election_type == "NATIONAL":
        constituency, created = Constituency.objects.get_or_create(
            constituency_id=voter.assigned_constituency_na,
            defaults={
                "election": election,
                "constituency_id": voter.assigned_constituency_na,
                "province": "Punjab",  # Voter specified Province
                "assembly_type": election_type,
                "registered_voters_count": 10,
            },
        )
        voter.has_voted_na = True
    elif election_type == "PROVINCIAL":
        constituency, created = Constituency.objects.get_or_create(
            constituency_id=voter.assigned_constituency_pa,
            defaults={
                "election": election,
                "constituency_id": voter.assigned_constituency_pa,
                "province": "Punjab",  # Voter specified Province
                "assembly_type": election_type,
                "registered_voters_count": 10,
            },
        )
        voter.has_voted_pa = True
    constituency.save()
    voter.save()
    constituency_id = re.sub(r"[^a-zA-Z]", "", constituency.constituency_id)
    ballot_box, created = BallotBox.objects.get_or_create(
        ballot_box_id=f"BOX-{polling_station.station_id}-{constituency_id}",
        defaults={
            "election": election,
            "ballot_box_id": f"BOX-{polling_station.station_id}-{constituency_id}",
            "assembly_type": election_type,
            "constituency": constituency,
            "vote_tallies": {},
            "total_votes_cast": 0,
        },
    )
    ballot_box.save()
    return vote(request, candidate, ballot_box, election)


def vote(request, candidate, ballot_box, election):
    with transaction.atomic():
        tallies = ballot_box.vote_tallies or {}
        current_count = tallies.get(str(candidate.candidate_id), 0)
        tallies[str(candidate.candidate_id)] = current_count + 1
        ballot_box.vote_tallies = tallies
        ballot_box.total_votes_cast += 1
        ballot_box.save()
        messages.success(request, "Your vote has been Successfully Casted!")
    return render(request, "voting_app/elections.html", {"election": election})

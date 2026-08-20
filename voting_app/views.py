import re

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.models import Voter

from .decorators import voter_required
from .models import BallotBox, Candidate, Constituency, ConstituencyMapping, Election, PollingStation


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
    if voter.has_voted_na and voter.has_voted_pa:
        election = Election.objects.first()
        messages.success(request, "You have voted both votes Successfully!")
        return render(request, "voting_app/elections.html", {"election": election})
    return render(
        request,
        "voting_app/assembly_types.html",
        {"election_title": title, "voter": voter},
    )


@voter_required
def show_candidates(request, title, assembly):
    election = Election.objects.filter(title=title).first()
    if not election:
        messages.error(request, "No Elections at this Moment exists!")
        return render(request, "voting_app/elections.html")
    voter_id = request.session.get("voter_id")
    voter = Voter.objects.get(id=voter_id)
    candidates = None
    constituency_mapping = ConstituencyMapping.objects.get(block_code=voter.block_code)
    if not constituency_mapping:
        messages.error(request, "You can't Vote, Invalid Voter!")
        return render(request, "voting_app/elections.html")
    if assembly == "NATIONAL":
        candidates = Candidate.objects.filter(constituency=constituency_mapping.constituency_na, assembly_type=assembly)
    elif assembly == "PROVINCIAL":
        candidates = Candidate.objects.filter(constituency=constituency_mapping.constituency_pa, assembly_type=assembly)
    else:
        messages.error(request, "Invalid Assembly Type")
        return render(request, "voting_app/elections.html")
    if not candidates.exists():
        messages.error(request, "No such candidates exists!")
        return render(request, "voting_app/elections.html")
    return render(
        request,
        "voting_app/vote.html",
        {"election_id": election.pk, "candidates": candidates, "voter_id": voter.id},
    )


@voter_required
def vote_view(request):
    if request.method != "POST":
        messages.error(request, "Method is not POST!")
        return render(request, "voting_app/elections.html")
    try:
        election = Election.objects.get(pk=request.POST.get("election_id"))
        candidate = Candidate.objects.get(candidate_id=request.POST.get("candidate_id"))
        voter = Voter.objects.get(id=request.session.get("voter_id"))
    except (Election.DoesNotExist, Candidate.DoesNotExist, Voter.DoesNotExist):
        messages.error(request, "Can't Vote Error Occured 404!")
        return render(request, "voting_app/elections.html")

    election_type = candidate.assembly_type
    ballot_box = None
    polling_station = None
    constituency = None
    constituency_mapping = ConstituencyMapping.objects.get(block_code=voter.block_code)
    if not constituency_mapping:
        messages.error(request, "No Constituency Mapping Exists for the Block")
        return render(request, "voting_app/elections.html")
    constituency_id_na = constituency_mapping.constituency_na
    constituency_id_pa = constituency_mapping.constituency_pa
    constituency_id = constituency_id_na + "-" + constituency_id_pa
    start, end = voter.serial_range

    polling_station, _created = PollingStation.objects.get_or_create(
        station_id=f"PS-{constituency_id}",
        defaults={
            "election": election,
            "station_id": f"PS-{constituency_id}",
            "location_name": "Government Building",
            "block_code": voter.block_code,
            "serial_number_start_from": start,
            "serial_number_end_at": end,
            # "constituency_na": constituency_id_na,
            # "constituency_pa": constituency_id_pa,
            "is_connected_to_central_server": True,
        },
    )
    polling_station.save()
    registered_voters_count = Voter.objects.filter(block_code=constituency_mapping.block_code).count()
    constituency, _created = Constituency.objects.get_or_create(
        constituency_id=candidate.constituency.constituency_id,
        defaults={
            "election": election,
            "constituency_id": candidate.constituency.constituency_id,
            "province": voter.province,
            "assembly_type": election_type,
            "registered_voters_count": registered_voters_count,
        },
    )
    constituency.save()
    constituency_id = re.sub(r"[^a-zA-Z]", "", constituency.constituency_id)
    ballot_box, _created = BallotBox.objects.get_or_create(
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
    if ballot_box.total_votes_cast == constituency.registered_voters_count:
        messages.error(request, "Already Maxed out Votes Casted for this Constituency")
        return render(request, "voting_app/elections.html", {"election": election})
    is_casted = vote(request, candidate, ballot_box, election)
    if is_casted:
        if election_type == "NATIONAL":
            voter.has_voted_na = True
        elif election_type == "PROVINCIAL":
            voter.has_voted_pa = True
        voter.save()
        messages.success(request, "Your vote has been Successfully Casted!")
    else:
        messages.error(request, "Vote Casting Failed Retry!")
        return render(request, "voting_app/elections.html", {"election": election})
    return render(request, "voting_app/elections.html", {"election": election})


def vote(request, candidate, ballot_box, election):
    with transaction.atomic():
        tallies = ballot_box.vote_tallies or {}
        current_count = tallies.get(str(candidate.candidate_id), 0)
        tallies[str(candidate.candidate_id)] = current_count + 1
        ballot_box.vote_tallies = tallies
        ballot_box.total_votes_cast += 1
        ballot_box.save()
        messages.success(request, "Your vote has been Successfully Casted!")
        return True
    return False

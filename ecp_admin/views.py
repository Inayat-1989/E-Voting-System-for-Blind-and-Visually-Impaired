import csv
import io

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.models import Voter
from voting_app.models import BallotBox, Candidate, Constituency, Election, PollingStation

from .forms import ECPBulkUploadForm, ElectionForm

User = get_user_model()


def ecp_dashboard(request):
    return render(request, "ecp_admin/login.html")


def ecp_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        election = Election.objects.first()
        return render(request, "ecp_admin/menu.html", {"election": election})
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        ecp_admin = authenticate(request, username=username, password=password)
        if not ecp_admin:
            messages.error(request, "No ECP Admin found with that Username and Password.")
            return render(request, "ecp_admin/login.html")
        login(request, ecp_admin)
        ecp_admin.current_session_key = request.session.session_key
        ecp_admin.save()
        messages.success(request, "Welcome ECP Admin!")
        election = Election.objects.first()
        return render(request, "ecp_admin/menu.html", {"election": election})
    return render(request, "ecp_admin/login.html")


def ecp_election_creation_form(request):
    form = ElectionForm()
    return render(request, "ecp_admin/election.html", {"form": form})


def ecp_election_upload(request):
    if request.method == "POST":
        form = ElectionForm(request.POST)
        if form.is_valid():
            Election.objects.all().delete()
            Voter.objects.all().delete()
            Constituency.objects.all().delete()
            Candidate.objects.all().delete()
            PollingStation.objects.all().delete()
            BallotBox.objects.all().delete()
            form.save()
            messages.success(request, "Election was created Successfully, Upload the Files Now!")
            upload_form = ECPBulkUploadForm()
            return render(request, "ecp_admin/upload.html", {"form": upload_form})
        messages.error(request, "Form is not Valid, Please recreate Election.")
    return render(request, "ecp_admin/election.html")


# @staff_member_required(login_url="/login/")
def ecp_election_data(request):  # noqa: C901, PLR0912
    election = Election.objects.first()
    if not election:
        messages.error(request, "Error: You must configure an Election instance before uploading data files.")
        return redirect("ecp_admin/login")

    if request.method != "POST":
        form = ECPBulkUploadForm()
        return render(request, "ecp_admin/upload.html", {"form": form})

    form = ECPBulkUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Form is Invalid.")
        form = ECPBulkUploadForm()
        return render(request, "ecp_admin/upload.html", {"form": form})

    try:
        with transaction.atomic():
            # --- 1. PROCESS VOTERS ---
            voter_file = request.FILES["voters_file"]
            voter_data = csv.reader(io.StringIO(voter_file.read().decode("utf-8")))
            next(voter_data)  # Skip header

            for row in voter_data:
                Voter.objects.get_or_create(
                    cnic=row[0],
                    defaults={
                        "cnic": row[0],
                        "full_name": row[1],
                        "assigned_constituency_na": row[5],
                        "assigned_constituency_pa": row[6],
                        "is_biometrically_verified": True,
                    },
                )
                constituency_obj, _ = Constituency.objects.get_or_create(
                    constituency_id=row[5],
                    defaults={
                        "election": election,
                        "province": row[3],
                        "assembly_type": "NATIONAL",
                        "registered_voters_count": 0,
                    },
                )
                constituency_obj, _ = Constituency.objects.get_or_create(
                    constituency_id=row[6],
                    defaults={
                        "election": election,
                        "province": row[3],
                        "assembly_type": "PROVINCIAL",
                        "registered_voters_count": 0,
                    },
                )

            all_constituencies = Constituency.objects.all()

            for constituency in all_constituencies:
                if constituency.assembly_type == "NATIONAL":
                    registered_voters_count = Voter.objects.filter(
                        assigned_constituency_na=constituency.constituency_id
                    ).count()
                elif constituency.assembly_type == "PROVINCIAL":
                    registered_voters_count = Voter.objects.filter(
                        assigned_constituency_pa=constituency.constituency_id
                    ).count()
                constituency.registered_voters_count = registered_voters_count
                constituency.save()

            # --- 2. PROCESS CANDIDATES & AUTO-CREATE CONSTITUENCIES ---
            candidate_file = request.FILES["candidates_file"]
            candidate_data = csv.reader(io.StringIO(candidate_file.read().decode("utf-8")))
            next(candidate_data)  # Skip header

            for row in candidate_data:
                constituency_obj = Constituency.objects.get(constituency_id=row[6])
                if constituency_obj:
                    Candidate.objects.get_or_create(
                        candidate_id=f"CAND-{row[0]}",
                        assembly_type=row[5],
                        defaults={
                            "election": election,
                            "candidate_id": f"CAND-{row[0]}",
                            "name": row[1],
                            "political_party": row[2],
                            "constituency": constituency_obj,
                            "assembly_type": row[5],
                        },
                    )

            # --- 3. PROCESS POLLING STATIONS & AUTO-CREATE BALLOT BOXES ---
            station_file = request.FILES["polling_stations_file"]
            station_data = csv.reader(io.StringIO(station_file.read().decode("utf-8")))
            next(station_data)  # Skip header

            for row in station_data:
                constituency_na = Constituency.objects.get(constituency_id=row[3])
                constituency_pa = Constituency.objects.get(constituency_id=row[4])
                polling_station, _ = PollingStation.objects.get_or_create(
                    station_id=f"PS-{row[3]}-{row[4]}",
                    defaults={
                        "election": election,
                        "station_id": f"PS-{row[3]}-{row[4]}",
                        "location_name": row[0],
                        "constituency_na": row[3],
                        "constituency_pa": row[4],
                    },
                )

                # Create NA Ballot Box
                if constituency_na:
                    BallotBox.objects.get_or_create(
                        ballot_box_id=f"BOX-{polling_station.station_id}-NA",
                        defaults={
                            "election": election,
                            "ballot_box_id": f"BOX-{polling_station.station_id}-NA",
                            "constituency": constituency_na,
                            "assembly_type": "NATIONAL",
                            "vote_tallies": {},
                            "total_votes_cast": 0,
                        },
                    )

                # Create PA Ballot Box
                if constituency_pa:
                    BallotBox.objects.get_or_create(
                        ballot_box_id=f"BOX-{polling_station.station_id}-PA",
                        defaults={
                            "election": election,
                            "ballot_box_id": f"BOX-{polling_station.station_id}-PA",
                            "constituency": constituency_pa,
                            "assembly_type": "PROVINCIAL",
                            "vote_tallies": {},
                            "total_votes_cast": 0,
                        },
                    )
        messages.success(request, "All systems integrated successfully! Database updated.")
        return redirect("../login/")
    except Exception as e:  # noqa: BLE001
        messages.error(request, f"Database insertion aborted! Formatting or index error detected: {e}")
    return redirect("ecp_admin/login")


def ecp_logout(request):
    if request.user.is_authenticated:
        request.user.current_session_key = None
        request.user.save()
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("ecp_login")

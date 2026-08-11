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
            election = form.save()
    return redirect("ecp_upload_csv_step2", election_id=election.pk)


# @staff_member_required(login_url="/login/")
def ecp_election_creation(request):
    if request.method == "POST":
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save()
            return redirect("ecp_admin/election.html", {"form": form})
        election = Election.objects.get_or_create(
            title=request.POST.get("title", "General Elections Pakistan"),
            election_type=request.POST.get("election_type", "NATIONAL"),
            start_time=request.POST.get("start_time"),
            end_time=request.POST.get("end_time"),
        )
    return render(request, "ecp_admin/admin_panel_upload.html", {"election": election})


# @staff_member_required(login_url="/login/")
def ecp_upload_data(request):
    election = Election.objects.first()
    if request.method == "POST":
        form = ECPBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # --- 1. PROCESS POLLING STATIONS & AUTO-CREATE BALLOT BOXES ---
                    station_file = request.FILES["polling_stations_file"]
                    # Decode byte stream to text for CSV parser
                    station_data = csv.reader(io.StringIO(station_file.read().decode("utf-8")))
                    next(station_data)  # Skip header row ['name', 'constituency_code', 'election_id']

                    for row in station_data:
                        polling_station = PollingStation.objects.create(
                            election=election,
                            station_id=f"PS-{row[0]}",
                            location_name=row[1],
                            constituency_na=row[2],
                            constituency_pa=row[3],
                        )
                        # Automate Dependent Model Insertion: Create the 2 required ballot boxes
                        BallotBox.objects.create(
                            election=election,
                            ballot_box_id=f"BOX-{polling_station.station_id}-NA",
                            constituency=row[0][0:2],
                            assembly_type="NATIONAL",
                            vote_tallies={},
                            total_votes_cast=0,
                        )
                        BallotBox.objects.create(
                            election=election,
                            ballot_box_id=f"BOX-{polling_station.station_id}-PA",
                            constituency=row[0][3:],
                            assembly_type="PROVINCIAL",
                            vote_tallies={},
                            total_votes_cast=0,
                        )

                    # --- 2. PROCESS CANDIDATES & AUTO-CREATE CONSTITUENCIES ---
                    candidate_file = request.FILES["candidates_file"]
                    candidate_data = csv.reader(io.StringIO(candidate_file.read().decode("utf-8")))
                    next(
                        candidate_data
                    )  # Skip header row ['name', 'party', 'constituency_code', 'election_id', 'assembly']

                    for row in candidate_data:
                        # Auto-create the constituency object if it does not exist yet
                        constituency_obj, _ = Constituency.objects.get_or_create(
                            constituency_id=row[5],
                            default={
                                "election": election,
                                "constituency_id": row[5],
                                "province": row[3],
                                "assembly_type": row[4],
                                "registered_voters_count": 0,
                            },
                        )
                        Candidate.objects.create(
                            election=election,
                            candidate_id=f"CAND-{row[0]}",
                            name=row[1],
                            political_party=row[2],
                            constituency=constituency_obj,
                            assembly_type=row[4],
                        )

                    # --- 3. PROCESS VOTERS ---
                    voter_file = request.FILES["voters_file"]
                    voter_data = csv.reader(io.StringIO(voter_file.read().decode("utf-8")))
                    next(
                        voter_data
                    )  # Skip header row ['cnic', 'name', 'assigned_constituency_na', 'assigned_constituency_pa']

                    for row in voter_data:
                        Voter.objects.create(
                            cnic=row[0],
                            full_name=row[1],
                            assigned_constituency_na=row[2],
                            assigned_constituency_pa=row[3],
                            is_biometrically_verified=True,
                        )

                messages.success(request, "All systems integrated successfully! Database updated.")
                return render(request, "ecp_admin/admin_panel_menu.html")

            except Exception as e:  # noqa: BLE001
                messages.error(request, f"Database insertion aborted! Formatting error detected: {e}")
    else:
        form = ECPBulkUploadForm()

    return render(request, "ecp_admin/upload.html", {"form": form})


def ecp_logout(request):
    if request.user.is_authenticated:
        request.user.current_session_key = None
        request.user.save()
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("ecp_login")

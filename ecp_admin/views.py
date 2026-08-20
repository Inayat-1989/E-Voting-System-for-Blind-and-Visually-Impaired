import csv
import io

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.shortcuts import redirect, render

from accounts.models import Voter
from voting_app.models import BallotBox, Candidate, Constituency, ConstituencyMapping, Election, PollingStation

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
            ConstituencyMapping.objects.all().delete()
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
def ecp_election_data(request):  # noqa: C901
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
                if row[2] != "Active" or row[3] != "Yes":
                    continue
                Voter.objects.get_or_create(
                    cnic=row[0],
                    defaults={
                        "cnic": row[0],
                        "full_name": row[1],
                        "province": row[4],
                        "city": row[5],
                        "block_code": row[6],
                        "serial_number": row[7],
                        "is_biometrically_verified": True,
                    },
                )

            # --- 2. PROCESS Constituency Mapping and Constituency Creation ---
            constituency_mapping_file = request.FILES["constituency_mappings_file"]
            constituency_mapping_data = csv.reader(io.StringIO(constituency_mapping_file.read().decode("utf-8")))
            next(constituency_mapping_data)
            for row in constituency_mapping_data:
                ConstituencyMapping.objects.get_or_create(
                    block_code=row[0],
                    defaults={
                        "block_code": row[0],
                        "constituency_na": row[1],
                        "constituency_pa": row[2],
                    },
                )

            total_constituencies_mapping = ConstituencyMapping.objects.all()
            block_code_list = []
            for constituency_mapping in total_constituencies_mapping:
                voter = Voter.objects.filter(block_code=constituency_mapping.block_code)
                if not voter.exists():
                    continue
                registered_voters_count_for_pa = voter.count()
                province, city = voter.values_list("province", "city").first()
                constituency_pa_obj, _created = Constituency.objects.get_or_create(
                    constituency_id=constituency_mapping.constituency_pa,
                    defaults={
                        "election": election,
                        "constituency_id": constituency_mapping.constituency_pa,
                        "province": province,
                        "city": city,
                        "assembly_type": "PROVINCIAL",
                        "registered_voters_count": registered_voters_count_for_pa,
                    },
                )
                if constituency_mapping.block_code in block_code_list:
                    continue
                block_code_list = ConstituencyMapping.objects.filter(
                    constituency_na=constituency_mapping.constituency_na
                ).values_list("block_code", flat=True)
                registered_voters_count_for_na = Voter.objects.filter(block_code__in=block_code_list).count()
                constituency_na_obj, _created = Constituency.objects.get_or_create(
                    constituency_id=constituency_mapping.constituency_na,
                    defaults={
                        "election": election,
                        "constituency_id": constituency_mapping.constituency_na,
                        "province": province,
                        "city": city,
                        "assembly_type": "NATIONAL",
                        "registered_voters_count": registered_voters_count_for_na,
                    },
                )

            # --- 2. PROCESS CANDIDATES ---
            candidate_file = request.FILES["candidates_file"]
            candidate_data = csv.reader(io.StringIO(candidate_file.read().decode("utf-8")))
            next(candidate_data)  # Skip header

            for row in candidate_data:
                try:
                    constituency_obj = Constituency.objects.get(constituency_id=row[6])
                except Constituency.DoesNotExist:
                    continue
                Candidate.objects.get_or_create(
                    candidate_id=row[0],
                    assembly_type=row[5],
                    defaults={
                        "election": election,
                        "candidate_id": row[0],
                        "name": row[1],
                        "political_party": row[2],
                        "province": row[3],
                        "city": row[4],
                        "assembly_type": row[5],
                        "constituency": constituency_obj,
                    },
                )

            # --- 3. PROCESS POLLING STATIONS & AUTO-CREATE BALLOT BOXES ---
            station_file = request.FILES["polling_stations_file"]
            station_data = csv.reader(io.StringIO(station_file.read().decode("utf-8")))
            next(station_data)  # Skip header

            for row in station_data:
                constituency_mapping = ConstituencyMapping.objects.get(block_code=row[3])
                constituency_na = constituency_mapping.constituency_na
                constituency_pa = constituency_mapping.constituency_pa
                try:
                    constituency_pa_obj = Constituency.objects.get(constituency_id=constituency_pa)
                except Constituency.DoesNotExist:
                    continue
                try:
                    constituency_na_obj = Constituency.objects.get(constituency_id=constituency_na)
                except Constituency.DoesNotExist:
                    continue
                polling_station, _ = PollingStation.objects.get_or_create(
                    station_id=f"PS-{constituency_na}-{constituency_pa}",
                    defaults={
                        "election": election,
                        "station_id": f"PS-{constituency_na}-{constituency_pa}",
                        "location_name": row[0],
                        "province": row[1],
                        "city": row[2],
                        "block_code": row[3],
                        "serial_number_start_from": row[4],
                        "serial_number_end_at": row[5],
                        "constituency_na": row[6],
                        "constituency_pa": row[7],
                    },
                )

                # Create NA Ballot Box
                BallotBox.objects.get_or_create(
                    ballot_box_id=f"BOX-{polling_station.station_id}-NA",
                    defaults={
                        "election": election,
                        "ballot_box_id": f"BOX-{polling_station.station_id}-NA",
                        "assembly_type": "NATIONAL",
                        "constituency": constituency_na_obj,
                        "vote_tallies": {},
                        "total_votes_cast": 0,
                    },
                )

                # Create PA Ballot Box
                BallotBox.objects.get_or_create(
                    ballot_box_id=f"BOX-{polling_station.station_id}-PA",
                    defaults={
                        "election": election,
                        "ballot_box_id": f"BOX-{polling_station.station_id}-PA",
                        "assembly_type": "PROVINCIAL",
                        "constituency": constituency_pa_obj,
                        "vote_tallies": {},
                        "total_votes_cast": 0,
                    },
                )
        messages.success(request, "All systems integrated successfully! Database updated.")
        return redirect("../login/")
    except Exception as e:  # noqa: BLE001
        messages.error(request, f"Database insertion aborted! Formatting or index error detected: {e}")
    return redirect("../login/")


def ecp_logout(request):
    if request.user.is_authenticated:
        request.user.current_session_key = None
        request.user.save()
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("ecp_login")

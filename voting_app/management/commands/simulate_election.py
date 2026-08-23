import random

from django.core.management.base import BaseCommand
from django.test import Client

from accounts.models import Voter
from voting_app.models import BallotBox, Candidate, ConstituencyMapping, Election, PollingStation


class Command(BaseCommand):
    help = "Simulates an election, maps voters to polling stations via block codes, and updates database ballot boxes."

    def handle(self, *args, **options):
        self.stdout.write("Starting Election Simulation and Database Update...")

        election = Election.load()
        self.stdout.write(f"Target Election: {election.title}")

        voters = Voter.objects.all()
        if not voters.exists():
            self.stdout.write(self.style.ERROR("No voters found in the database. Please add voters first."))
            return
        client = Client()

        for voter in voters:
            self.stdout.write(f"\n--- Simulating session for Voter CNIC: {voter.cnic} (Block: {voter.block_code}) ---")

            if voter.has_voted_na and voter.has_voted_pa:
                self.stdout.write(
                    self.style.WARNING(f"Has Already Voted for both Assemblies {voter.full_name}. Skipping votes.")
                )
                client.get("/logout/")
                continue
            # 1. Voter Sign-in
            login_response = client.post("/", {"cnic": voter.cnic})
            if login_response.status_code not in [200, 302]:
                self.stdout.write(self.style.WARNING(f"Login failed for voter {voter.cnic}"))
                continue
            self.stdout.write("Voter successfully logged in.")

            # 2. Visit Elections view
            client.get("/elections/")

            # Find the polling station matching the voter's block code
            polling_station = PollingStation.objects.filter(block_code=voter.block_code).first()
            if not polling_station:
                self.stdout.write(
                    self.style.WARNING(f"No polling station found for block code {voter.block_code}. Skipping votes.")
                )
                client.get("/logout/")
                continue

            assemblies = ["NATIONAL", "PROVINCIAL"]
            if voter.has_voted_na:
                assemblies.remove("NATIONAL")
            if voter.has_voted_pa:
                assemblies.remove("PROVINCIAL")

            for assembly in assemblies:
                if assembly == "NATIONAL":
                    constituency_id = ConstituencyMapping.objects.get(block_code=voter.block_code).constituency_na
                else:
                    constituency_id = ConstituencyMapping.objects.get(block_code=voter.block_code).constituency_pa
                candidates = Candidate.objects.filter(constituency_id=constituency_id, assembly_type=assembly)

                if not candidates.exists():
                    self.stdout.write(self.style.WARNING(f"No candidates found for assembly: {assembly}"))
                    continue

                # Select a random candidate
                selected_candidate = random.choice(candidates)
                constituency = selected_candidate.constituency
                self.stdout.write(
                    f"Voted for: {selected_candidate.name} ({selected_candidate.political_party}) in {assembly}"
                )

                # 3. Submit Vote via Test Client
                vote_payload = {
                    "candidate_id": selected_candidate.candidate_id,
                    "assembly_type": assembly,
                    "constituency_id": constituency.constituency_id,
                }
                vote_response = client.post("/elections/vote/", vote_payload)

                if vote_response.status_code in [200, 302]:
                    # --- DYNAMIC BALLOT BOX SELECTION LOGIC ---
                    if assembly == "NATIONAL":
                        # Multiple NA ballot boxes tied to the specific polling station ID suffix
                        box_id = f"BOX-{polling_station.station_id}-NA"
                        voter.has_voted_na = True
                    else:
                        # Single PA ballot box per constituency/station mapping
                        box_id = f"BOX-{polling_station.station_id}-PA"
                        voter.has_voted_pa = True

                    ballot_box = BallotBox.objects.get(ballot_box_id=box_id)

                    # Initialize vote_tallies if null/empty
                    # if not ballot_box.vote_tallies:
                    #     ballot_box.vote_tallies = {}

                    # Increment candidate vote count inside JSON field
                    cand_id_str = str(selected_candidate.candidate_id)
                    current_count = ballot_box.vote_tallies.get(cand_id_str, 0)
                    ballot_box.vote_tallies[cand_id_str] = current_count + 1

                    # Increment total votes cast
                    ballot_box.total_votes_cast = ballot_box.total_votes_cast + 1
                    voter.save()
                    ballot_box.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"Database updated: BallotBox {ballot_box.ballot_box_id} tally incremented.")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to cast vote for {assembly}. Status: {vote_response.status_code}")
                    )

            # 4. Logout Voter
            logout_response = client.get("/logout/")
            if logout_response.status_code in [200, 302]:
                self.stdout.write("Voter successfully logged out.")
            else:
                self.stdout.write(self.style.WARNING("Logout encountered an issue."))

        self.stdout.write(self.style.SUCCESS("\nElection simulation and database updates completed successfully!"))

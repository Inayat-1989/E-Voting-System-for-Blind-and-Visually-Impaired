from django.test import TestCase
from django.urls import reverse

from voting_app.models import Candidate, Election, Voter


class VotingStoriesTests(TestCase):
    def setUp(self):
        self.election = Election.objects.create(title="Student Council", description="Choose the next representative")
        self.candidate = Candidate.objects.create(election=self.election, name="Ayesha")

    def test_registration_records_cnic_and_disabled_status(self):
        response = self.client.post(
            reverse("register"),
            {"full_name": "Ali Khan", "cnic": "3520212345678", "is_disabled": "on"},
        )
        self.assertEqual(response.status_code, 302)
        voter = Voter.objects.get(cnic="3520212345678")
        self.assertTrue(voter.is_disabled)
        self.assertEqual(voter.full_name, "Ali Khan")

    def test_login_requires_correct_otp(self):
        voter = Voter.objects.create(full_name="Sara", cnic="3520298765432", is_disabled=True)
        voter.generate_otp()
        voter.save()

        response = self.client.post(reverse("login"), {"cnic": voter.cnic, "otp": voter.otp_code})
        self.assertEqual(response.status_code, 302)
        self.assertIn("voter_id", self.client.session)

        response = self.client.post(reverse("login"), {"cnic": voter.cnic, "otp": "000000"})
        self.assertContains(response, "Invalid OTP")

    def test_voting_is_blocked_for_non_disabled_voter(self):
        voter = Voter.objects.create(full_name="Nadia", cnic="3520211111111", is_disabled=False)
        self.client.session["voter_id"] = voter.id
        self.client.session.save()

        response = self.client.post(
            reverse("vote", args=[self.election.id]),
            {"candidate_id": self.candidate.id},
        )
        self.assertContains(response, "Only disabled voters")

    def test_voting_allows_disabled_voter(self):
        voter = Voter.objects.create(full_name="Hassan", cnic="3520212222222", is_disabled=True)
        self.client.session["voter_id"] = voter.id
        self.client.session.save()

        response = self.client.post(
            reverse("vote", args=[self.election.id]),
            {"candidate_id": self.candidate.id},
        )
        self.assertContains(response, "Your vote was recorded")

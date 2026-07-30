import uuid

from django.db import models


class Voter(models.Model):
    full_name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=13, unique=True)
    # email = models.EmailField(unique=True)
    is_disabled = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)

    def generate_verification_token(self):
        self.verification_token = uuid.uuid4().hex
        return self.verification_token

    def __str__(self):
        return self.full_name


class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name="votes")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="votes")

    class Meta:
        unique_together = ("election", "voter")

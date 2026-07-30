from django.db import models
from accounts.models import User


class Voter(User):
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

    def __repr__(self):
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

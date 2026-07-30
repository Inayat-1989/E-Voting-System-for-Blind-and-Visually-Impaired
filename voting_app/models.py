from django.db import models
from accounts.models import User
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta

class Voter(User):
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return self.full_name

class Election(models.Model):
    ELECTION_TYPES = [
        ('NATIONAL', 'National Assembly'),
        ('PROVINCIAL', 'Provincial Assembly'),
    ]
    title = models.CharField(max_length=200, default="National")
    election_type = models.CharField(max_length=15, choices=ELECTION_TYPES, default="National")
    default_time = timezone.make_aware(datetime.datetime(2028, 2, 10, 6, 0 ,0))
    start_time = models.DateTimeField(default=default_time)
    end_time = models.DateTimeField(default=default_time + relativedelta(years=5))

    def __str__(self):
        return f"{self.title} ({self.get_election_type_display()})"

    @property
    def is_active(self):
        """Checks if the current time falls within the election window."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def has_ended(self):
        """Checks if the voting window has closed."""
        return timezone.now() > self.end_time

    def clean(self):
        """Validates that the end date is after the start date."""
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be later than the start time.")

# class National(Election):
#     title = "National Election"

# class Provincial(Election):
#     title = "Provincial Election"

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

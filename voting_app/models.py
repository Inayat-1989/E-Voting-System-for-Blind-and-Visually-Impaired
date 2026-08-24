from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def get_default_start_time():
    return timezone.now()


def get_default_end_time():
    return get_default_start_time() + relativedelta(years=5)


# --- MODELS ---
class Election(models.Model):
    """Admin-managed configuration for scheduling simultaneous elections.

    Controls time windows and structural configurations without touching voter
    identities.
    """

    title = models.CharField(max_length=255, default="General Elections Pakistan")
    is_na = models.BooleanField(default=True)
    is_pa = models.BooleanField(default=True)
    start_time = models.DateTimeField(default=timezone.now, editable=True)
    end_time = models.DateTimeField(default=get_default_end_time)

    def __str__(self):
        active_types = []
        if self.is_na:
            active_types.append("National")
        if self.is_pa:
            active_types.append("Provincial")
        types_str = " & ".join(active_types) if active_types else "None"
        return f"{self.title} ({types_str})"

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
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be later than the start time.")

    def save(self, *args, **kwargs):
        self.pk = 1
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):  # noqa: ANN206
        obj, _created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "title": "Default Election",
                "start_time": timezone.now(),
                "end_time": timezone.now(),
            },
        )
        return obj

    def fetch_election_infrastructure(self):
        """Fetches non-sensitive operational infrastructure required for voting:

        constituencies, candidates, ballot boxes, and polling stations.
        EXCLUDES voter identity data to preserve privacy.
        """
        return {
            "election": self,
            "constituencies": Constituency.objects.filter(election=self),
            "candidates": Candidate.objects.filter(election=self),
            "ballot_boxes": BallotBox.objects.filter(election=self),
            "polling_stations": PollingStation.objects.filter(election=self),
        }


class ConstituencyMapping(models.Model):
    block_code = models.CharField(max_length=255, primary_key=True)
    constituency_na = models.CharField(max_length=255, default="NA-00")
    constituency_pa = models.CharField(max_length=255, default="PA-00")

    class Meta:
        db_table = "constituency_mapping"

    def __str__(self):
        return f"Block Code: {self.block_code} - {self.constituency_na} - {self.constituency_pa}"


class Constituency(models.Model):
    """Represent a defined electoral geographical territory (Halqa)."""

    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="constituencies")
    constituency_id = models.CharField(max_length=20, primary_key=True, default="NA-00")
    province = models.CharField(max_length=255, default="Punjab")
    city = models.CharField(max_length=255, default="Lahore")
    assembly_type = models.CharField(max_length=255, default="NATIONAL")
    registered_voters_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.constituency_id} ({self.assembly_type})"


class Candidate(models.Model):
    """Represents a politician contesting a specific assembly seat."""

    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    candidate_id = models.CharField(max_length=50, default="CAND-000")
    name = models.CharField(max_length=255, default="")
    political_party = models.CharField(max_length=100, default="Independent")
    assigned_symbol = models.ImageField(upload_to="election_symbols/", blank=True, null=True)
    province = models.CharField(max_length=255, default="Punjab")
    city = models.CharField(max_length=255, default="Lahore")
    assembly_type = models.CharField(max_length=255, default="NATIONAL")
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name="candidates")

    def __str__(self):
        return f"{self.name} ({self.political_party}) - {self.constituency.constituency_id}"


class PollingStation(models.Model):
    """Represents the physical or localized digital node where votes are cast."""

    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="polling_stations")
    station_id = models.CharField(max_length=50, primary_key=True, default="STATION-000")
    location_name = models.CharField(max_length=255, default="Government Building")
    province = models.CharField(max_length=255, default="Punjab")
    city = models.CharField(max_length=255, default="Lahore")
    block_code = models.CharField(max_length=255, default="0")
    serial_number_start_from = models.IntegerField(default=1)
    serial_number_end_at = models.IntegerField(default=999)

    def __str__(self):
        return f"Station {self.station_id} - {self.location_name}"


class BallotBox(models.Model):
    """Secure anonymous tally counter decoupled from Voter records."""

    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="ballot_boxes")
    ballot_box_id = models.CharField(max_length=50, primary_key=True, default="BOX-000")
    assembly_type = models.CharField(max_length=255, default="NATIONAL")
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name="ballot_boxes")
    vote_tallies = models.JSONField(
        default=dict,
        help_text="Stores key-value pairs of candidateId and their respective vote counts.",
        null=True,
        blank=True,
    )
    total_votes_cast = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"BallotBox {self.ballot_box_id} for {self.constituency.constituency_id}"

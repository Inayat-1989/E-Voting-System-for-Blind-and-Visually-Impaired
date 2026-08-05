from django.db import models


class Voter(models.Model):
    cnic = models.CharField(max_length=13, unique=True, default="")
    full_name = models.CharField(max_length=255, default="")
    assigned_constituency_na = models.CharField(max_length=20, default="NA-00")
    assigned_constituency_pa = models.CharField(max_length=20, default="PA-00")
    has_voted_na = models.BooleanField(default=False)
    has_voted_pa = models.BooleanField(default=False)
    is_biometrically_verified = models.BooleanField(default=False)
    current_session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.cnic}"

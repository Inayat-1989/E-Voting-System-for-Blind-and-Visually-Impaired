from django.db import models


class Voter(models.Model):
    cnic = models.CharField(max_length=13, unique=True, default="") #0
    full_name = models.CharField(max_length=255, default="") #1
    status = models.CharField(max_length=255, default="Active") #2
    disabled = models.CharField(max_length=255, default="Yes") #3
    block_code = models.IntegerField(default=0) #6
    serial_number = models.IntegerField(default=0) #7

    # father_or_husband_name = models.CharField(max_length=255, default="")
    # mother_name = models.CharField(max_length=255, default="")
    # address = models.CharField(max_length=255, default="")
    # province = models.CharField(max_length=50, default="")
    # city = models.CharField(max_length=50, default="")

    has_voted_na = models.BooleanField(default=False)
    has_voted_pa = models.BooleanField(default=False)
    is_biometrically_verified = models.BooleanField(default=False)
    current_session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.cnic}"

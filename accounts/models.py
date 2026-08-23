from django.db import models


class Voter(models.Model):
    cnic = models.CharField(max_length=13, unique=True, default="")  # 0
    full_name = models.CharField(max_length=255, default="")  # 1
    province = models.CharField(max_length=50, default="Punjab")  # 4
    city = models.CharField(max_length=50, default="Lahore")  # 5
    block_code = models.CharField(max_length=255, default="0")  # 6
    serial_number = models.IntegerField(default=0)  # 7

    has_voted_na = models.BooleanField(default=False)
    has_voted_pa = models.BooleanField(default=False)
    is_biometrically_verified = models.BooleanField(default=False)
    current_session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.cnic} - {self.full_name}"

    @property
    def serial_range(self):
        """Returns a tuple of (start, end) based on groups of 20"""
        if self.serial_number < 1:
            return (0, 0)  # Handles edge cases safely

        # Calculate the start of the 20-voter block
        start = ((self.serial_number - 1) // 20) * 20 + 1
        end = start + 19

        return start, end

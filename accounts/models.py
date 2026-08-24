from django.db import models


class Voter(models.Model):
    cnic = models.CharField(max_length=13, unique=True, default="")
    full_name = models.CharField(max_length=255, default="")
    province = models.CharField(max_length=50, default="Punjab")
    city = models.CharField(max_length=50, default="Lahore")
    block_code = models.CharField(max_length=255, default="0")
    serial_number = models.IntegerField(default=0)

    has_voted_na = models.BooleanField(default=False)
    has_voted_pa = models.BooleanField(default=False)

    current_session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.cnic} - {self.full_name}"

    @property
    def serial_range(self):
        """Returns a tuple of (start, end) for a 100-voter block based on serial_number."""
        if self.serial_number < 1 or self.serial_number > 500:  # noqa: PLR2004
            return (0, 0)

        # Calculate start (1, 101, 201, 301, or 401) and end of the 100-voter block
        start = ((self.serial_number - 1) // 100) * 100 + 1
        end = start + 99

        return start, end

import uuid
from django.db import models

class User(models.Model):
    cnic = models.CharField(max_length=13, unique=True)
    is_disabled = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)

    def generate_verification_token(self):
            self.verification_token = uuid.uuid4().hex
            return self.verification_token

    def __str__(self):
            return self.cnic

    def __repr__(self):
           return self.cnic
    

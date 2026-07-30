import uuid
from django.db import models

class User(models.Model):
    cnic = models.CharField(max_length=13, unique=True)
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
            return self.cnic

    def __repr__(self):
           return self.cnic
    

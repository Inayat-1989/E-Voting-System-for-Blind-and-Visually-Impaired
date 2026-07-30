# your_app/admin.py
from django.contrib import admin
from .models import Voter, Election, Candidate

admin.site.register(Voter)
admin.site.register(Election)
admin.site.register(Candidate)


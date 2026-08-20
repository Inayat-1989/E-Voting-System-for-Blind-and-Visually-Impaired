from django.contrib import admin

from .models import Voter


# Register your models here.
@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ("cnic", "full_name", "block_code", "serial_number")

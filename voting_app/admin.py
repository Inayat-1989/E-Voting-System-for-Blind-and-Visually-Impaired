# your_app/admin.py
from django.contrib import admin
from .models import Voter, Election, Candidate
admin.site.register(Voter)
admin.site.register(Candidate)

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'election_type', 'start_time', 'end_time', 'is_open')
    list_filter = ('election_type', 'start_time', 'end_time')
    search_fields = ('title',)

    @admin.display(boolean=True, description='Currently Open')
    def is_open(self, obj):
        return obj.is_active
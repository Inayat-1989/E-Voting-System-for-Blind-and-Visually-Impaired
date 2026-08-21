from django.contrib import admin

from .models import BallotBox, Candidate, Constituency, Election, PollingStation

admin.site.register(Candidate)
admin.site.register(BallotBox)
admin.site.register(Constituency)
admin.site.register(PollingStation)


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    """Admin interface for the Election model."""

    list_display = ("title", "election_type", "start_time", "end_time", "is_open")
    list_filter = ("election_type", "start_time", "end_time")
    search_fields = ("title",)

    @admin.display(boolean=True, description="Currently Open")
    def is_open(self, obj):
        return obj.is_active

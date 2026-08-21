from django import forms
from django.utils import timezone

from voting_app.models import Election


class ECPBulkUploadForm(forms.Form):
    polling_stations_file = forms.FileField(
        label="Polling Stations CSV", widget=forms.FileInput(attrs={"accept": ".csv"})
    )
    candidates_file = forms.FileField(label="Candidates List CSV", widget=forms.FileInput(attrs={"accept": ".csv"}))
    voters_file = forms.FileField(label="Voters List CSV", widget=forms.FileInput(attrs={"accept": ".csv"}))


class ElectionForm(forms.ModelForm):
    election_type = forms.MultipleChoiceField(
        choices=[
            ("NATIONAL", "National Assembly"),
            ("PROVINCIAL", "Provincial Assembly"),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Election
        fields = ["title", "start_time", "end_time"]

        # Adding clear labels and visual placeholders/widgets
        labels = {
            "title": "Election Title",
            "start_time": "Voting Start Time",
            "end_time": "Voting End Time",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., General Elections Pakistan"}
            ),
            "start_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",  # Enables native browser calendar/time picker
                }
            ),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)
        self.fields["title"].initial = None
        local_now = timezone.localtime(timezone.now())
        self.fields["start_time"].initial = local_now
        self.fields["end_time"].initial = local_now + timezone.timedelta(days=1)

        # Explicitly restore initial checkbox state if it's a new form
        if self.instance and self.instance.pk:
            initial_checks = []
            if self.instance.is_NA:
                initial_checks.append("NATIONAL")
            if self.instance.is_PA:
                initial_checks.append("PROVINCIAL")
            self.fields["election_type"].initial = initial_checks
        elif not self.is_bound:
            self.fields["election_type"].initial = ["NATIONAL", "PROVINCIAL"]

    def clean(self):
        """Cross-field validation hook.

        This mimics your model's clean method to catch the date mismatch
        before it hits the database save process.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            # Attaches the specific error text directly underneath the end_time field
            self.add_error("end_time", "End time must be later than the start time.")

        return cleaned_data

    def save(self, commit=True):
        # Generate instance object without executing immediate SQL write operations
        instance = super().save(commit=False)

        # Parse user checkbox list entries
        selected_types = self.cleaned_data.get("election_type", [])

        # Explicitly map checked lists back to individual database Boolean values
        instance.is_NA = "NATIONAL" in selected_types
        instance.is_PA = "PROVINCIAL" in selected_types

        if commit:
            instance.save()
        return instance

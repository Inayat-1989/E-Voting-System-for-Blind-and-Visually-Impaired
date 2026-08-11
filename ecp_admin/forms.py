# ecp_admin/forms.py
from django import forms

from voting_app.models import Election


class ECPBulkUploadForm(forms.Form):
    polling_stations_file = forms.FileField(
        label="Polling Stations CSV", widget=forms.FileInput(attrs={"accept": ".csv"})
    )
    candidates_file = forms.FileField(label="Candidates List CSV", widget=forms.FileInput(attrs={"accept": ".csv"}))
    voters_file = forms.FileField(label="Voters List CSV", widget=forms.FileInput(attrs={"accept": ".csv"}))


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ["title", "election_type", "start_time", "end_time"]

        # Adding clear labels and visual placeholders/widgets
        labels = {
            "title": "Election Title",
            "election_type": "Assembly Type",
            "start_time": "Voting Start Time",
            "end_time": "Voting End Time",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., General Elections Pakistan"}
            ),
            "election_type": forms.Select(attrs={"class": "form-select"}),
            "start_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",  # Enables native browser calendar/time picker
                }
            ),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

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

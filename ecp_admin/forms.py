# ecp_admin/forms.py
from django import forms


class ECPBulkUploadForm(forms.Form):
    polling_stations_file = forms.FileField(
        label="Polling Stations CSV", widget=forms.FileInput(attrs={"accept": ".csv"})
    )
    candidates_file = forms.FileField(label="Candidates List CSV", widget=forms.FileInput(attrs={"accept": ".csv"}))
    voters_file = forms.FileField(label="Voters List CSV", widget=forms.FileInput(attrs={"accept": ".csv"}))

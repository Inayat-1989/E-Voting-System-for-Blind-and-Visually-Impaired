from django.urls import path

from . import views

urlpatterns = [
    path("", views.ecp_login, name="ecp_login"),
    path("dashboard/", views.ecp_dashboard, name="ecp_dashboard"),
    path("election-creation/", views.election_creation, name="election_creation"),
    # path("upload-election-data/", views.upload_election_data, name="upload_election_data"),
]

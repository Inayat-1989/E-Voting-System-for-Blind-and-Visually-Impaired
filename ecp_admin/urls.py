from django.urls import path

from . import views

urlpatterns = [
    path("", views.ecp_dashboard, name="ecp_dashboard"),
    path("login/", views.ecp_login, name="ecp_login"),
    path("election/", views.ecp_election_creation_form, name="ecp_election_creation_form"),
    path("upload/", views.ecp_election_upload, name="ecp_election_upload"),
    path("data-processing/", views.ecp_election_data, name="ecp_election_data"),
    path("report/", views.ecp_report, name="ecp_report"),
    path("logout/", views.ecp_logout, name="ecp_logout"),
    path("na_constituencies/", views.ecp_na_constituencies, name="ecp_na_constituencies"),
    path("pa_constituencies/", views.ecp_pa_constituencies, name="ecp_pa_constituencies"),
    path("na_candidate/<str:constituency_id>", views.ecp_na_candidates, name="ecp_na_candidate"),
    path("pa_candidate/<str:constituency_id>", views.ecp_pa_candidates, name="ecp_pa_candidate"),
]

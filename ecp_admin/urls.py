from django.urls import path

from . import views

urlpatterns = [
    path("", views.ecp_dashboard, name="ecp_dashboard"),
    path("login/", views.ecp_login, name="ecp_login"),
    path("form/", views.ecp_election_creation_form, name="ecp_election_creation_form"),
    path("upload/", views.ecp_election_upload, name="ecp_election_upload"),
    path("election/", views.ecp_election_creation, name="ecp_election_creation"),
    path("logout/", views.ecp_logout, name="ecp_logout"),
]

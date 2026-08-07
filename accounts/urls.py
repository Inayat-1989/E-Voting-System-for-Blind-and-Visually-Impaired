from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.login_voter, name="login"),
    path("logout/", views.logout_voter, name="logout"),
    path("api/process-speech/", views.process_speech, name="process_speech"),
    path("elections/", include("voting_app.urls")),
]

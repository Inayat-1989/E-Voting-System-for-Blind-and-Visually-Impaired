from django.urls import path

from . import views

urlpatterns = [
    path("elections/", views.elections_list, name="elections"),
    path("vote/<int:election_id>/", views.vote, name="vote"),
]

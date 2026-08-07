from django.urls import path

from . import views

urlpatterns = [
    path("", views.elections_list, name="elections"),
    path("assembly/<str:title>/", views.assembly_types, name="assembly_types"),
    path(
        "candidates/<str:title>/<str:assembly>/",
        views.show_candidates,
        name="candidates",
    ),
    path("vote/", views.vote_view, name="vote"),
]

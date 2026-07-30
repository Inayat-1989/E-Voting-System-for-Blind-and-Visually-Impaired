from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_voter, name="login"),
    path("logout/", views.logout_voter, name="logout"),
    path('api/process-speech/', views.process_speech, name='process_speech'),
]
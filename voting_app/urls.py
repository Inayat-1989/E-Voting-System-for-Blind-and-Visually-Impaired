from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # path("register/", views.register_voter, name="register"),
    # path("verify/<str:token>/", views.verify_email, name="verify_email"),
    path("login/", views.login_voter, name="login"),
    # path("verify-login/<str:token>/", views.verify_login, name="verify_login"),
    path("logout/", views.logout_voter, name="logout"),
    path("elections/", views.elections_list, name="elections"),
    path('api/process-speech/', views.process_speech, name='process_speech'),
    path("vote/<int:election_id>/", views.vote, name="vote"),
]

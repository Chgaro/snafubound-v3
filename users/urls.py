from django.urls import path
from . import views

urlpatterns = [
    path("", views.player_list, name="player_list"),
    path("<slug:slug>/", views.player_detail, name="player_detail"),
]
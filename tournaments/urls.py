from django.urls import path
from . import views

urlpatterns = [
    path("", views.tournament_list, name="tournament_list"),
    path("<slug:slug>/", views.tournament_detail, name="tournament_detail"),
    path(
        "<slug:tournament_slug>/rounds/<int:round_number>/",
        views.round_detail,
        name="round_detail",
    ),
]
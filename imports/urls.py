from django.urls import path

from . import views

urlpatterns = [
    path(
        "tournament/",
        views.tournament_import_view,
        name="tournament_import",
    ),
]
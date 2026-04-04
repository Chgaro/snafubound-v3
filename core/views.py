from django.db.models import Count, Sum
from django.shortcuts import render

from tournaments.models import Tournament, TournamentEntry
from catalog.models import Set


def home(request):
    # Últimos torneos
    latest_tournaments = (
        Tournament.objects.select_related("set")
        .order_by("-date", "-id")[:4]
    )

    # Set actual
    current_set = Set.objects.filter(is_active=True).first()

    # Histórico: solo torneos finalizados
    base_entries = (
        TournamentEntry.objects.select_related("player", "legend", "tournament")
        .filter(tournament__status="finished")
    )

    # Entradas del set actual
    current_entries = base_entries
    if current_set:
        current_entries = base_entries.filter(tournament__set=current_set)

    # ---- JUGADOR DESTACADO HISTÓRICO ----
    top_player_all = (
        base_entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_tournaments=Count("id"),
        )
        .order_by("-total_points", "-total_wins", "-total_tournaments")
        .first()
    )

    # ---- JUGADOR DESTACADO SET ACTUAL ----
    top_player_current = (
        current_entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_tournaments=Count("id"),
        )
        .order_by("-total_points", "-total_wins", "-total_tournaments")
        .first()
    )

    # ---- LEYENDA DESTACADA HISTÓRICO ----
    top_legend_all = (
        base_entries.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
        )
        .order_by("-total_uses", "-total_points")
        .first()
    )

    # ---- LEYENDA DESTACADA SET ACTUAL ----
    top_legend_current = (
        current_entries.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
        )
        .order_by("-total_uses", "-total_points")
        .first()
    )

    # ---- TOP JUGADORES ----
    top_players = (
        base_entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
        )
        .order_by("-total_points", "-total_wins")[:3]
    )

    context = {
        "latest_tournaments": latest_tournaments,
        "current_set": current_set,
        "top_player_all": top_player_all,
        "top_player_current": top_player_current,
        "top_legend_all": top_legend_all,
        "top_legend_current": top_legend_current,
        "top_players": top_players,
    }

    return render(request, "core/home.html", context)
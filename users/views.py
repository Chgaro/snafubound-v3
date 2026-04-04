from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, render

from catalog.models import Set
from tournaments.models import TournamentEntry
from .models import Player
from .services import build_player_detail_data


def player_list(request):
    scope = request.GET.get("scope", "all")
    if scope not in {"all", "set"}:
        scope = "all"

    current_set = Set.objects.filter(is_active=True).first()

    entries = (
        TournamentEntry.objects.select_related("player", "tournament", "legend", "tournament__set")
        .filter(tournament__status="finished")
    )

    if scope == "set" and current_set:
        entries = entries.filter(tournament__set=current_set)

    ranking_points = (
        entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
            total_tournaments=Count("tournament", distinct=True),
        )
        .order_by("-total_points", "-total_wins", "player__display_name")[:5]
    )

    ranking_wins = (
        entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
            total_tournaments=Count("tournament", distinct=True),
        )
        .order_by("-total_wins", "-total_points", "player__display_name")[:5]
    )

    ranking_participations = (
        entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
            total_tournaments=Count("tournament", distinct=True),
        )
        .order_by("-total_tournaments", "-total_points", "player__display_name")[:5]
    )

    context = {
        "ranking_points": ranking_points,
        "ranking_wins": ranking_wins,
        "ranking_participations": ranking_participations,
        "scope": scope,
        "current_set": current_set,
    }

    return render(request, "users/player_list.html", context)


def player_detail(request, slug):
    player = get_object_or_404(Player, slug=slug)

    scope = request.GET.get("scope", "all")
    if scope not in {"all", "set"}:
        scope = "all"

    current_set = Set.objects.filter(is_active=True).first()

    entries = (
        player.tournament_entries
        .select_related("tournament", "legend", "tournament__set")
        .filter(tournament__status="finished")
        .order_by("-tournament__date", "-tournament__id")
    )

    if scope == "set" and current_set:
        entries = entries.filter(tournament__set=current_set)

    data = build_player_detail_data(player=player, entries=entries)

    context = {
        "player": player,
        "entries": entries,
        "stats": data["stats"],
        "total_matches": data["total_matches"],
        "winrate": data["winrate"],
        "favorite_legend": data["favorite_legend"],
        "nemesis": data["nemesis"],
        "favorite_opponent": data["favorite_opponent"],
        "rivalries": data["rivalries"],
        "scope": scope,
        "current_set": current_set,
    }

    return render(request, "users/player_detail.html", context)
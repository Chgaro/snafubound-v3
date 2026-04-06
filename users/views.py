from urllib.parse import urlencode

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from catalog.models import Set
from tournaments.models import TournamentEntry
from .models import Player
from .services import (
    build_player_detail_data,
    build_player_rows,
    build_player_search_data,
)


MIN_TOURNAMENTS_FOR_WINRATE_RANKING = 5


def _build_player_rankings(entries):
    player_rows = build_player_rows(entries)

    ranking_points = sorted(
        player_rows,
        key=lambda row: (
            -(row["total_points"] or 0),
            -(row["total_wins"] or 0),
            -(row["total_tournaments"] or 0),
            row["player__display_name"].lower(),
        ),
    )[:5]

    ranking_wins = sorted(
        player_rows,
        key=lambda row: (
            -(row["total_wins"] or 0),
            -(row["total_points"] or 0),
            -(row["total_tournaments"] or 0),
            row["player__display_name"].lower(),
        ),
    )[:5]

    winrate_candidates = [
        row
        for row in player_rows
        if (row["total_tournaments"] or 0) >= MIN_TOURNAMENTS_FOR_WINRATE_RANKING
        and (row["total_matches"] or 0) > 0
    ]

    ranking_winrate = sorted(
        winrate_candidates,
        key=lambda row: (
            -(row["winrate"] or 0),
            -(row["total_matches"] or 0),
            -(row["total_points"] or 0),
            row["player__display_name"].lower(),
        ),
    )[:5]

    return {
        "ranking_points": ranking_points,
        "ranking_wins": ranking_wins,
        "ranking_winrate": ranking_winrate,
    }


def player_list(request):
    scope = request.GET.get("scope", "all")
    if scope not in {"all", "set"}:
        scope = "all"

    query = (request.GET.get("q") or "").strip()

    current_set = Set.objects.filter(is_active=True).first()

    entries = (
        TournamentEntry.objects.select_related("player", "tournament", "legend", "tournament__set")
        .filter(tournament__status="finished")
    )

    if scope == "set" and current_set:
        entries = entries.filter(tournament__set=current_set)

    search_data = build_player_search_data(entries=entries, query=query)

    if search_data["exact_match"]:
        url = reverse("player_detail", kwargs={"slug": search_data["exact_match"]["player__slug"]})
        if scope == "set":
            url = f"{url}?{urlencode({'scope': 'set'})}"
        return redirect(url)

    rankings = _build_player_rankings(entries)

    context = {
        "ranking_points": rankings["ranking_points"],
        "ranking_wins": rankings["ranking_wins"],
        "ranking_winrate": rankings["ranking_winrate"],
        "scope": scope,
        "current_set": current_set,
        "min_tournaments_for_winrate_ranking": MIN_TOURNAMENTS_FOR_WINRATE_RANKING,
        "search_query": search_data["query"],
        "search_results": search_data["results"],
        "is_search_mode": search_data["has_query"],
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
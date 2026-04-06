from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.urls import reverse

from catalog.models import Set
from tournaments.models import Tournament, TournamentEntry
from users.services import build_player_search_data


def _with_winrate(rows):
    enriched = []

    for row in rows:
        total_wins = row.get("total_wins") or 0
        total_losses = row.get("total_losses") or 0
        total_draws = row.get("total_draws") or 0
        total_matches = total_wins + total_losses + total_draws

        if total_matches > 0:
            winrate = ((total_wins + (0.5 * total_draws)) / total_matches) * 100
        else:
            winrate = 0

        row["total_matches"] = total_matches
        row["winrate"] = winrate
        enriched.append(row)

    return enriched


def home(request):
    query = (request.GET.get("q") or "").strip()

    latest_tournaments = (
        Tournament.objects.select_related("set")
        .order_by("-date", "-id")[:4]
    )

    current_set = Set.objects.filter(is_active=True).first()

    base_entries = (
        TournamentEntry.objects.select_related("player", "legend", "tournament", "tournament__set")
        .filter(tournament__status="finished")
    )

    search_data = build_player_search_data(entries=base_entries, query=query)

    if search_data["exact_match"]:
        return redirect(
            reverse("player_detail", kwargs={"slug": search_data["exact_match"]["player__slug"]})
        )

    base_entries_with_legend = base_entries.filter(legend__isnull=False)

    if current_set:
        current_entries = base_entries.filter(tournament__set=current_set)
        current_entries_with_legend = base_entries_with_legend.filter(
            tournament__set=current_set
        )
    else:
        current_entries = TournamentEntry.objects.none()
        current_entries_with_legend = TournamentEntry.objects.none()

    top_player_all_rows = list(
        base_entries.values(
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
            total_tournaments=Count("id"),
        )
        .order_by(
            "-total_points",
            "-total_wins",
            "-total_tournaments",
            "player__display_name",
        )[:1]
    )
    top_player_all = _with_winrate(top_player_all_rows)[0] if top_player_all_rows else None

    top_legend_all = (
        base_entries_with_legend.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
        )
        .order_by(
            "-total_uses",
            "-total_points",
            "-total_wins",
            "legend__name",
        )
        .first()
    )

    top_player_current_rows = list(
        current_entries.values(
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
            total_tournaments=Count("id"),
        )
        .order_by(
            "-total_points",
            "-total_wins",
            "-total_tournaments",
            "player__display_name",
        )[:1]
    )
    top_player_current = _with_winrate(top_player_current_rows)[0] if top_player_current_rows else None

    top_legend_current = (
        current_entries_with_legend.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
        )
        .order_by(
            "-total_uses",
            "-total_points",
            "-total_wins",
            "legend__name",
        )
        .first()
    )

    top_players_rows = list(
        base_entries.values(
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
            total_tournaments=Count("id"),
        )
        .order_by(
            "-total_points",
            "-total_wins",
            "-total_tournaments",
            "player__display_name",
        )[:5]
    )
    top_players = _with_winrate(top_players_rows)

    top_legends = (
        base_entries_with_legend.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
        )
        .order_by(
            "-total_uses",
            "-total_points",
            "-total_wins",
            "legend__name",
        )[:5]
    )

    context = {
        "latest_tournaments": latest_tournaments,
        "current_set": current_set,
        "top_player_all": top_player_all,
        "top_legend_all": top_legend_all,
        "top_player_current": top_player_current,
        "top_legend_current": top_legend_current,
        "top_players": top_players,
        "top_legends": top_legends,
        "search_query": search_data["query"],
        "search_results": search_data["results"],
        "is_search_mode": search_data["has_query"],
    }

    return render(request, "core/home.html", context)
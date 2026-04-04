from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, render

from tournaments.models import TournamentEntry
from .models import Legend, Set
from .services import build_legend_stats


def legend_list(request):
    scope = request.GET.get("scope", "all")
    if scope not in {"all", "set"}:
        scope = "all"

    current_set = Set.objects.filter(is_active=True).first()

    entries = (
        TournamentEntry.objects.select_related("legend", "tournament", "tournament__set")
        .filter(
            tournament__status="finished",
            legend__isnull=False,
        )
    )

    if scope == "set" and current_set:
        entries = entries.filter(tournament__set=current_set)

    ranking_played = (
        entries.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
        )
        .order_by("-total_uses", "-total_points", "legend__name")[:5]
    )

    ranking_points = (
        entries.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
        )
        .order_by("-total_points", "-total_wins", "legend__name")[:5]
    )

    ranking_wins = (
        entries.values(
            "legend__id",
            "legend__name",
            "legend__slug",
            "legend__image",
        )
        .annotate(
            total_uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
        )
        .order_by("-total_wins", "-total_points", "legend__name")[:5]
    )

    context = {
        "ranking_played": ranking_played,
        "ranking_points": ranking_points,
        "ranking_wins": ranking_wins,
        "scope": scope,
        "current_set": current_set,
    }

    return render(request, "catalog/legend_list.html", context)


def legend_detail(request, slug):
    legend = get_object_or_404(Legend, slug=slug)

    scope = request.GET.get("scope", "all")
    if scope not in {"all", "set"}:
        scope = "all"

    current_set = Set.objects.filter(is_active=True).first()

    entries = (
        TournamentEntry.objects.select_related("player", "tournament", "tournament__set")
        .filter(
            legend=legend,
            tournament__status="finished",
        )
        .order_by("-tournament__date", "-tournament__id")
    )

    if scope == "set" and current_set:
        entries = entries.filter(tournament__set=current_set)

    data = build_legend_stats(
        legend=legend,
        entries=entries,
        current_set=current_set if scope == "set" else None,
    )

    context = {
        "legend": legend,
        "stats": data["stats"],
        "winrate": data["winrate"],
        "avg_points": data["avg_points"],
        "players_usage": data["players_usage"],
        "top_player": data["top_player"],
        "mirror_matches": data["mirror_matches"],
        "matchups": data["matchups"],
        "best_matchups": data["best_matchups"],
        "worst_matchups": data["worst_matchups"],
        "scope": scope,
        "current_set": current_set,
    }

    return render(request, "catalog/legend_detail.html", context)
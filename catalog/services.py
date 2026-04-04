from django.db.models import Count, Q, Sum

from tournaments.models import Match, TournamentEntry


MIN_MATCHES_FOR_MATCHUP = 2


def build_legend_stats(legend, entries=None, current_set=None):
    if entries is None:
        entries = (
            TournamentEntry.objects.select_related("player", "tournament", "tournament__set")
            .filter(
                legend=legend,
                tournament__status="finished",
            )
            .order_by("-tournament__date", "-tournament__id")
        )

    stats = entries.aggregate(
        total_uses=Count("id"),
        total_points=Sum("points"),
        total_wins=Sum("wins"),
        total_losses=Sum("losses"),
        total_draws=Sum("draws"),
    )

    total_wins = stats["total_wins"] or 0
    total_losses = stats["total_losses"] or 0
    total_draws = stats["total_draws"] or 0
    total_matches = total_wins + total_losses + total_draws

    if total_matches > 0:
        winrate = ((total_wins + (0.5 * total_draws)) / total_matches) * 100
    else:
        winrate = 0

    avg_points = 0
    total_uses = stats["total_uses"] or 0
    total_points = stats["total_points"] or 0
    if total_uses > 0:
        avg_points = total_points / total_uses

    players_usage = (
        entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        )
        .annotate(
            uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
        )
        .order_by("-uses", "-total_points", "-total_wins", "player__display_name")
    )

    top_player = players_usage.first()

    matchup_stats = {}
    mirror_matches = 0

    matches = Match.objects.select_related(
        "player1_entry__legend",
        "player2_entry__legend",
    ).filter(
        Q(player1_entry__legend=legend) | Q(player2_entry__legend=legend),
        round__tournament__status="finished",
        round__status="finished",
        is_bye=False,
        player2_entry__isnull=False,
    )

    if current_set:
        matches = matches.filter(round__tournament__set=current_set)

    for match in matches:
        legend_1 = match.player1_entry.legend
        legend_2 = match.player2_entry.legend

        if legend_1 is None or legend_2 is None:
            continue

        if legend_1.id == legend.id and legend_2.id == legend.id:
            mirror_matches += 1
            continue

        if legend_1.id == legend.id:
            opponent = legend_2
            own_wins = match.player1_wins
            opp_wins = match.player2_wins
        elif legend_2.id == legend.id:
            opponent = legend_1
            own_wins = match.player2_wins
            opp_wins = match.player1_wins
        else:
            continue

        if opponent.id not in matchup_stats:
            matchup_stats[opponent.id] = {
                "legend": opponent,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "matches": 0,
                "winrate": 0,
            }

        matchup_stats[opponent.id]["matches"] += 1

        if own_wins > opp_wins:
            matchup_stats[opponent.id]["wins"] += 1
        elif own_wins < opp_wins:
            matchup_stats[opponent.id]["losses"] += 1
        else:
            matchup_stats[opponent.id]["draws"] += 1

    matchup_list = []

    for data in matchup_stats.values():
        if data["matches"] < MIN_MATCHES_FOR_MATCHUP:
            continue

        data["winrate"] = (
            (data["wins"] + (0.5 * data["draws"])) / data["matches"]
        ) * 100

        matchup_list.append(data)

    matchup_list.sort(
        key=lambda x: (
            -x["matches"],
            -x["winrate"],
            x["legend"].name.lower(),
        )
    )

    best_matchups = sorted(
        matchup_list,
        key=lambda x: (
            -x["winrate"],
            -x["matches"],
            x["legend"].name.lower(),
        ),
    )[:3]

    worst_matchups = sorted(
        matchup_list,
        key=lambda x: (
            x["winrate"],
            -x["matches"],
            x["legend"].name.lower(),
        ),
    )[:3]

    return {
        "stats": stats,
        "winrate": winrate,
        "avg_points": avg_points,
        "players_usage": players_usage,
        "top_player": top_player,
        "mirror_matches": mirror_matches,
        "matchups": matchup_list,
        "best_matchups": best_matchups,
        "worst_matchups": worst_matchups,
    }
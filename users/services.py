from django.db.models import Count, Q, Sum

from tournaments.models import Match


MIN_MATCHES_FOR_RIVALRY = 2


def build_player_rows(entries):
    player_rows = list(
        entries.values(
            "player__id",
            "player__display_name",
            "player__slug",
            "player__avatar",
        ).annotate(
            total_points=Sum("points"),
            total_wins=Sum("wins"),
            total_losses=Sum("losses"),
            total_draws=Sum("draws"),
            total_tournaments=Count("tournament", distinct=True),
        )
    )

    for row in player_rows:
        total_wins = row["total_wins"] or 0
        total_losses = row["total_losses"] or 0
        total_draws = row["total_draws"] or 0
        total_matches = total_wins + total_losses + total_draws

        row["total_matches"] = total_matches

        if total_matches > 0:
            row["winrate"] = ((total_wins + (0.5 * total_draws)) / total_matches) * 100
        else:
            row["winrate"] = 0

    return player_rows


def build_player_search_data(entries, query, limit=12):
    query = (query or "").strip()

    if not query:
        return {
            "query": "",
            "exact_match": None,
            "results": [],
            "has_query": False,
        }

    normalized_query = query.casefold()

    player_rows = build_player_rows(
        entries.filter(player__display_name__icontains=query)
    )

    exact_match = next(
        (
            row
            for row in player_rows
            if (row["player__display_name"] or "").casefold() == normalized_query
        ),
        None,
    )

    results = sorted(
        player_rows,
        key=lambda row: (
            0 if (row["player__display_name"] or "").casefold().startswith(normalized_query) else 1,
            -(row["total_points"] or 0),
            -(row["winrate"] or 0),
            -(row["total_tournaments"] or 0),
            (row["player__display_name"] or "").lower(),
        ),
    )[:limit]

    return {
        "query": query,
        "exact_match": exact_match,
        "results": results,
        "has_query": True,
    }


def build_player_summary(entries):
    stats = entries.aggregate(
        total_points=Sum("points"),
        total_wins=Sum("wins"),
        total_losses=Sum("losses"),
        total_draws=Sum("draws"),
        total_tournaments=Count("id"),
    )

    total_wins = stats["total_wins"] or 0
    total_losses = stats["total_losses"] or 0
    total_draws = stats["total_draws"] or 0
    total_matches = total_wins + total_losses + total_draws

    if total_matches > 0:
        winrate = ((total_wins + (0.5 * total_draws)) / total_matches) * 100
    else:
        winrate = 0

    favorite_legend = (
        entries.filter(legend__isnull=False)
        .values("legend__name", "legend__slug")
        .annotate(
            uses=Count("id"),
            total_points=Sum("points"),
            total_wins=Sum("wins"),
        )
        .order_by("-uses", "-total_points", "-total_wins", "legend__name")
        .first()
    )

    return {
        "stats": stats,
        "total_matches": total_matches,
        "winrate": winrate,
        "favorite_legend": favorite_legend,
    }


def build_player_rivalries(player, entries):
    player_entry_ids = list(entries.values_list("id", flat=True))

    if not player_entry_ids:
        return {
            "nemesis": None,
            "favorite_opponent": None,
            "rivalries": [],
        }

    matches = Match.objects.select_related(
        "player1_entry__player",
        "player2_entry__player",
    ).filter(
        Q(player1_entry__in=player_entry_ids) | Q(player2_entry__in=player_entry_ids),
        round__tournament__status="finished",
        round__status="finished",
        is_bye=False,
        player2_entry__isnull=False,
    )

    rivalry_stats = {}

    for match in matches:
        if match.player1_entry_id in player_entry_ids:
            if match.player2_entry.player_id == player.id:
                continue

            opponent = match.player2_entry.player
            own_wins = match.player1_wins
            opp_wins = match.player2_wins

        elif match.player2_entry_id in player_entry_ids:
            if match.player1_entry.player_id == player.id:
                continue

            opponent = match.player1_entry.player
            own_wins = match.player2_wins
            opp_wins = match.player1_wins
        else:
            continue

        if opponent.id not in rivalry_stats:
            rivalry_stats[opponent.id] = {
                "player": opponent,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "matches": 0,
                "winrate": 0,
            }

        rivalry_stats[opponent.id]["matches"] += 1

        if own_wins > opp_wins:
            rivalry_stats[opponent.id]["wins"] += 1
        elif own_wins < opp_wins:
            rivalry_stats[opponent.id]["losses"] += 1
        else:
            rivalry_stats[opponent.id]["draws"] += 1

    rivalries = []

    for data in rivalry_stats.values():
        if data["matches"] < MIN_MATCHES_FOR_RIVALRY:
            continue

        data["winrate"] = (
            (data["wins"] + (0.5 * data["draws"])) / data["matches"]
        ) * 100

        rivalries.append(data)

    rivalries.sort(
        key=lambda x: (
            x["winrate"],
            -x["matches"],
            x["player"].display_name.lower(),
        )
    )

    nemesis = rivalries[0] if rivalries else None

    favorite_opponent = None
    if rivalries:
        best_rivalries = sorted(
            rivalries,
            key=lambda x: (
                -x["winrate"],
                -x["matches"],
                x["player"].display_name.lower(),
            ),
        )

        for candidate in best_rivalries:
            if not nemesis or candidate["player"].id != nemesis["player"].id:
                favorite_opponent = candidate
                break

    return {
        "nemesis": nemesis,
        "favorite_opponent": favorite_opponent,
        "rivalries": rivalries,
    }


def build_player_detail_data(player, entries):
    summary = build_player_summary(entries)
    rivalries = build_player_rivalries(player=player, entries=entries)

    return {
        **summary,
        **rivalries,
    }
from tournaments.models import Tournament, TournamentEntry


def recalculate_tournament_standings(tournament: Tournament) -> None:
    entries = (
        TournamentEntry.objects
        .filter(tournament=tournament)
        .select_related("player", "legend")
    )

    for entry in entries:
        entry.wins = 0
        entry.losses = 0
        entry.draws = 0
        entry.points = 0

    TournamentEntry.objects.bulk_update(
        entries,
        ["wins", "losses", "draws", "points"],
    )

    entry_map = {
        entry.id: entry
        for entry in TournamentEntry.objects.filter(tournament=tournament)
    }

    rounds = (
        tournament.rounds
        .prefetch_related("matches")
        .all()
    )

    for round_obj in rounds:
        for match in round_obj.matches.all():
            player1 = entry_map.get(match.player1_entry_id)

            if match.is_bye:
                if player1:
                    player1.wins += 1
                    player1.points += 3
                continue

            player2 = entry_map.get(match.player2_entry_id)

            if not player1 or not player2:
                continue

            if match.player1_wins > match.player2_wins:
                player1.wins += 1
                player2.losses += 1
                player1.points += 3
            elif match.player2_wins > match.player1_wins:
                player2.wins += 1
                player1.losses += 1
                player2.points += 3
            else:
                player1.draws += 1
                player2.draws += 1
                player1.points += 1
                player2.points += 1

    TournamentEntry.objects.bulk_update(
        entry_map.values(),
        ["wins", "losses", "draws", "points"],
    )
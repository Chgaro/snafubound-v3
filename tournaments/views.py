from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Round, Tournament


def tournament_list(request):
    tournaments = Tournament.objects.select_related("set").all()
    return render(
        request,
        "tournaments/tournament_list.html",
        {"tournaments": tournaments},
    )


def tournament_detail(request, slug):
    tournament = get_object_or_404(
        Tournament.objects.select_related("set").prefetch_related("rounds", "entries"),
        slug=slug,
    )

    rounds = tournament.rounds.all().order_by("number")
    entries = tournament.entries.select_related("player", "legend").all().order_by(
        "-points",
        "-wins",
        "-draws",
        "losses",
        "player__display_name",
    )

    total_matches = (
        Round.objects.filter(tournament=tournament)
        .aggregate(total=Count("matches"))
        .get("total", 0)
    ) or 0

    context = {
        "tournament": tournament,
        "rounds": rounds,
        "entries": entries,
        "total_players": entries.count(),
        "total_rounds": rounds.count(),
        "total_matches": total_matches,
    }

    return render(request, "tournaments/tournament_detail.html", context)


def round_detail(request, tournament_slug, round_number):
    tournament = get_object_or_404(Tournament.objects.select_related("set"), slug=tournament_slug)
    round_obj = get_object_or_404(
        Round.objects.select_related("tournament").prefetch_related(
            "matches__player1_entry__player",
            "matches__player1_entry__legend",
            "matches__player2_entry__player",
            "matches__player2_entry__legend",
        ),
        tournament=tournament,
        number=round_number,
    )
    return render(
        request,
        "tournaments/round_detail.html",
        {
            "tournament": tournament,
            "round": round_obj,
        },
    )
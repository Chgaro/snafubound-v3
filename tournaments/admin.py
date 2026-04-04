from django.contrib import admin, messages
from .models import Match, Round, Tournament, TournamentEntry
from .services import recalculate_tournament_standings


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "set", "date", "status", "external_id", "created_at")
    list_filter = ("status", "date", "set")
    search_fields = ("name", "slug", "external_id", "set__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("set",)

    actions = ["recalculate_standings_action"]

    def recalculate_standings_action(self, request, queryset):
        for tournament in queryset:
            recalculate_tournament_standings(tournament)

        self.message_user(
            request,
            f"Standings recalculados para {queryset.count()} torneo(s).",
            level=messages.SUCCESS,
        )

    recalculate_standings_action.short_description = "Recalcular standings"


@admin.register(TournamentEntry)
class TournamentEntryAdmin(admin.ModelAdmin):
    list_display = (
        "tournament",
        "player",
        "legend",
        "wins",
        "losses",
        "draws",
        "points",
        "final_position",
    )
    list_filter = ("tournament", "legend")
    search_fields = (
        "tournament__name",
        "player__display_name",
        "legend__name",
        "external_id",
    )
    autocomplete_fields = ("tournament", "player", "legend")


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("tournament", "number", "status", "external_id", "created_at")
    list_filter = ("tournament", "status")
    search_fields = ("tournament__name", "external_id")
    autocomplete_fields = ("tournament",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "round",
        "table_number",
        "player1_entry",
        "player2_entry",
        "is_bye",
        "player1_wins",
        "player2_wins",
    )
    list_filter = ("round__tournament", "round", "is_bye")
    search_fields = (
        "round__tournament__name",
        "player1_entry__player__display_name",
        "player2_entry__player__display_name",
        "external_id",
    )
    autocomplete_fields = ("round", "player1_entry", "player2_entry")
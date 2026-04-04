from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class TournamentStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    FINISHED = "finished", "Finalizado"


class RoundStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    FINISHED = "finished", "Finalizada"


class Tournament(models.Model):
    name = models.CharField("Nombre", max_length=140)
    slug = models.SlugField("Slug", max_length=160, unique=True)
    external_id = models.CharField(
        "ID externo",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    date = models.DateField("Fecha", blank=True, null=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=TournamentStatus.choices,
        default=TournamentStatus.DRAFT,
    )
    set = models.ForeignKey(
        "catalog.Set",
        verbose_name="Set",
        on_delete=models.PROTECT,
        related_name="tournaments",
    )
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Torneo"
        verbose_name_plural = "Torneos"
        ordering = ["-date", "-created_at", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tournament_detail", kwargs={"slug": self.slug})

    def get_status_badge_variant(self):
        if self.status == TournamentStatus.DRAFT:
            return "badge-status-draft"

        if self.status == TournamentStatus.FINISHED:
            return "badge-status-finished"

        return ""

    @property
    def status_badge_classes(self):
        variant = self.get_status_badge_variant()
        if variant:
            return f"meta-pill badge-status {variant}"
        return "meta-pill badge-status"


class TournamentEntry(models.Model):
    tournament = models.ForeignKey(
        "tournaments.Tournament",
        verbose_name="Torneo",
        on_delete=models.CASCADE,
        related_name="entries",
    )
    player = models.ForeignKey(
        "users.Player",
        verbose_name="Jugador",
        on_delete=models.CASCADE,
        related_name="tournament_entries",
    )
    legend = models.ForeignKey(
        "catalog.Legend",
        verbose_name="Leyenda",
        on_delete=models.PROTECT,
        related_name="tournament_entries",
        blank=True,
        null=True,
    )
    external_id = models.CharField(
        "ID externo",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    wins = models.PositiveIntegerField("Victorias", default=0)
    losses = models.PositiveIntegerField("Derrotas", default=0)
    draws = models.PositiveIntegerField("Empates", default=0)
    points = models.PositiveIntegerField("Puntos", default=0)
    final_position = models.PositiveIntegerField(
        "Posición final",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        ordering = ["tournament", "player"]
        constraints = [
            models.UniqueConstraint(
                fields=["tournament", "player"],
                name="unique_player_per_tournament",
            )
        ]

    def __str__(self):
        return f"{self.player} · {self.tournament}"

    @property
    def legend_display_name(self):
        if self.legend:
            return self.legend.name
        return "Sin leyenda"

    @property
    def has_legend(self):
        return self.legend_id is not None


class Round(models.Model):
    tournament = models.ForeignKey(
        "tournaments.Tournament",
        verbose_name="Torneo",
        on_delete=models.CASCADE,
        related_name="rounds",
    )
    number = models.PositiveIntegerField("Número")
    external_id = models.CharField(
        "ID externo",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=RoundStatus.choices,
        default=RoundStatus.PENDING,
    )
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = "Ronda"
        verbose_name_plural = "Rondas"
        ordering = ["tournament", "number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tournament", "number"],
                name="unique_round_number_per_tournament",
            )
        ]

    def __str__(self):
        return f"{self.tournament} · Ronda {self.number}"

    def get_absolute_url(self):
        return reverse(
            "round_detail",
            kwargs={
                "tournament_slug": self.tournament.slug,
                "round_number": self.number,
            },
        )

    def get_status_badge_variant(self):
        if self.status == RoundStatus.PENDING:
            return "badge-status-pending"

        if self.status == RoundStatus.FINISHED:
            return "badge-status-finished"

        return ""

    @property
    def status_badge_classes(self):
        variant = self.get_status_badge_variant()
        if variant:
            return f"meta-pill badge-status {variant}"
        return "meta-pill badge-status"


class Match(models.Model):
    round = models.ForeignKey(
        "tournaments.Round",
        verbose_name="Ronda",
        on_delete=models.CASCADE,
        related_name="matches",
    )
    external_id = models.CharField(
        "ID externo",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    table_number = models.PositiveIntegerField(
        "Mesa",
        blank=True,
        null=True,
    )
    player1_entry = models.ForeignKey(
        "tournaments.TournamentEntry",
        verbose_name="Jugador 1",
        on_delete=models.CASCADE,
        related_name="matches_as_player1",
    )
    player2_entry = models.ForeignKey(
        "tournaments.TournamentEntry",
        verbose_name="Jugador 2",
        on_delete=models.CASCADE,
        related_name="matches_as_player2",
        blank=True,
        null=True,
    )
    is_bye = models.BooleanField("Es bye", default=False)
    player1_wins = models.PositiveIntegerField("Victorias jugador 1", default=0)
    player2_wins = models.PositiveIntegerField("Victorias jugador 2", default=0)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    def clean(self):
        errors = {}

        if self.is_bye:
            if not self.player1_entry_id:
                errors["player1_entry"] = "Un BYE debe tener jugador 1."

            if self.player2_entry_id is not None:
                errors["player2_entry"] = "Un BYE no puede tener jugador 2."

            if self.player1_wins < self.player2_wins:
                errors["player1_wins"] = "Un BYE no puede tener menos victorias que el jugador 2."
        else:
            if not self.player2_entry_id:
                errors["player2_entry"] = "El jugador 2 es obligatorio si no es un BYE."

            if self.player1_entry_id and self.player2_entry_id:
                if self.player1_entry_id == self.player2_entry_id:
                    errors["player2_entry"] = "Un jugador no puede enfrentarse a sí mismo."

        if self.round_id and self.player1_entry_id:
            if self.player1_entry.tournament_id != self.round.tournament_id:
                errors["player1_entry"] = "El jugador 1 no pertenece al torneo de esta ronda."

        if self.round_id and self.player2_entry_id:
            if self.player2_entry.tournament_id != self.round.tournament_id:
                errors["player2_entry"] = "El jugador 2 no pertenece al torneo de esta ronda."

        if errors:
            raise ValidationError(errors)
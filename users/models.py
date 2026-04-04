from django.db import models
from django.urls import reverse


class Player(models.Model):
    display_name = models.CharField("Nombre visible", max_length=80)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    external_id = models.CharField(
        "ID externo",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    avatar = models.ImageField(
        "Avatar",
        upload_to="players/avatars/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse("player_detail", kwargs={"slug": self.slug})
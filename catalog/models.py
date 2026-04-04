from django.db import models
from django.urls import reverse


class Legend(models.Model):
    name = models.CharField("Nombre", max_length=80)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    external_id = models.CharField(
        "ID externo",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )
    image = models.ImageField(
        "Imagen",
        upload_to="legends/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("Activa", default=True)
    created_at = models.DateTimeField("Creada", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = "Leyenda"
        verbose_name_plural = "Leyendas"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("legend_detail", kwargs={"slug": self.slug})


class Set(models.Model):
    name = models.CharField("Nombre", max_length=80)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    release_date = models.DateField("Fecha de lanzamiento", blank=True, null=True)
    is_active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Set"
        verbose_name_plural = "Sets"
        ordering = ["-release_date", "name"]

    def __str__(self):
        return self.name

    def get_badge_variant(self):
        value = f"{self.slug} {self.name}".lower()

        if "origin" in value:
            return "badge-origins"

        if "spiritforged" in value or "spirit-forged" in value:
            return "badge-spiritforged"

        if "unleashed" in value:
            light_keywords = (
                "pre-rift",
                "prerift",
                "starter",
                "fiora",
            )
            if any(keyword in value for keyword in light_keywords):
                return "badge-unleashed-light"
            return "badge-unleashed"

        return ""

    @property
    def badge_classes(self):
        variant = self.get_badge_variant()
        if variant:
            return f"meta-pill badge-set {variant}"
        return "meta-pill badge-set"
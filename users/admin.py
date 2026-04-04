from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "slug", "external_id", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("display_name", "slug", "external_id")
    prepopulated_fields = {"slug": ("display_name",)}
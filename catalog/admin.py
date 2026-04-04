from django.contrib import admin
from .models import Legend, Set


@admin.register(Legend)
class LegendAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "external_id", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "external_id")
    prepopulated_fields = {"slug": ("name",)}
    
@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "release_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
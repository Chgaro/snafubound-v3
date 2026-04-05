from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("players/", include("users.urls")),
    path("legends/", include("catalog.urls")),
    path("tournaments/", include("tournaments.urls")),
    path("imports/", include("imports.urls")),
]


urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.legend_list, name="legend_list"),
    path("<slug:slug>/", views.legend_detail, name="legend_detail"),
]
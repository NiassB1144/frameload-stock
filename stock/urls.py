from django.urls import path
from . import views

app_name = "stock"

urlpatterns = [
    path("", views.stock_list, name="list"),
    path("ajouter/", views.stock_create, name="create"),
    path("alertes/", views.stock_alerts, name="alerts"),
]
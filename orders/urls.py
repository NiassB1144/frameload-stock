
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="list"),
    path("ajouter/", views.order_create, name="create"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("<int:pk>/modifier/", views.order_update, name="update"),
    path("<int:pk>/supprimer/", views.order_delete, name="delete"),
    path("<int:pk>/facture.pdf", views.order_invoice, name="invoice"),
]

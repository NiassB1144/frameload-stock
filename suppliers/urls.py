from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [ path("", views.supplier_list, name="list"),
    path("ajouter/", views.supplier_create, name="create"),
    path("<int:pk>/modifier/", views.supplier_update, name="update"),
    path("<int:pk>/supprimer/", views.supplier_delete, name="delete"),
    ]
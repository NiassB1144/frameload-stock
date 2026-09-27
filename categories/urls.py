from django.urls import path
from . import views

app_name = 'categories'


urlpatterns = [
    path("", views.category_list, name="list"),
    path("ajouter/", views.category_create, name="create"),
    path("<int:pk>/modifier/", views.category_update, name="update"),
    path("<int:pk>/supprimer/", views.category_delete, name="delete"),
]
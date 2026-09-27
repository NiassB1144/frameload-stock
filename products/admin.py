from django.contrib import admin
from .models import Product
# Enrigistrer le models Product dans l'admin

admin.site.register(Product)
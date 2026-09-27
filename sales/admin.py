from django.contrib import admin
from .models import Sale, SaleItem
# Enregistrer le models Sale et SaleItem dans l'admin

admin.site.register(Sale)
admin.site.register(SaleItem)


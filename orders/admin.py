from django.contrib import admin
from .models import Order, OrderItem
# Engistrer le models Order et OrderItem dans l'admin

admin.site.register(Order)
admin.site.register(OrderItem)

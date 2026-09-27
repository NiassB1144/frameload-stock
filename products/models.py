from django.db import models
from categories.models import Category
from suppliers.models import Supplier
import uuid


class Product(models.Model):
    name = models.CharField(max_length=150)
    reference = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"P-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

from django.db import models
from products.models import Product
import uuid


class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "En attente"),
        ("CONFIRMED", "Confirmée"),
        ("COMPLETED", "Terminée"),
        ("CANCELLED", "Annulée"),
    ]

    number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
    )

    client_name = models.CharField(
        max_length=150,
        blank=True
    )

    client_phone = models.CharField(
        max_length=20,
        blank=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"CMD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

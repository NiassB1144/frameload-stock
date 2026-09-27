from django.db import models
from django.conf import settings
from products.models import Product


class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ("IN", "Entrée"),
        ("OUT", "Sortie"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_movements"
    )

    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_TYPES
    )

    quantity = models.PositiveIntegerField()

    reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"


class StockAlertReadState(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_alert_read_state",
    )
    signature = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alertes consultées par {self.user}"

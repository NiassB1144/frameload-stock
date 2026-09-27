import hashlib

from django.db import models

from products.models import Product


def low_stock_snapshot(user):
    if not user.is_authenticated or not user.has_perm("stock.view_stockmovement"):
        return [], 0, ""

    alerts = Product.objects.filter(
        stock_quantity__lte=models.F("minimum_stock")
    )
    alert_state = list(
        alerts.order_by("pk").values_list("pk", "stock_quantity", "minimum_stock")
    )
    signature = hashlib.sha256(repr(alert_state).encode("utf-8")).hexdigest()
    products = list(
        alerts.only("id", "name", "stock_quantity", "minimum_stock")
        .order_by("stock_quantity")[:8]
    )
    return products, len(alert_state), signature

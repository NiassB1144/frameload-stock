from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models, transaction
from django.shortcuts import redirect, render

from products.models import Product
from .forms import StockMovementForm
from .models import StockMovement


@login_required
@permission_required("stock.view_stockmovement", raise_exception=True)
def stock_list(request):
    movements = StockMovement.objects.select_related("product").order_by("-created_at")
    query = request.GET.get("q", "").strip()
    movement_type = request.GET.get("type", "").strip()
    if query:
        movements = movements.filter(
            models.Q(product__name__icontains=query)
            | models.Q(product__reference__icontains=query)
            | models.Q(reason__icontains=query)
        )
    if movement_type in {"IN", "OUT"}:
        movements = movements.filter(movement_type=movement_type)

    return render(
        request,
        "stock/list.html",
        {
            "movements": movements,
            "query": query,
            "movement_type": movement_type,
            "has_filters": bool(query or movement_type),
        },
    )


@login_required
@permission_required("stock.add_stockmovement", raise_exception=True)
def stock_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            product = movement.product
            if movement.movement_type == "OUT" and movement.quantity > product.stock_quantity:
                form.add_error(
                    "quantity",
                    "Stock insuffisant pour effectuer cette sortie.",
                )
            else:
                with transaction.atomic():
                    if movement.movement_type == "OUT":
                        product.stock_quantity -= movement.quantity
                    else:
                        product.stock_quantity += movement.quantity
                    product.save(update_fields=["stock_quantity"])
                    movement.save()
                messages.success(request, "Mouvement de stock enregistré avec succès.")
                return redirect(
                    "stock:list"
                    if request.user.has_perm("stock.view_stockmovement")
                    else "home"
                )
    else:
        form = StockMovementForm()

    return render(request, "stock/form.html", {"form": form})


@login_required
@permission_required("stock.view_stockmovement", raise_exception=True)
def stock_alerts(request):
    products = Product.objects.filter(
        stock_quantity__lte=models.F("minimum_stock")
    ).order_by("stock_quantity")
    return render(request, "stock/alerts.html", {"products": products})


from django.shortcuts import render, redirect
from .models import Sale
from .forms import SaleForm, SaleItemForm
from stock.models import StockMovement
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q


@login_required
@permission_required("sales.view_sale", raise_exception=True)
def sale_list(request):
    query = request.GET.get("q", "").strip()
    sales = Sale.objects.prefetch_related("items__product").order_by("-created_at")

    if query:
        sales = sales.filter(
            Q(client_name__icontains=query) | Q(client_phone__icontains=query)
            | Q(id__icontains=query)
        )

    records = [
        {
            "reference": f"Vente #{sale.pk}",
            "client_name": sale.client_name,
            "client_phone": sale.client_phone,
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                }
                for item in sale.items.all()
            ],
            "total": sale.total,
            "created_at": sale.created_at,
        }
        for sale in sales
    ]

    return render(
        request,
        "sales/list.html",
        {
            "sales": records,
            "query": query,
            "total_sales": len(records),
            "has_filters": bool(query),
        }
    )


@login_required
@permission_required("sales.add_sale", raise_exception=True)
def sale_create(request):
    if request.method == "POST":
        sale_form = SaleForm(request.POST)
        item_form = SaleItemForm(request.POST)

        if sale_form.is_valid() and item_form.is_valid():

            item = item_form.save(commit=False)
            product = item.product

            if item.quantity > product.stock_quantity:
                item_form.add_error(
                    "quantity",
                    "Stock insuffisant pour effectuer cette vente."
                )

                return render(
                    request,
                    "sales/form.html",
                    {
                        "sale_form": sale_form,
                        "item_form": item_form,
                    }
                )

            item.unit_price = product.selling_price
            item.total = item.quantity * item.unit_price

            with transaction.atomic():
                sale = sale_form.save()
                item.sale = sale
                item.save()
                sale.total = item.total
                sale.save(update_fields=["total"])
                product.stock_quantity -= item.quantity
                product.save(update_fields=["stock_quantity"])
                StockMovement.objects.create(
                    product=product,
                    movement_type="OUT",
                    quantity=item.quantity,
                    reason=f"Vente #{sale.id}",
                )

            messages.success(request, "Vente enregistrée avec succès.")
            return redirect(
                "sales:list" if request.user.has_perm("sales.view_sale") else "home"
            )

    else:
        sale_form = SaleForm()
        item_form = SaleItemForm()

    return render(
        request,
        "sales/form.html",
        {
            "sale_form": sale_form,
            "item_form": item_form,
        }
    )

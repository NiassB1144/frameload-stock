from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from categories.models import Category
from orders.models import Order
from products.models import Product
from sales.models import Sale, SaleItem
from suppliers.models import Supplier


def _revenue(queryset):
    return queryset.aggregate(total=Sum("total"))["total"] or Decimal("0.00")


def _top_selling_products():
    product_totals = [
        {
            "name": item["product__name"],
            "quantity_sold": item["quantity_sold"],
            "revenue": item["revenue"] or Decimal("0.00"),
        }
        for item in SaleItem.objects.values(
            "product_id", "product__name"
        ).annotate(quantity_sold=Sum("quantity"), revenue=Sum("total"))
    ]

    return sorted(
        product_totals,
        key=lambda product: (-product["quantity_sold"], product["name"]),
    )[:10]


def _recent_activity():
    activity = [
        {
            "label": f"Vente #{sale.pk}",
            "client": sale.client_name or "Client non renseigné",
            "total": sale.total,
            "created_at": sale.created_at,
        }
        for sale in Sale.objects.order_by("-created_at")[:15]
    ]
    return sorted(
        activity,
        key=lambda item: item["created_at"],
        reverse=True,
    )[:15]


@login_required
def dashboard(request):
    if not (
        request.user.groups.filter(name__in=["ADMIN", "MANAGER"]).exists()
        or request.user.is_superuser
    ):
        raise PermissionDenied

    today = timezone.localdate()
    first_day_of_month = today.replace(day=1)
    next_month = (
        first_day_of_month.replace(
            year=first_day_of_month.year + 1, month=1
        )
        if first_day_of_month.month == 12
        else first_day_of_month.replace(month=first_day_of_month.month + 1)
    )

    sales_today = Sale.objects.filter(created_at__date=today)
    sales_this_month = Sale.objects.filter(
        created_at__date__gte=first_day_of_month,
        created_at__date__lt=next_month,
    )

    daily_revenue = []
    french_weekdays = [
        "Lun",
        "Mar",
        "Mer",
        "Jeu",
        "Ven",
        "Sam",
        "Dim",
    ]
    for days_ago in range(6, -1, -1):
        day = today - timedelta(days=days_ago)
        sale_total = _revenue(Sale.objects.filter(created_at__date=day))
        daily_revenue.append(
            {
                "date": day,
                "date_label": f"{french_weekdays[day.weekday()]} {day:%d/%m}",
                "total": sale_total,
            }
        )

    highest_daily_revenue = max(
        (day["total"] for day in daily_revenue),
        default=Decimal("0.00"),
    )
    for day in daily_revenue:
        day["percentage"] = (
            int(day["total"] * 100 / highest_daily_revenue)
            if highest_daily_revenue
            else 0
        )

    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F("minimum_stock"),
        stock_quantity__gt=0,
    ).order_by("stock_quantity", "name")[:10]
    out_of_stock_products = Product.objects.filter(
        stock_quantity=0
    ).order_by("name")[:10]

    context = {
        "total_products": Product.objects.count(),
        "total_categories": Category.objects.count(),
        "total_suppliers": Supplier.objects.count(),
        "total_stock": Product.objects.aggregate(
            total=Sum("stock_quantity")
        )["total"]
        or 0,
        "total_sales": Sale.objects.count(),
        "chiffre_affaires": _revenue(Sale.objects.all()),
        "commandes_en_attente": Order.objects.filter(
            status="PENDING"
        ).count(),
        "produits_stock_faible": Product.objects.filter(
            stock_quantity__lte=F("minimum_stock"),
            stock_quantity__gt=0,
        ).count(),
        "produits_en_rupture": Product.objects.filter(
            stock_quantity=0
        ).count(),
        "ventes_aujourd_hui": sales_today.count(),
        "chiffre_affaires_aujourd_hui": _revenue(sales_today),
        "chiffre_affaires_ce_mois": _revenue(sales_this_month),
        "top_products": _top_selling_products(),
        "recent_activity": _recent_activity(),
        "daily_revenue": daily_revenue,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
    }

    return render(request, "dashboard/index.html", context)

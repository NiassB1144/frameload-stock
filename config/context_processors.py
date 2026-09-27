from .notifications import low_stock_snapshot
from stock.models import StockAlertReadState


def user_access(request):
    """Expose role flags for navigation without weakening view permissions."""
    user = request.user
    groups = set(user.groups.values_list("name", flat=True)) if user.is_authenticated else set()
    if "ADMIN" in groups or user.is_superuser:
        role_label = "Administrateur"
    elif "MANAGER" in groups:
        role_label = "Manager"
    elif "EMPLOYEE" in groups:
        role_label = "Employé"
    else:
        role_label = "Utilisateur"

    low_stock_products, low_stock_count, low_stock_signature = low_stock_snapshot(user)
    low_stock_unread_count = low_stock_count
    if (
        user.is_authenticated
        and user.has_perm("stock.view_stockmovement")
        and StockAlertReadState.objects.filter(
            user=user,
            signature=low_stock_signature,
        ).exists()
    ):
        low_stock_unread_count = 0
    return {
        "is_management": bool({"ADMIN", "MANAGER"} & groups) or user.is_superuser,
        "is_employee": "EMPLOYEE" in groups,
        "role_label": role_label,
        "low_stock_products": low_stock_products,
        "low_stock_count": low_stock_count,
        "low_stock_unread_count": low_stock_unread_count,
        "low_stock_signature": low_stock_signature,
    }

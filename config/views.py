from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .notifications import low_stock_snapshot
from stock.models import StockAlertReadState


def home_view(request):
    return render(request, "home.html")


def server_error(request):
    return render(request, "500.html", status=500)


def login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name="EMPLOYEE").exists():
            return redirect("products:list")
        if request.user.groups.filter(name__in=["ADMIN", "MANAGER"]).exists():
            return redirect("dashboard:index")
        return redirect("products:list")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.groups.filter(name="EMPLOYEE").exists():
                return redirect("products:list")
            if user.groups.filter(name__in=["ADMIN", "MANAGER"]).exists():
                return redirect("dashboard:index")
            return redirect("products:list")

        return render(
            request,
            "registration/login.html",
            {"error": "Identifiant ou mot de passe incorrect."},
        )

    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
@permission_required("stock.view_stockmovement", raise_exception=True)
def acknowledge_stock_alerts(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)
    _, _, signature = low_stock_snapshot(request.user)
    StockAlertReadState.objects.update_or_create(
        user=request.user,
        defaults={"signature": signature},
    )
    return JsonResponse({"acknowledged": True})

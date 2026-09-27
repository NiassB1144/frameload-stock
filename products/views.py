from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q


@login_required
def product_list(request):
    is_employee = request.user.groups.filter(name="EMPLOYEE").exists()
    if not request.user.has_perm("products.view_product") and not is_employee:
        raise PermissionDenied

    products = Product.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(reference__icontains=query)
            | Q(category__name__icontains=query) | Q(supplier__name__icontains=query)
        )

    return render(
        request,
        "products/list.html",
        {"products": products, "query": query}
    )


@login_required
@permission_required("products.add_product", raise_exception=True)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("products:list")

    else:
        form = ProductForm()

    return render(
        request,
        "products/form.html",
        {"form": form}
    )


@login_required
@permission_required("products.change_product", raise_exception=True)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect("products:list")

    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/form.html",
        {"form": form}
    )


@login_required
@permission_required("products.delete_product", raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect("products:list")

    return render(
        request,
        "products/delete.html",
        {"product": product}
    )

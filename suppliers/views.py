from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SupplierForm
from .models import Supplier


@login_required
@permission_required("suppliers.view_supplier", raise_exception=True)
def supplier_list(request):
    suppliers = Supplier.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query)
            | Q(company__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    return render(
        request,
        "suppliers/list.html",
        {"suppliers": suppliers, "query": query},
    )


@login_required
@permission_required("suppliers.add_supplier", raise_exception=True)
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur ajouté avec succès.")
            return redirect("suppliers:list")
    else:
        form = SupplierForm()
    return render(request, "suppliers/form.html", {"form": form})


@login_required
@permission_required("suppliers.change_supplier", raise_exception=True)
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur modifié avec succès.")
            return redirect("suppliers:list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "suppliers/form.html", {"form": form})


@login_required
@permission_required("suppliers.delete_supplier", raise_exception=True)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        messages.success(request, "Fournisseur supprimé avec succès.")
        return redirect("suppliers:list")
    return render(request, "suppliers/delete.html", {"supplier": supplier})

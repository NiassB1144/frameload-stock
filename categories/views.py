from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm
from .models import Category


@login_required
@permission_required("categories.view_category", raise_exception=True)
def category_list(request):
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        categories = categories.filter(name__icontains=query)
    return render(
        request,
        "categories/list.html",
        {"categories": categories, "query": query},
    )


@login_required
@permission_required("categories.add_category", raise_exception=True)
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès.")
            return redirect("categories:list")
    else:
        form = CategoryForm()
    return render(request, "categories/form.html", {"form": form})


@login_required
@permission_required("categories.change_category", raise_exception=True)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès.")
            return redirect("categories:list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "categories/form.html", {"form": form})


@login_required
@permission_required("categories.delete_category", raise_exception=True)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Catégorie supprimée avec succès.")
        return redirect("categories:list")
    return render(request, "categories/delete.html", {"category": category})

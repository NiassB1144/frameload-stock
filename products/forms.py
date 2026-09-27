from django import forms
from .models import Product
from config.forms import StyledModelForm

class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "supplier",
            "purchase_price",
            "selling_price",
            "stock_quantity",
            "minimum_stock",
        ]
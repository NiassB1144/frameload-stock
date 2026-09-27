
from django import forms
from .models import Sale, SaleItem
from config.forms import StyledModelForm


class SaleForm(StyledModelForm):
    class Meta:
        model = Sale
        fields = [
            "client_name",
            "client_phone",
        ]

        widgets = {
            "client_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nom du client",
            }),
            "client_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Téléphone du client",
            }),
        }


class SaleItemForm(StyledModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "La quantité doit être supérieure à 0.",
            "required": "La quantité est obligatoire.",
            "invalid": "Saisissez une quantité entière valide.",
        },
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": 1,
            "placeholder": "Ex : 2",
        }),
    )

    class Meta:
        model = SaleItem
        fields = [
            "product",
            "quantity",
        ]

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select",
            }),
        }

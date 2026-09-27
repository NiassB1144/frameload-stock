from django import forms
from .models import StockMovement
from config.forms import StyledModelForm


class StockMovementForm(StyledModelForm):
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
            "placeholder": "Ex : 10",
        }),
    )

    class Meta:
        model = StockMovement
        fields = [
            "product",
            "movement_type",
            "quantity",
            "reason",
        ]

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select",
            }),
            "movement_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "reason": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Réception fournisseur",
            }),
        }
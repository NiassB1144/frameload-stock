
from django import forms
from .models import Order, OrderItem
from config.forms import StyledModelForm


class OrderForm(StyledModelForm):

    class Meta:
        model = Order
        fields = [
            "client_name",
            "client_phone",
            "status",
        ]

        widgets = {
            "number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : CMD-001"
                }
            ),

            "client_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom du client"
                }
            ),

            "client_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Téléphone du client"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }


class OrderItemForm(StyledModelForm):
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
        model = OrderItem
        fields = ["product", "quantity"]

        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

        }

from django import forms
from .models import Supplier
from config.forms import StyledModelForm
# Creation du formulaire pour la creation de fournisseurs

class SupplierForm(StyledModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'company', 'email', 'phone', 'address']
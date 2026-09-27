# Creation du formulaire pour la creation de categories
from django import forms
from .models import Category
from config.forms import StyledModelForm

class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
from django import forms

from inventory.models import Category, ProductType, Stock, Warehouse


class CategoryCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'Category' instance, related to :model:`inventory.Category`
    """

    class Meta:
        model = Category
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def clean(self):
        name = self.cleaned_data.get("name")
        if Category.objects.filter(name=name).exists():
            self.add_error("name", "Ya existe una categoría con el nombre dado.")


class ProductTypeCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'ProductType' instance, related to :model:`inventory.ProductType`.
    """

    class Meta:
        model = ProductType
        fields = "__all__"
        widgets = {
            "cuenta": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "reference_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "data-bs-toggle": "tooltip",
                    "data-bs-placement": "bottom",
                    "data-bs-title": "Código único de indentificación del producto. Máximo 20 caracteres.",
                }
            ),
            "measurement_unit": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input align-text-bottom"}
            ),
        }


class WarehouseCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'Warehouse', related to :model:`inventory.Warehouse`.
    """

    class Meta:
        model = Warehouse
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "",
                }
            ),
            "location": forms.HiddenInput(),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Piso, número de departamento u otras aclaraciones.",
                }
            ),
        }


class StockCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'Stock' instance, related to :model:`inventory.Stock`.
    """

    class Meta:
        model = Stock
        fields = "__all__"
        widgets = {
            "cuenta": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "producttype": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "warehouse": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean(self):
        super().clean()
        producttype = self.cleaned_data.get("producttype")
        if not producttype.is_active:
            self.add_error("producttype", "El producto seleccionado no está activo.")

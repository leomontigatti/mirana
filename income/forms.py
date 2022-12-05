from django import forms

from income.models import Customer, Product, Receipt, Tax


class CustomerCreateForm(forms.ModelForm):
    """
    Form for creating or updating a customer, related to :model:`income.Customer`.
    """

    class Meta:
        model = Customer
        fields = "__all__"
        widgets = {
            "create_date": forms.DateInput(
                attrs={
                    "class": "form-control noinput",
                }
            ),
            "situacion_iva": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "identification_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "identification_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "data-bs-toggle": "tooltip",
                    "data-bs-placement": "bottom",
                    "data-bs-title": "8 números sin puntos para DNI, 11 números sin guiones para CUIT/CUIL",
                }
            ),
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
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "data-bs-toggle": "tooltip",
                    "data-bs-placement": "bottom",
                    "data-bs-title": "Código de area sin 0 y número sin 15.",
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
            "cuenta": forms.HiddenInput(),
        }


class ReceiptCreateForm(forms.ModelForm):
    """
    Form for creating or updating a receipt, related to :model:`income.Receipt`.
    """

    class Meta:
        model = Receipt
        fields: str = "__all__"
        widgets: dict = {
            "customer": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "issue_date": forms.DateInput(
                attrs={
                    "class": "form-control noinput",
                    "readonly": "",
                }
            ),
            "sale_term": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "due_date": forms.DateInput(
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
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "data-bs-toggle": "tooltip",
                    "data-bs-placement": "bottom",
                    "data-bs-title": "Código de area sin 0 y número sin 15.",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Piso, número de departamento u otras aclaraciones.",
                }
            ),
            "is_clean": forms.CheckboxInput(
                attrs={"class": "form-check-input align-text-bottom"}
            ),
            "is_placed": forms.CheckboxInput(
                attrs={"class": "form-check-input align-text-bottom"}
            ),
            "subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control text-center noinput",
                    "readonly": "",
                },
            ),
            "total": forms.NumberInput(
                attrs={
                    "class": "form-control text-center noinput",
                    "readonly": "",
                },
            ),
            "cai": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "product_type": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                },
            ),
            "unitario": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                },
            ),
            "subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control-plaintext rounded text-center",
                    "readonly": "",
                },
            ),
        }


ProductFormset = forms.inlineformset_factory(
    Receipt, Product, form=ProductForm, extra=0
)


class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = "__all__"
        widgets = {
            "tax_type": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control text-center tax noinput",
                    "readonly": "",
                },
            ),
        }


TaxFormset = forms.inlineformset_factory(Receipt, Tax, form=TaxForm, extra=2)

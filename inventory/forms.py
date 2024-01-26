from django import forms

from inventory.models import ServiceType, StockStatusChoices

PRODUCT_CHOICES = [
    ("BATHROOM", "Baño"),
    ("WORKSHOP", "Obrador"),
    ("TOILET_PAPER", "Papel higiénico"),
]


STOCK_STATUS = {
    "available": ("AVAILABLE", "Disponible"),
    "promised": ("PROMISED", "Prometido"),
    "placed": ("PLACED", "Colocado"),
    "maintenance": ("MAINTENANCE", "En mantenimiento"),
}


class ServiceTypeCreateForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = "__all__"


class StockCreateForm(forms.Form):
    product = forms.CharField(
        max_length=50,
        widget=forms.Select(
            attrs={
                "class": "form-select rounded-end",
            },
            choices=PRODUCT_CHOICES,
        ),
        label="Producto",
    )
    amount = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control rounded-end"},
        ),
        label="Cantidad",
    )
    password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(
            attrs={"class": "form-control rounded-end"},
        ),
        label="Contraseña",
    )


class StockAdjustmentForm(forms.Form):
    def __init__(self, *args, status, **kwargs):
        super().__init__(*args, **kwargs)
        current_status = STOCK_STATUS.get(status, None)
        choices = StockStatusChoices.choices
        choices.remove(current_status) if current_status in choices else None
        self.fields["status"].widget.choices = choices

    move_amount = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control rounded-end"},
        ),
        label="Cantidad",
    )
    status = forms.CharField(
        max_length=50,
        widget=forms.Select(
            attrs={"class": "form-select rounded-end"},
        ),
        label="Estado",
    )
    reason = forms.CharField(
        max_length=300,
        widget=forms.Textarea(
            {
                "class": "form-control rounded-end",
                "rows": "3",
                "placeholder": "Para modificar el stock de un producto es necesario ingresar un motivo y volver a identificarse.",
            }
        ),
        label="Motivo",
    )
    password = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(
            attrs={"class": "form-control rounded-end"},
        ),
        label="Contraseña",
    )

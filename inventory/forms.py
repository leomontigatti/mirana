from django import forms

from inventory.models import ServiceType, Stock, Warehouse


class ServiceTypeCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'ServiceType' instance, related to :model:`inventory.ServiceType`.
    """

    class Meta:
        model = ServiceType
        fields = "__all__"


class WarehouseCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'Warehouse', related to :model:`inventory.Warehouse`.
    """

    class Meta:
        model = Warehouse
        fields = "__all__"


class StockCreateForm(forms.ModelForm):
    """
    Form for creating or updating a 'Stock' instance, related to :model:`inventory.Stock`.
    """

    class Meta:
        model = Stock
        fields = "__all__"

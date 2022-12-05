from django import forms

from accounting.models import Cuenta, Rubro, Subrubro, TaxType


class RubroCreateForm(forms.ModelForm):
    """
    Form for creating or updating a rubro, related to :model:`accounting.Rubro`.
    """

    class Meta:
        model = Rubro
        fields = "__all__"


class SubrubroCreateForm(forms.ModelForm):
    """
    Form for creating or updating a subrubro, related to :model:`accounting.Subrubro`.
    """

    class Meta:
        model = Subrubro
        fields = "__all__"


class CuentaCreateForm(forms.ModelForm):
    """
    Form for creating or updating a sub-rubro, related to :model:`accounting.Cuenta`.
    """

    class Meta:
        model = Cuenta
        fields = ("subrubro", "name")


class TaxTypeCreateForm(forms.ModelForm):
    """
    Form for creating or updating a Tax type, related to :model:`accounting.TaxType`.
    """

    class Meta:
        model = TaxType
        fields = ("name", "percentage")

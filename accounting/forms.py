from django import forms

from accounting.models import Asiento, Cuenta, Entry, TaxType


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
        fields = "__all__"


class EntryCreateForm(forms.ModelForm):
    """
    Form for creating an asiento entry, related to :model:`accounting.Entry`.
    """

    class Meta:
        model = Entry
        exclude = "__all__"

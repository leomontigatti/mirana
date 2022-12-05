from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView

from accounting.forms import (
    CuentaCreateForm,
    RubroCreateForm,
    SubrubroCreateForm,
    TaxTypeCreateForm,
)
from accounting.models import CapituloChoices, Cuenta, Rubro, Subrubro, TaxType
from main.views import CustomContextMixin


class CustomSuccessMessageMixin(SuccessMessageMixin):
    MODEL_LABELS = {
        "create": {
            "rubro": "Rubro creado con éxito!",
            "subrubro": "Subrubro creado con éxito!",
            "cuenta": "Cuenta creada con éxito!",
            "taxtype": "Tipo de impuesto creado con éxito!",
        },
        "update": {
            "customer": "Cliente modificado con éxito!",
            "budget": "Presupuesto modificado con éxito!",
            "hiring": "Contratación modificada con éxito!",
            "invoice": "Factura modificada con éxito!",
        },
        "delete": {
            "customer": "Cliente eliminado con éxito!",
            "budget": "Presupuesto eliminado con éxito!",
            "hiring": "Contratación eliminada con éxito!",
            "invoice": "Factura eliminada con éxito!",
        },
    }


# region Rubro


class RubroCreateView(CreateView):
    model = Rubro
    form_class = RubroCreateForm


# endregion
# region SubRubro


class SubrubroCreateView(CreateView):
    model = Subrubro
    form_class = SubrubroCreateForm


# endregion
# region Cuenta


class CuentaListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`accounting.Cuenta` instances.
    **Context:**
    ``cuenta_list``
        A list of :model:`income.Customer` instances.
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`accounting/cuenta_list.html`
    """

    model = Cuenta

    def get_context_data(self, **kwargs):
        extra_context = {
            "capitulos_list": CapituloChoices.labels,
            "rubros_list": Rubro.objects.all(),
            "subrubros_list": Subrubro.objects.all(),
        }

        return {**super().get_context_data(**kwargs), **extra_context}


class CuentaCreateView(CreateView):
    """
    Display a form for creating a :model:`accounting.Cuenta` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`accounting/cuenta_form.html`.
    """

    model = Cuenta
    form_class = CuentaCreateForm


# endregion
# region TaxType


class TaxTypeListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`accounting.TaxType` instances.
    **Context:**
    ``taxtype_list``
        A list of :model:`income.Customer` instances.
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`accounting/taxtype_list.html`
    """

    model = TaxType


class TaxTypeCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`accounting.TaxType` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`accounting/taxtype_form.html`.
    """

    model = TaxType
    form_class = TaxTypeCreateForm


# endregion

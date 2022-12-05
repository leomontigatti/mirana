from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

from accounting.models import Cuenta
from income.forms import (
    CustomerCreateForm,
    ProductFormset,
    ReceiptCreateForm,
    TaxFormset,
)
from income.models import Customer, Receipt
from main.models import IdentificationTypeChoices, SituacionIvaChoices
from main.views import CustomContextMixin


class CustomSuccessMessageMixin(SuccessMessageMixin):
    MODEL_LABELS = {
        "create": {
            "customer": "Cliente creado con éxito!",
            "budget": "Presupuesto creado con éxito!",
            "hiring": "Contratación creada con éxito!",
            "invoice": "Factura creada con éxito!",
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

    def get_success_url(self):
        request_path = self.request.path.strip("/").split("/")
        if request_path[1] == "delete":
            return redirect(f"{request_path[0]}_list")
        return reverse(f"{request_path[0]}_list")

    def get_success_message(self, cleaned_data):
        request_path = self.request.path.strip("/").split("/")
        return self.MODEL_LABELS.get(request_path[1]).get(request_path[0])


# region Customer


class CustomerListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`income.Customer` instances and a GET method search.
    **Context:**
    ``customer_list``
        A list of :model:`income.Customer` instances.
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`income/customer_list.html`
    """

    model = Customer

    def get_queryset(self):
        search_input = self.request.GET.get("search_input")
        if search_input:
            return Customer.objects.filter(
                Q(name__icontains=search_input)
                | Q(identification_number__icontains=search_input)
                | Q(address__icontains=search_input)
            )
        filter_kwargs = {key: value for key, value in self.request.GET.items() if value}
        return Customer.objects.filter(**filter_kwargs)

    def get_context_data(self, **kwargs):
        search_input = self.request.GET.get("search_input")
        filter_options = {
            "situacion_iva": SituacionIvaChoices.choices,
            "identification_type": IdentificationTypeChoices.choices,
        }
        extra_context = {
            "search_text": "Buscar por nombre, número de ID o domicilio.",
            "search_input": search_input if search_input else "",
            "filter_options": filter_options,
        }
        return {**super().get_context_data(**kwargs), **extra_context}


class CustomerCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`income.Customer` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`income/customer_form.html`.
    """

    model = Customer
    form_class = CustomerCreateForm

    def form_valid(self, form):
        cuenta = Cuenta.objects.create(
            subrubro_id=7, name=form.cleaned_data.get("name")
        )
        form.instance.cuenta = cuenta
        return super().form_valid(form)


class CustomerUpdateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, UpdateView
):
    """
    Display a form for editing a :model:`income.Customer` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`income/customer_form.html`.
    """

    model = Customer
    form_class = CustomerCreateForm


# endregion
# region Receipt


class ReceiptListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`income.Receipt` instances and a GET method search.
    **Context:**
    ``receipt_list``
        A list of :model:`income.Receipt` instances
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`receipt_list.html`
    """

    model = Receipt

    def get_queryset(self):
        receipt_type = self.request.path.strip("/").split("/")[0].upper()
        search_input = self.request.GET.get("search_input")
        if search_input:
            return Receipt.objects.filter(receipt_type=receipt_type).filter(
                Q(customer__name__icontains=search_input)
                | Q(id__icontains=search_input)
                | Q(address__icontains=search_input)
            )
        return Receipt.objects.filter(receipt_type=receipt_type)

    def get_context_data(self, **kwargs):
        search_input = self.request.GET.get("search_input")
        extra_context = {
            "search_text": "Buscar por número, cliente o domicilio.",
            "search_input": search_input if search_input else "",
        }
        return {**super().get_context_data(**kwargs), **extra_context}


class ReceiptCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`income.Receipt` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    ``product_formset``
        Formset for creating products related to current receipt.
    ``tax_formset``
        Formset for creating taxes related to current receipt.
    **Template:**
    :template:`income/receipt_form.html`.
    """

    model = Receipt
    form_class = ReceiptCreateForm

    def get_context_data(self, **kwargs):
        request_path = self.request.path.strip("/").split("/")
        receipt_id = self.request.GET.get("receipt")
        receipt = Receipt.objects.get(pk=receipt_id) if receipt_id else self.object

        receipt_lookup = {
            "budget": {
                "receipt_type": None,
                "receipt_list": None,
            },
            "hiring": {
                "receipt_type": "BUDGET",
                "receipt_list": Receipt.objects.filter(
                    receipt_type="BUDGET",
                    has_hiring__isnull=True,
                ),
            },
            "invoice": {
                "receipt_type": "HIRING",
                "receipt_list": Receipt.objects.filter(
                    receipt_type="HIRING",
                    has_invoice__isnull=True,
                ),
            },
        }

        extra_context = {
            "receipt_type": receipt_lookup.get(request_path[0]).get("receipt_type"),
            "receipt_list": receipt_lookup.get(request_path[0]).get("receipt_list"),
            "product_formset": ProductFormset(instance=receipt),
            "tax_formset": TaxFormset(instance=receipt),
        }

        if self.request.POST:
            extra_context["product_formset"] = ProductFormset(
                self.request.POST, instance=receipt
            )
            extra_context["tax_formset"] = TaxFormset(
                self.request.POST, instance=receipt
            )

        return {**super().get_context_data(**kwargs), **extra_context}

    def get_initial(self):
        receipt_id = self.request.GET.get("receipt")
        if receipt_id:
            receipt = Receipt.objects.get(pk=receipt_id)
            return {
                "customer": receipt.customer,
                "has_invoice": receipt.has_invoice,
                "has_hiring": receipt.has_hiring,
                "address": receipt.address,
                "location": receipt.location,
                "phone_number": receipt.phone_number,
                "notes": receipt.notes,
                "subtotal": receipt.subtotal,
                "total": receipt.total,
            }

    def form_valid(self, form):
        request_path = self.request.path.strip("/").split("/")
        receipt_type = request_path[0]
        form.instance.receipt_type = receipt_type.upper()
        context = self.get_context_data()
        receipt = form.save()

        # Increase customer's cuenta debe.
        if receipt_type == "invoice":
            receipt.customer.cuenta.aumenta_debe(receipt.total)

        product_formset = context.get("product_formset")
        if product_formset.is_valid():
            product_formset.instance = receipt
            product_formset.save()

        tax_formset = context.get("tax_formset")
        if tax_formset.is_valid():
            tax_formset.instance = receipt
            tax_formset.save()

        # Set current receipt has_hiring or has_invoice attribute.
        if self.request.GET.get("receipt"):
            if receipt_type == "hiring":
                budget = Receipt.objects.get(pk=self.request.GET.get("receipt"))
                budget.has_hiring = receipt
                budget.save()
            elif receipt_type == "invoice":
                hiring = Receipt.objects.get(pk=self.request.GET.get("receipt"))
                hiring.has_invoice = receipt
                hiring.save()

        return super().form_valid(form)


class ReceiptUpdateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, UpdateView
):
    """
    Display a form for editing a :model:`income.Receipt` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    ``product_formset``
        Formset for creating products related to current receipt.
    ``tax_formset``
        Formset for creating taxes related to current receipt.
    **Template:**
    :template:`income/receipt_form.html`.
    """

    model = Receipt
    form_class = ReceiptCreateForm

    def get_context_data(self, **kwargs):
        receipt = self.object
        extra_context = {
            "product_formset": ProductFormset(instance=receipt),
            "tax_formset": TaxFormset(instance=receipt),
        }

        if self.request.POST:
            extra_context["product_formset"] = ProductFormset(
                self.request.POST, instance=receipt
            )
            extra_context["tax_formset"] = TaxFormset(
                self.request.POST, instance=receipt
            )

        return {**super().get_context_data(**kwargs), **extra_context}

    def form_valid(self, form):
        context = self.get_context_data()
        receipt = form.save()

        product_formset = context.get("product_formset")
        if product_formset.is_valid():
            product_formset.instance = receipt
            product_formset.save()

        tax_formset = context.get("tax_formset")
        if tax_formset.is_valid():
            tax_formset.instance = receipt
            tax_formset.save()

        return super().form_valid(form)


class ReceiptDeleteView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, DeleteView
):
    """
    Display a form for deleting a :model:`income.Receipt` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`income/receipt_form.html`.
    """

    model = Receipt


# endregion

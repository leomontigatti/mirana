from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from inventory.forms import (
    CategoryCreateForm,
    ProductTypeCreateForm,
    StockCreateForm,
    WarehouseCreateForm,
)
from inventory.models import Category, ProductType, Stock, Warehouse
from main.views import CustomContextMixin


class CustomSuccessMessageMixin(SuccessMessageMixin):
    MODEL_LABELS = {
        "create": {
            "producttype": "Producto creado con éxito!",
            "category": "Categoría creada con éxito!",
            "warehouse": "Depósito creado con éxito!",
            "stock": "Stock creado con éxito!",
        },
        "update": {
            "producttype": "Product modificado con éxito!",
            "warehouse": "Depósito modificado con éxito!",
            "stock": "Stock modificado con éxito!",
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


# region Category


class CategoryCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`inventory.Category` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/category_form.html`.
    """

    model = Category
    form_class = CategoryCreateForm

    def form_invalid(self, form):
        messages.warning(
            self.request, "Ya existe una categoría con el nombre ingresado."
        )
        return redirect("producttype_create")

    def get_success_url(self):
        return reverse("producttype_create", kwargs={"category": self.object.id})


# endregion
# region ProductType


class ProductTypeListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`inventory.ProductType` and a GET method search.
    **Context:**
    ``object_list``
        A list of :model:`inventory.ProductType` instances
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/producttype_list.html`
    """

    model = ProductType

    def get_queryset(self):
        search_input = self.request.GET.get("search_input")
        if search_input:
            return ProductType.objects.filter(
                Q(name__icontains=search_input)
                | Q(reference_code__icontains=search_input)
            )
        return ProductType.objects.all()

    def get_context_data(self, **kwargs) -> dict:
        search_input = self.request.GET.get("search_input")
        extra_context = {
            "search_text": "Buscar por nombre o código de referencia.",
            "search_input": search_input if search_input else "",
        }
        return {**super().get_context_data(**kwargs), **extra_context}


class ProductTypeCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`inventory.ProductType` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/producttype_form.html`.
    """

    model = ProductType
    form_class = ProductTypeCreateForm

    def get_context_data(self, **kwargs):
        extra_context = {
            "category_form": CategoryCreateForm,
        }
        return {**super().get_context_data(**kwargs), **extra_context}

    def get_initial(self):
        category_id = self.kwargs.get("category")
        category = Category.objects.get(pk=category_id) if category_id else ""
        if category_id:
            return {
                "category": category,
            }


class ProductTypeUpdateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, UpdateView
):
    """
    Display a form for editing a :model:`inventory.ProductType` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/producttype_form.html`.
    """

    model = ProductType
    form_class = ProductTypeCreateForm


# endregion
# region Warehouse


class WarehouseListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`inventory.Warehouse`.
    **Context:**
    ``object_list``
        A list of :model:`inventory.Warehouse` instances
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/warehouse_list.html`
    """

    model = Warehouse

    def get_queryset(self):
        search_input = self.request.GET.get("search_input")
        if search_input:
            return Warehouse.objects.filter(
                Q(name__icontains=search_input) | Q(address__icontains=search_input)
            )
        return Warehouse.objects.all()

    def get_context_data(self, **kwargs):
        search_input = self.request.GET.get("search_input")
        extra_context = {
            "search_text": "Buscar por nombre o domicilio.",
            "search_input": search_input if search_input else "",
        }
        return {**super().get_context_data(**kwargs), **extra_context}


class WarehouseCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`inventory.Warehouse` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/warehouse_form.html`.
    """

    model = Warehouse
    form_class = WarehouseCreateForm


class WarehouseUpdateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, UpdateView
):
    """
    Display a form for editing a :model:`inventory.Warehouse` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/warehouse_form.html`.
    """

    model = Warehouse
    form_class = WarehouseCreateForm


# endregion
# region Stock


class StockListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """
    Display a list of :model:`inventory.Stock` and a GET method search.
    **Context:**
    ``object_list``
        A list of :model:`inventory.Stock` instances
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    ``search_text``
        A string for rendering inside search input box.
    ``search_input``
        The value of search input box if any.
    ``filter_options``
        A dictionary containing filter kwarg and queryset.
    **Template:**
    :template:`inventory/stock_list.html`
    """

    model = Stock

    def get_queryset(self):
        search_input = self.request.GET.get("search_input")
        if search_input:
            return Stock.objects.filter(
                Q(producttype__name__icontains=search_input)
                | Q(producttype__reference_code__icontains=search_input)
            )

        filter_kwargs = {key: value for key, value in self.request.GET.items() if value}
        return Stock.objects.filter(**filter_kwargs)

    def get_context_data(self, **kwargs):
        search_input = self.request.GET.get("search_input")
        filter_options = {
            "producttype": ProductType.objects.filter(is_active=True),
            "producttype__category": Category.objects.all(),
            "warehouse": Warehouse.objects.all(),
        }
        extra_context = {
            "search_text": "Buscar por nombre o código de referencia del producto.",
            "search_input": search_input if search_input else "",
            "filter_options": filter_options,
        }
        return {**super().get_context_data(**kwargs), **extra_context}


class StockCreateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, CreateView
):
    """
    Display a form for creating a :model:`inventory.Stock` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/stock_form.html`.
    """

    model = Stock
    form_class = StockCreateForm

    def form_valid(self, form):
        """
        If an instance of :model:`inventory.Stock` is already created, the amount is updated.
        """
        producttype = form.cleaned_data.get("producttype")
        warehouse = form.cleaned_data.get("warehouse")
        amount = form.cleaned_data.get("amount")
        try:
            stock = Stock.objects.get(producttype=producttype, warehouse=warehouse)
            stock.amount += amount
            stock.save()
            return redirect(self.get_success_url())
        except ObjectDoesNotExist:
            return super().form_valid(form)


class StockUpdateView(
    LoginRequiredMixin, CustomContextMixin, CustomSuccessMessageMixin, UpdateView
):
    """
    Display a form for editing a :model:`inventory.Stock` instance.
    **Context:**
    ``app``
        A string to set template's title and navbar's active tab.
    ``page``
        A string to set card's active tab.
    ``model``
        Current view's model to set template url's names.
    **Template:**
    :template:`inventory/stock_form.html`.
    """

    model = Stock
    form_class = StockCreateForm


# endregion

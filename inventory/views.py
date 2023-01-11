from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from inventory.forms import ServiceTypeCreateForm, StockCreateForm, WarehouseCreateForm
from inventory.models import ServiceType, Stock, Warehouse


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    context = {
        "app": "inventory",
        "page": request_path[1],
        "model": request_path[0],
    }
    return context


# region Category


# class CategoryCreateView(CustomContextMixin, CustomSuccessMessageMixin, CreateView):
#     """
#     Display a form for creating a :model:`inventory.Category` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`inventory/category_form.html`.
#     """

#     model = Category
#     form_class = CategoryCreateForm

#     def form_invalid(self, form):
#         messages.warning(
#             self.request, "Ya existe una categoría con el nombre ingresado."
#         )
#         return redirect("product_type_create")

#     def get_success_url(self):
#         return reverse("product_type_create", kwargs={"category": self.object.id})


# endregion
# region ServiceType


@login_required
def service_type_index_view(request):
    context = get_context_data(request)
    # context["filter_options"] = {
    #     "is_active": (("true", "Activo"), ("false", "No Activo")),
    # }
    return render(request, "index.html", context)


@login_required
def service_type_list_view(request):
    queryset = ServiceType.objects.all()
    context = {
        "service_type_list": queryset,
    }
    return render(request, "inventory/service_type_list.html", context)


@login_required
def service_type_create_view(request):
    form = ServiceTypeCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio creado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "service_typeListChanged"}
            )
    return render(request, "inventory/service_type_form.html", context)


@login_required
def service_type_update_view(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)
    form = ServiceTypeCreateForm(request.POST or None, instance=service_type)
    context = {
        "service_type": service_type,
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio modificado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "service_typeListChanged"}
            )
    return render(request, "inventory/service_type_form.html", context)


@login_required
def service_type_delete_view(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)
    context = get_context_data(request)
    context["object"] = service_type
    if request.method == "POST":
        try:
            service_type.delete()
            messages.success(request, "Servicio eliminado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "service_typeListChanged"}
            )
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el servicio porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# class ProductTypeListView(CustomContextMixin, ListView):
#     """
#     Display a list of :model:`inventory.ProductType` and a GET method search.
#     **Context:**
#     ``object_list``
#         A list of :model:`inventory.ProductType` instances
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`inventory/product_type_list.html`
#     """

#     model = ProductType
#     template_name = "inventory/product_type_list.html"

#     def get_queryset(self):
#         search_input = self.request.GET.get("search_input")
#         if search_input:
#             return ProductType.objects.filter(
#                 Q(name__icontains=search_input)
#                 | Q(reference_code__icontains=search_input)
#             )

#         filter_kwargs = {key: value for key, value in self.request.GET.items() if value}
#         return ProductType.objects.filter(**filter_kwargs)

#     def get_context_data(self, **kwargs) -> dict:
#         search_input = self.request.GET.get("search_input")
#         filter_options = {
#             "type_select": TypeSelectChoices.choices,
#         }
#         extra_context = {
#             "search_text": "Buscar por nombre o código de referencia.",
#             "search_input": search_input if search_input else "",
#             "filter_options": filter_options,
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}


# class ProductTypeCreateView(CustomContextMixin, CustomSuccessMessageMixin, CreateView):
#     """
#     Display a form for creating a :model:`inventory.ProductType` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`inventory/product_type_form.html`.
#     """

#     model = ProductType
#     form_class = ProductTypeCreateForm
#     template_name = "inventory/product_type_form.html"

#     def get_context_data(self, **kwargs):
#         extra_context = {
#             "category_form": CategoryCreateForm,
#             "cuenta_form": CuentaCreateForm,
#             # "task_type_form": TaskTypeCreateForm,
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}

#     def get_initial(self):
#         category_id = self.kwargs.get("category")
#         category = Category.objects.get(pk=category_id) if category_id else ""
#         if category_id:
#             return {
#                 "category": category,
#             }

#     def form_valid(self, form):
#         type_select = self.request.POST.get("type-select")
#         if not type_select:
#             form.add_error("type_select", "Se debe seleccionar si se está cargando un producto o un servicio.")
#             return self.form_invalid(form)
#         form.instance.type_select = type_select

#         if type_select == "SERVICE":
#             form.instance.task_type = form.cleaned_data.get("task_type")
#             form.instance.stock_cuenta = None
#             form.instance.amount = None
#         elif type_select == "PRODUCT":
#             form.instance.task_type = None
#             form.instance.stock_cuenta = form.cleaned_data.get("stock_cuenta")
#             form.instance.amount = form.cleaned_data.get("amount") or 0

#         return super().form_valid(form)


# class ProductTypeUpdateView(CustomContextMixin, CustomSuccessMessageMixin, UpdateView):
#     """
#     Display a form for editing a :model:`inventory.ProductType` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`inventory/product_type_form.html`.
#     """

#     model = ProductType
#     form_class = ProductTypeCreateForm
#     template_name = "inventory/product_type_form.html"

#     def get_context_data(self, **kwargs):
#         extra_context = {
#             "cuenta_form": CuentaCreateForm,
#             # "task_type_form": TaskTypeCreateForm,
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}

#     def form_valid(self, form):
#         type_select = self.request.POST.get("type-select")
#         if not type_select:
#             form.add_error("type_select", "Se debe seleccionar si se está cargando un producto o un servicio.")
#             return self.form_invalid(form)
#         form.instance.type_select = type_select

#         if type_select == "SERVICE":
#             form.instance.task_type = form.cleaned_data.get("task_type")
#             form.instance.stock_cuenta = None
#             form.instance.amount = None
#         elif type_select == "PRODUCT":
#             form.instance.task_type = None
#             form.instance.stock_cuenta = form.cleaned_data.get("stock_cuenta")
#             form.instance.amount = form.cleaned_data.get("amount") or 0

#         return super().form_valid(form)


# endregion
# region Warehouse


@login_required
def warehouse_index_view(request):
    context = get_context_data(request)
    return render(request, "index.html", context)


@login_required
def warehouse_list_view(request):
    queryset = Warehouse.objects.all()
    context = {
        "warehouse_list": queryset,
    }
    return render(request, "inventory/warehouse_list.html", context)


@login_required
def warehouse_create_view(request):
    form = WarehouseCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Depósito creado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "warehouseListChanged"}
            )
    return render(request, "inventory/warehouse_form.html", context)


@login_required
def warehouse_update_view(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    form = WarehouseCreateForm(request.POST or None, instance=warehouse)
    context = {
        "warehouse": warehouse,
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Depósito modificado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "warehouseListChanged"}
            )
    return render(request, "inventory/warehouse_form.html", context)


@login_required
def warehouse_delete_view(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    context = get_context_data(request)
    context["object"] = warehouse
    if request.method == "POST":
        try:
            warehouse.delete()
            messages.success(request, "Depósito eliminado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "warehouseListChanged"}
            )
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el depósito porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# endregion
# region Stock


@login_required
def stock_index_view(request):
    context = get_context_data(request)
    return render(request, "index.html", context)


@login_required
def stock_list_view(request):
    queryset = Stock.objects.all()
    context = {
        "stock_list": queryset,
    }
    return render(request, "inventory/stock_list.html", context)


@login_required
def stock_create_view(request):
    form = StockCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Stock creado con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "stockListChanged"})
    return render(request, "inventory/stock_form.html", context)


@login_required
def stock_update_view(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    form = StockCreateForm(request.POST or None, instance=stock)
    context = {
        "stock": stock,
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Stock modificado con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "stockListChanged"})
    return render(request, "inventory/stock_form.html", context)


@login_required
def stock_delete_view(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    context = get_context_data(request)
    context["object"] = stock
    if request.method == "POST":
        try:
            stock.delete()
            messages.success(request, "Stock eliminado con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "stockListChanged"})
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el stock porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# class StockListView(CustomContextMixin, ListView):
#     """
#     Display a list of :model:`inventory.Stock` and a GET method search.
#     **Context:**
#     ``object_list``
#         A list of :model:`inventory.Stock` instances
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     ``search_text``
#         A string for rendering inside search input box.
#     ``search_input``
#         The value of search input box if any.
#     ``filter_options``
#         A dictionary containing filter kwarg and queryset.
#     **Template:**
#     :template:`inventory/stock_list.html`
#     """

#     model = Stock

#     def get_queryset(self):
#         search_input = self.request.GET.get("search_input")
#         if search_input:
#             return Stock.objects.filter(
#                 Q(product_type__name__icontains=search_input)
#                 | Q(product_type__reference_code__icontains=search_input)
#             )

#         filter_kwargs = {key: value for key, value in self.request.GET.items() if value}
#         return Stock.objects.filter(**filter_kwargs)

#     def get_context_data(self, **kwargs):
#         search_input = self.request.GET.get("search_input")
#         filter_options = {
#             "product_type": ProductType.objects.filter(is_active=True),
#             "product_type__category": Category.objects.all(),
#             "warehouse": Warehouse.objects.all(),
#         }
#         extra_context = {
#             "search_text": "Buscar por nombre o código de referencia del producto.",
#             "search_input": search_input if search_input else "",
#             "filter_options": filter_options,
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}


# class StockCreateView(CustomContextMixin, CustomSuccessMessageMixin, CreateView):
#     """
#     Display a form for creating a :model:`inventory.Stock` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`inventory/stock_form.html`.
#     """

#     model = Stock
#     form_class = StockCreateForm

#     def form_valid(self, form):
#         """
#         If an instance of :model:`inventory.Stock` is already created, the amount is updated.
#         """
#         product_type = form.cleaned_data.get("product_type")
#         warehouse = form.cleaned_data.get("warehouse")
#         amount = form.cleaned_data.get("amount")
#         try:
#             stock = Stock.objects.get(product_type=product_type, warehouse=warehouse)
#             stock.amount += amount
#             stock.save()
#             return redirect(self.get_success_url())
#         except ObjectDoesNotExist:
#             return super().form_valid(form)


# class StockUpdateView(CustomContextMixin, CustomSuccessMessageMixin, UpdateView):
#     """
#     Display a form for editing a :model:`inventory.Stock` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`inventory/stock_form.html`.
#     """

#     model = Stock
#     form_class = StockCreateForm


# endregion

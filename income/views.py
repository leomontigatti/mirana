from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounting.models import Asiento, Cuenta, Entry
from configuration.models import Task
from income.forms import (
    BudgetCreateForm,
    CustomerCreateForm,
    HiringCreateForm,
    IncomePaymentCreateForm,
    ServiceCreateForm,
    TaxCreateForm,
)
from income.models import Budget, Customer, Hiring, IncomePayment, Service, Tax
from main.models import IdentificationTypeChoices, IvaSituationChoices, is_operator


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    context = {
        "app": "income",
        "page": request_path[1],
        "model": request_path[0],
    }
    return context


def handle_formsets(request, instance):
    service_type = request.POST.getlist("service_type")
    amount = request.POST.getlist("amount")
    unitario = request.POST.getlist("unitario")
    service_subtotal = request.POST.getlist("service_subtotal")
    service_lookup_dict = {}
    for a, b, c, d in zip(service_type, amount, unitario, service_subtotal):
        service_lookup_dict["service_type_id"] = a
        service_lookup_dict[instance._meta.model_name] = instance
        Service.objects.update_or_create(
            **service_lookup_dict,
            defaults={"amount": b, "unitario": c, "service_subtotal": d}
        )
    tax_type = request.POST.getlist("tax_type")
    tax_subtotal = request.POST.getlist("tax_subtotal")
    tax_lookup_dict = {}
    for (
        e,
        f,
    ) in zip(tax_type, tax_subtotal):
        tax_lookup_dict["tax_type_id"] = e
        tax_lookup_dict[instance._meta.model_name] = instance
        Tax.objects.update_or_create(**tax_lookup_dict, defaults={"tax_subtotal": f})


def handle_task_formset(request, instance):
    description = request.POST.getlist("description")
    frequency = request.POST.getlist("frequency")
    operator = request.POST.getlist("operator")
    priority = request.POST.getlist("priority")
    task_lookup_dict = {}
    for a, b, c, d in zip(description, frequency, operator, priority):
        task_lookup_dict["description"] = a
        task_lookup_dict[instance._meta.model_name] = instance
        Task.objects.update_or_create(
            **task_lookup_dict,
            defaults={
                "frequency": b,
                "operator_id": c,
                "priority": d,
                "task_start_date": instance.start_date,
                "task_end_date": instance.end_date,
            }
        )


# region Customer


@login_required
def customer_index_view(request):
    context = get_context_data(request)
    context["search_text"] = "Buscar por nombre, número de ID o domicilio."
    return render(request, "index.html", context)


@login_required
def customer_list_view(request):
    queryset = Customer.objects.all()
    context = {
        "customer_list": queryset,
    }
    return render(request, "income/customer_list.html", context)


@login_required
def customer_create_view(request):
    form = CustomerCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                cuenta_activo = Cuenta.objects.create(
                    subrubro_id=7, name=form.cleaned_data.get("name")
                )
                form.instance.cuenta_activo = cuenta_activo
                cuenta_pasivo = Cuenta.objects.create(
                    subrubro_id=16, name=form.cleaned_data.get("name")
                )
                form.instance.cuenta_pasivo = cuenta_pasivo
                form.save()
                messages.success(request, "Cliente creado con éxito!")
                if any(
                    receipt in request.path
                    for receipt in ["budget", "hiring", "invoice"]
                ):
                    return HttpResponse(
                        status=204, headers={"HX-Trigger": "customerSelectChanged"}
                    )
                return HttpResponse(
                    status=204, headers={"HX-Trigger": "customerListChanged"}
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    messages.error(
                        request,
                        "Ya existe un cliente con el tipo y número de identificación ingresados.",
                    )
                    return HttpResponse(status=204)
    return render(request, "income/customer_form.html", context)


@login_required
def customer_update_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerCreateForm(request.POST or None, instance=customer)
    context = {
        "customer": customer,
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cliente modificado con éxito!")
                return HttpResponse(
                    status=204, headers={"HX-Trigger": "customerListChanged"}
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    messages.error(
                        request,
                        "Ya existe un cliente con el tipo y número de identificación ingresados.",
                    )
                    return HttpResponse(status=204)
    return render(request, "income/customer_form.html", context)


@login_required
def customer_delete_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    context = get_context_data(request)
    context["object"] = customer
    if request.method == "POST":
        try:
            customer.delete()
            messages.success(request, "Cliente eliminado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "customerListChanged"}
            )
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el cliente porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# endregion
# region Budget


@login_required
def budget_index_view(request):
    context = get_context_data(request)
    context["search_text"] = "Buscar por número, cliente o domicilio."
    return render(request, "index.html", context)


@login_required
def budget_list_view(request):
    context = get_context_data(request)
    queryset = Budget.objects.all()
    context["object_list"] = queryset
    return render(request, "income/receipt_list.html", context)


@login_required
def budget_update_or_create_view(request, pk=None):
    context = get_context_data(request)
    if pk:
        budget = Budget.objects.get(pk=pk)
        context["object"] = budget
    return render(request, "income/receipt_update_or_create.html", context)


@login_required
def budget_create_form_view(request):
    context = get_context_data(request)
    form = BudgetCreateForm(
        request.POST or None,
        initial={
            "notes": "El presente presupuesto tiene una validez de quince (15) días a partir de su fecha de emisión."
        },
    )
    context["form"] = form
    if request.method == "POST":
        if form.is_valid():
            instance = form.save()
            handle_formsets(request, instance)
            messages.success(request, "Presupuesto creado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Redirect": reverse("budget_index")}
            )
    return render(request, "income/receipt_form.html", context)


@login_required
def budget_update_form_view(request, pk=None):
    context = get_context_data(request)
    budget = get_object_or_404(Budget, pk=pk)
    context["object"] = budget
    form = BudgetCreateForm(request.POST or None, instance=budget)
    context["form"] = form
    service_list = Service.objects.filter(budget=budget)
    context["service_list"] = service_list
    tax_list = Tax.objects.filter(budget=budget)
    context["tax_list"] = tax_list
    if request.method == "POST":
        if form.is_valid():
            instance = form.save()
            handle_formsets(request, instance)
            messages.success(request, "Presupuesto modificado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Location": reverse("budget_index")}
            )
    return render(request, "income/receipt_form.html", context)


@login_required
def budget_delete_view(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    context = get_context_data(request)
    context["object"] = budget
    if request.method == "POST":
        try:
            budget.delete()
            messages.success(request, "Presupuesto eliminado con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "budgetListChanged"})
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el presupuesto porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# endregion
# region Hiring


@login_required
def hiring_index_view(request):
    context = get_context_data(request)
    context["search_text"] = "Buscar por número, cliente o domicilio."
    return render(request, "index.html", context)


@login_required
def hiring_list_view(request):
    context = get_context_data(request)
    queryset = Hiring.objects.all()
    context["object_list"] = queryset
    return render(request, "income/receipt_list.html", context)


@login_required
def hiring_update_or_create_view(request, pk=None):
    context = get_context_data(request)
    if pk:
        hiring = Hiring.objects.get(pk=pk)
        context["object"] = hiring
    return render(request, "income/receipt_update_or_create.html", context)


@login_required
def hiring_create_form_view(request):
    context = get_context_data(request)
    form = HiringCreateForm(request.POST or None)
    context["form"] = form
    budget_id = request.GET.get(
        "budget"
    )  # Hacer que el formulario cambie cuando cambia el select con HTMX
    if budget_id:
        budget = get_object_or_404(Budget, pk=budget_id)
        initialized_form = HiringCreateForm(
            initial={
                "customer": budget.customer,
                "address": budget.address,
                "location": budget.location,
                "phone_number": budget.phone_number,
                "notes": budget.notes,
                "budget": budget,
            }
        )
        context["form"] = initialized_form
        service_list = Service.objects.filter(budget=budget)
        task_list = [
            Task.objects.create(description=service.service_type)
            for service in service_list
        ]
        context["task_list"] = task_list
    if request.method == "POST":
        if form.is_valid():
            instance = form.save()
            handle_task_formset(request, instance)
            messages.success(request, "Contratación creada con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Redirect": reverse("hiring_index")}
            )
    return render(request, "income/receipt_form.html", context)


@login_required
def hiring_update_form_view(request, pk=None):
    context = get_context_data(request)
    hiring = get_object_or_404(Hiring, pk=pk)
    context["object"] = hiring
    form = HiringCreateForm(request.POST or None, instance=hiring)
    context["form"] = form
    task_list = Task.objects.filter(hiring=hiring)
    context["task_list"] = task_list
    if request.method == "POST":
        if form.is_valid():
            instance = form.save()
            handle_task_formset(request, instance)
            messages.success(request, "Contratación modificada con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Location": reverse("hiring_index")}
            )
    return render(request, "income/receipt_form.html", context)


@login_required
def hiring_delete_view(request, pk):
    hiring = get_object_or_404(Hiring, pk=pk)
    context = get_context_data(request)
    context["object"] = hiring
    if request.method == "POST":
        try:
            hiring.delete()
            messages.success(request, "Contratación eliminada con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "hiringListChanged"})
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar la contratación porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# class ReceiptListView(CustomContextMixin, ListView):
#     """
#     Display a list of :model:`income.Receipt` instances and a GET method search.
#     **Context:**
#     ``receipt_list``
#         A list of :model:`income.Receipt` instances
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`receipt_list.html`
#     """

#     model = Receipt

#     def get_queryset(self):
#         receipt_type = self.request.path.strip("/").split("/")[0].upper()
#         search_input = self.request.GET.get("search_input")
#         if search_input:
#             return Receipt.objects.filter(receipt_type=receipt_type).filter(
#                 Q(customer__name__icontains=search_input)
#                 | Q(id__icontains=search_input)
#                 | Q(address__icontains=search_input)
#             )
#         return Receipt.objects.filter(receipt_type=receipt_type)

#     def get_context_data(self, **kwargs):
#         search_input = self.request.GET.get("search_input")
#         extra_context = {
#             "search_text": "Buscar por número, cliente o domicilio.",
#             "search_input": search_input if search_input else "",
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}


# class ReceiptCreateView(CustomContextMixin, CustomSuccessMessageMixin, CreateView):
#     """
#     Display a form for creating a :model:`income.Receipt` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     ``product_formset``
#         Formset for creating products related to current receipt.
#     ``tax_formset``
#         Formset for creating taxes related to current receipt.
#     **Template:**
#     :template:`income/receipt_form.html`.
#     """

#     model = Receipt
#     form_class = ReceiptCreateForm

#     def get_context_data(self, **kwargs):
#         request_path = self.request.path.strip("/").split("/")
#         receipt_id = self.request.GET.get("receipt")
#         receipt = Receipt.objects.get(pk=receipt_id) if receipt_id else self.object

#         receipt_lookup = {
#             "budget": {
#                 "receipt_type": None,
#                 "receipt_list": None,
#             },
#             "hiring": {
#                 "receipt_type": "BUDGET",
#                 "receipt_list": Receipt.objects.filter(
#                     receipt_type="BUDGET",
#                     has_hiring__isnull=True,
#                 ),
#             },
#             "invoice": {
#                 "receipt_type": "HIRING",
#                 "receipt_list": Receipt.objects.filter(
#                     receipt_type="HIRING",
#                     has_invoice__isnull=True,
#                 ),
#             },
#         }

#         extra_context = {
#             "receipt_type": receipt_lookup.get(request_path[0]).get("receipt_type"),
#             "receipt_list": receipt_lookup.get(request_path[0]).get("receipt_list"),
#             "product_formset": ProductFormset(instance=receipt),
#             "tax_formset": TaxFormset(instance=receipt),
#         }

#         if self.request.POST:
#             extra_context["product_formset"] = ProductFormset(
#                 self.request.POST, instance=receipt
#             )
#             extra_context["tax_formset"] = TaxFormset(
#                 self.request.POST, instance=receipt
#             )

#         return {**super().get_context_data(**kwargs), **extra_context}

#     def get_initial(self):
#         receipt_id = self.request.GET.get("receipt")
#         if receipt_id:
#             receipt = Receipt.objects.get(pk=receipt_id)
#             return {
#                 "customer": receipt.customer,
#                 "has_invoice": receipt.has_invoice,
#                 "has_hiring": receipt.has_hiring,
#                 "address": receipt.address,
#                 "location": receipt.location,
#                 "phone_number": receipt.phone_number,
#                 "notes": receipt.notes,
#                 "subtotal": receipt.subtotal,
#                 "total": receipt.total,
#             }

#     def form_valid(self, form):
#         request_path = self.request.path.strip("/").split("/")
#         receipt_type = request_path[0]
#         form.instance.receipt_type = receipt_type.upper()
#         form.instance.is_clean = True
#         receipt = form.save()
#         context = self.get_context_data()

#         product_formset = context.get("product_formset")
#         if product_formset.is_valid():
#             product_formset.instance = receipt
#             product_formset.save()

#         tax_formset = context.get("tax_formset")
#         if tax_formset.is_valid():
#             tax_formset.instance = receipt
#             tax_formset.save()

#         # Create an asiento to register the invoice. (Falta parte impuestos)
#         if receipt_type == "invoice":
#             asiento = Asiento.objects.create(create_date=timezone.now().date())
#             receipt.asiento = asiento
#             receipt.save()
#             Entry.objects.create(asiento=asiento, cuenta=receipt.customer.cuenta_activo, debe=form.cleaned_data.get("total"))
#             Entry.objects.create(asiento=asiento, cuenta_id=15, haber=form.cleaned_data.get("total"))

#         # Set current receipt has_hiring or has_invoice attribute.
#         if self.request.GET.get("receipt"):
#             if receipt_type == "hiring":
#                 budget = Receipt.objects.get(pk=self.request.GET.get("receipt"))
#                 budget.has_hiring = receipt
#                 budget.save()
#             elif receipt_type == "invoice":
#                 hiring = Receipt.objects.get(pk=self.request.GET.get("receipt"))
#                 hiring.has_invoice = receipt
#                 hiring.save()

# Create an operator task for every 'service' when a 'hiring' is created.
# if receipt_type == "hiring":
#     for product_form in product_formset:
#         if product_form.product_type.type_select == "SERVICE":
#             OperatorTask.objects.update_or_create(
#                 task_type=product_form.cleaned_data.get("product_type").task_type,
#                 hiring=receipt,
#                 defaults={
#                     "task_type": product_form.cleaned_data.get(
#                         "product_type"
#                     ).task_type,
#                     "hiring": receipt,
#                 },
#             )

# return super().form_valid(form)


# class ReceiptUpdateView(CustomContextMixin, CustomSuccessMessageMixin, UpdateView):
#     """
#     Display a form for editing a :model:`income.Receipt` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     ``product_formset``
#         Formset for creating products related to current receipt.
#     ``tax_formset``
#         Formset for creating taxes related to current receipt.
#     **Template:**
#     :template:`income/receipt_form.html`.
#     """

#     model = Receipt
#     form_class = ReceiptCreateForm

#     def get_context_data(self, **kwargs):
#         receipt = self.object
#         extra_context = {
#             "product_formset": ProductFormset(instance=receipt),
#             "tax_formset": TaxFormset(instance=receipt),
#         }

#         if self.request.POST:
#             extra_context["product_formset"] = ProductFormset(
#                 self.request.POST, instance=receipt
#             )
#             extra_context["tax_formset"] = TaxFormset(
#                 self.request.POST, instance=receipt
#             )

#         return {**super().get_context_data(**kwargs), **extra_context}

#     def form_valid(self, form):
#         request_path = self.request.path.strip("/").split("/")
#         receipt_type = request_path[0]
#         form.instance.receipt_type = receipt_type.upper()
#         # form.instance.is_clean = form.cleaned_data.get("is_clean") # Fijarse cuando una contratación está limpia o colocada
#         receipt = form.save()
#         context = self.get_context_data()

#         product_formset = context.get("product_formset")
#         if product_formset.is_valid():
#             product_formset.instance = receipt
#             product_formset.save()

#         tax_formset = context.get("tax_formset")
#         if tax_formset.is_valid():
#             tax_formset.instance = receipt
#             tax_formset.save()

#         # Set current receipt has_hiring or has_invoice attribute.
#         if self.request.GET.get("receipt"):
#             if receipt_type == "hiring":
#                 budget = Receipt.objects.get(pk=self.request.GET.get("receipt"))
#                 budget.has_hiring = receipt
#                 budget.save()
#             elif receipt_type == "invoice":
#                 hiring = Receipt.objects.get(pk=self.request.GET.get("receipt"))
#                 hiring.has_invoice = receipt
#                 hiring.save()

#         # Create an operator task for every 'service' when a 'hiring' is created.
#         # if receipt_type == "hiring":
#         #     for product_form in product_formset:
#         #         print(product_form.cleaned_data.get("product_type"))
#         #         if product_form.cleaned_data.get("product_type").type_select == "SERVICE":
#         #             OperatorTask.objects.update_or_create(
#         #                 task_type=product_form.cleaned_data.get("product_type").task_type,
#         #                 hiring=receipt,
#         #                 defaults={
#         #                     "task_type": product_form.cleaned_data.get(
#         #                         "product_type"
#         #                     ).task_type,
#         #                     "hiring": receipt,
#         #                 },
#         #             )

#         return super().form_valid(form)


# class ReceiptDeleteView(CustomContextMixin, CustomSuccessMessageMixin, DeleteView):
#     """
#     Display a form for deleting a :model:`income.Receipt` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`income/receipt_form.html`.
#     """

#     model = Receipt


# # endregion
# # region IncomePayment


# class IncomePaymentListView(CustomContextMixin, ListView):
#     """
#     Display a list of :model:`income.IncomePayment` instances and a GET method search.
#     **Context:**
#     ``income_payment_list``
#         A list of :model:`income.IncomePayment` instances
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`income_payment_list.html`
#     """

#     model = IncomePayment
#     template_name = "income/income_payment_list.html"
#     context_object_name = "income_payment_list"

#     def get_queryset(self):
#         search_input = self.request.GET.get("search_input")
#         if search_input:
#             return IncomePayment.objects.filter(
#                 Q(customer__name__icontains=search_input)
#                 | Q(issue_date__icontains=search_input)
#                 | Q(receipt__address__icontains=search_input)
#             )

#         filter_kwargs = {key: value for key, value in self.request.GET.items() if value}
#         return IncomePayment.objects.filter(**filter_kwargs)

#     def get_context_data(self, **kwargs):
#         search_input = self.request.GET.get("search_input") or ""
#         filter_options = {
#             "customer": Customer.objects.all(),
#         }
#         extra_context = {
#             "search_text": "Buscar por fecha, cliente o domicilio.",
#             "search_input": search_input,
#             "filter_options": filter_options,
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}


# class IncomePaymentCreateView(LoginRequiredMixin, CustomSuccessMessageMixin, CreateView):
#     """
#     Display a form for creating a :model:`income.IncomePayment` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`income/income_payment_form.html`.
#     """

#     model = IncomePayment
#     form_class = IncomePaymentCreateForm
#     template_name = "income/income_payment_form.html"

#     def get_context_data(self, **kwargs):
#         request_path = self.request.path.strip("/").split("/")
#         extra_context = {
#             "app": self.model._meta.app_label,
#             "page": request_path[1],
#             "model": request_path[0],
#             "receipt_list": Receipt.objects.filter(receipt_type="INVOICE", is_paid=False),
#         }
#         return {**super().get_context_data(**kwargs), **extra_context}

#     def get_initial(self):
#         receipt_id = self.request.GET.get("receipt")
#         if receipt_id:
#             receipt = Receipt.objects.get(pk=receipt_id)
#             return {
#                 "customer": receipt.customer,
#                 "receipt": receipt,
#                 "amount": receipt.total,
#             }

#         customer_id = self.kwargs.get("pk")
#         if customer_id:
#             customer = Customer.objects.get(pk=customer_id)
#             return {
#                 "customer": customer,
#                 "option": "OPERATOR",
#                 "method": 1,
#             }

#     def form_valid(self, form):
#         # Link the income payment to selected receipt if any. Check if it is paid fully.
#         receipt = form.cleaned_data.get("receipt")
#         if receipt:
#             form.instance.receipt = receipt
#             receipt.set_is_paid()

#         customer = form.cleaned_data.get("customer")
#         amount = form.cleaned_data.get("amount")
#         payment_method = form.cleaned_data.get("method")

#         # Create a new asiento instance to register the income payment.
#         asiento = Asiento.objects.create(create_date=timezone.now().date())
#         Entry.objects.create(asiento=asiento, cuenta=payment_method.cuenta, debe=amount)
#         Entry.objects.create(asiento=asiento, cuenta=customer.cuenta_activo, haber=amount)

#         return super().form_valid(form)


# class IncomePaymentUpdateView(CustomContextMixin, CustomSuccessMessageMixin, UpdateView):
#     """
#     Display a form for creating a :model:`income.IncomePayment` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`income/income_payment_form.html`.
#     """

#     model = IncomePayment
#     form_class = IncomePaymentCreateForm

#     def get_initial(self):
#         receipt_id = self.request.GET.get("receipt")
#         if receipt_id:
#             receipt = Receipt.objects.get(pk=receipt_id)
#             return {
#                 "customer": receipt.customer,
#                 "receipt": receipt,
#                 "amount": receipt.total,
#             }


# class IncomePaymentDeleteView(CustomContextMixin, CustomSuccessMessageMixin, DeleteView):
#     """
#     Display a form for deleting a :model:`income.IncomePayment` instance.
#     **Context:**
#     ``app``
#         A string to set template's title and navbar's active tab.
#     ``page``
#         A string to set card's active tab.
#     ``model``
#         Current view's model to set template url's names.
#     **Template:**
#     :template:`income/receipt_form.html`.
#     """

#     model = IncomePayment


# endregion


@login_required
def receipt_customer_create_view(request):
    form = CustomerCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                cuenta_activo = Cuenta.objects.create(
                    subrubro_id=7, name=form.cleaned_data.get("name")
                )
                form.instance.cuenta_activo = cuenta_activo
                cuenta_pasivo = Cuenta.objects.create(
                    subrubro_id=16, name=form.cleaned_data.get("name")
                )
                form.instance.cuenta_pasivo = cuenta_pasivo
                form.save()
                messages.success(request, "Cliente creado con éxito!")
                return HttpResponse(
                    status=204, headers={"HX-Trigger": "customerCreated"}
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    messages.error(
                        request,
                        "Ya existe un cliente con el tipo y número de identificación ingresados.",
                    )
                    return HttpResponse(status=204)
    return render(request, "income/customer_form.html", context)


@login_required
def service_create_view(request):
    form = ServiceCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, "income/service_inline_form.html", context)


@login_required
def service_update_view(request, pk=None):
    service = Service.objects.get(pk=pk)
    form = ServiceCreateForm(request.POST or None, instance=service)
    context = {
        "form": form,
    }
    return render(request, "income/service_inline_form.html", context)


@login_required
def tax_create_view(request):
    form = TaxCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, "income/tax_inline_form.html", context)


@login_required
def tax_update_view(request, pk=None):
    tax = Tax.objects.get(pk=pk)
    form = TaxCreateForm(request.POST or None, instance=tax)
    context = {
        "form": form,
    }
    return render(request, "income/tax_inline_form.html", context)

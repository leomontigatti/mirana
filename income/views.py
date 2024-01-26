from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from configuration.models import Collector, PaymentMethod
from income.forms import (
    BudgetCreateForm,
    CustomerCreateForm,
    HiringCreateForm,
    IncomePaymentCreateForm,
    SalesInvoiceCreateForm,
    ServicesFormSet,
    TaxesFormset,
)
from income.models import (
    Budget,
    Customer,
    CustomerMovement,
    Hiring,
    HiringStatusChoices,
    IncomePayment,
    SalesInvoice,
    Service,
    Tax,
)
from main.models import (
    IdentificationTypeChoices,
    IvaSituationChoices,
    SaleConditionChoices,
)
from main.tasks import send_whatsapp_acceptance
from main.views import is_not_operator, render_pdf_view


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    return {
        "app": "income",
        "page": request_path[1],
        "model": request_path[0],
    }


# def get_delete_error_message(instance):
#     model_name = instance._meta.verbose_name.lower()
#     article = "el" if model_name == "presupuesto" else "la"
#     suffix = "o" if model_name == "presupuesto" else "a"
#     services = instance.services.count() if instance.services.exists() else 0
#     taxes = (
#         instance.income_taxes.count()
#         if model_name != "contratación" and instance.income_taxes.exists()
#         else 0
#     )
#     if services and not taxes:
#         return f"No se puede eliminar {article} {model_name} porque tiene {services} servicio{'s' if services > 1 else ''} relacionado{'s' if services > 1 else ''}."
#     elif taxes and not services:
#         return f"No se puede eliminar {article} {model_name} porque tiene {taxes} impuesto{'s' if taxes > 1 else ''} relacionado{'s' if taxes > 1 else ''}."
#     elif services and taxes:
#         return f"No se puede eliminar {article} {model_name} porque tiene {services} servicio{'s' if services > 1 else ''} y {taxes} impuesto{'s' if taxes > 1 else ''} relacionados."
#     else:
#         try:
#             return f"No se puede eliminar {article} {model_name} porque está relacionad{suffix} a la contratación número {instance.hiring.id}."
#         except Hiring.DoesNotExist:
#             return f"No se puede eliminar {article} {model_name} porque está relacionad{suffix} a la factura de venta número {instance.sales_invoice.id}."


@login_required
@user_passes_test(is_not_operator)
def service_delete_view(request, model, pk):
    service = get_object_or_404(Service, pk=pk)

    if model == "budget":
        parent = service.budget
    elif model == "hiring":
        parent = service.hiring
    else:
        parent = service.invoice

    service.delete()
    messages.success(request, "Servicio eliminado con éxito!")
    return redirect(parent.get_update_url())


@login_required
@user_passes_test(is_not_operator)
def tax_delete_view(request, model, pk):
    tax = get_object_or_404(Tax, pk=pk)

    if model == "budget":
        parent = tax.budget
    else:
        parent = tax.invoice

    tax.delete()
    messages.success(request, "Impuesto eliminado con éxito!")
    return redirect(parent.get_update_url())


# region Customer


@login_required
@user_passes_test(is_not_operator)
def customer_list_view(request):
    context = get_context_data(request)
    queryset = Customer.objects.all()
    filter_options = {
        "identification_type": IdentificationTypeChoices.choices,
        "iva_situation": IvaSituationChoices.choices,
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = Customer.objects.filter(
            Q(name__icontains=search_input)
            | Q(identification_number__icontains=search_input)
            | Q(address__icontains=search_input)
        )

    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = Customer.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = (
        "Buscar por nombre, número de identificación o domicilio..."
    )
    context["page_obj"] = page_obj
    return render(request, "income/customer_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def customer_create_view(request):
    context = get_context_data(request)
    form = CustomerCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        instance = form.save()
        send_whatsapp_acceptance(
            instance.phone_number
        )  # TODO: ponerlo como método de instancia

        messages.success(request, "Cliente creado con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    return render(request, "income/customer_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def customer_update_view(request, pk):
    context = get_context_data(request)
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerCreateForm(request.POST or None, instance=customer)

    if request.method == "POST" and form.is_valid():
        instance = form.save()

        messages.success(request, "Cliente modificado con éxito!")
        return redirect(instance.get_absolute_url())

    context["object"] = customer
    context["form"] = form
    return render(request, "income/customer_form.html", context)


@login_required
def customer_detail_view(request, pk):
    context = get_context_data(request)
    customer = get_object_or_404(Customer, pk=pk)
    movement_list = CustomerMovement.objects.filter(customer=customer)

    context["object"] = customer
    context["movement_list"] = movement_list
    return render(request, "income/customer_detail.html", context)


@login_required
def render_customer_movements(request, pk):
    context = get_context_data(request)
    customer = get_object_or_404(Customer, pk=pk)

    context["object"] = customer
    return render_pdf_view(request, "income/customer_movements.html", context)


# endregion
# region Budget


@login_required
@user_passes_test(is_not_operator)
def budget_list_view(request):
    context = get_context_data(request)
    queryset = Budget.objects.all()
    search_input = request.GET.get("search_input", "")

    if search_input:
        queryset = Budget.objects.filter(
            Q(address__icontains=search_input)
            | Q(customer__name__icontains=search_input)
            | Q(issue_date__icontains=search_input)
        )

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha de inicio o ID de contratación..."
    context["page_obj"] = page_obj
    return render(request, "income/budget_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def budget_create_view(request):
    context = get_context_data(request)
    form = BudgetCreateForm(request.POST or None)
    service_formset = ServicesFormSet(
        request.POST or None, prefix="services", queryset=Service.objects.none()
    )
    taxes_formset = TaxesFormset(
        request.POST or None, prefix="taxes", queryset=Tax.objects.none()
    )

    if request.method == "POST" and all(
        [form.is_valid(), service_formset.is_valid(), taxes_formset.is_valid()]
    ):
        instance = form.save()

        for service_form in service_formset:
            service_form.instance.budget = instance
        service_formset.save()
        for tax_form in taxes_formset:
            tax_form.instance.budget = instance
        taxes_formset.save()

        messages.success(request, "Presupuesto creado con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    context["service_formset"] = service_formset
    context["taxes_formset"] = taxes_formset
    return render(request, "income/budget_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def budget_update_view(request, pk):
    context = get_context_data(request)
    budget = get_object_or_404(Budget, pk=pk)
    form = BudgetCreateForm(request.POST or None, instance=budget)
    service_formset = ServicesFormSet(
        request.POST or None, prefix="services", queryset=budget.services.all()
    )
    taxes_formset = TaxesFormset(
        request.POST or None, prefix="taxes", queryset=budget.income_taxes.all()
    )

    if request.method == "POST" and all(
        [form.is_valid(), service_formset.is_valid(), taxes_formset.is_valid()]
    ):
        instance = form.save()

        for service_form in service_formset:
            service_form.instance.budget = instance
        service_formset.save()
        for tax_form in taxes_formset:
            tax_form.instance.budget = instance
        taxes_formset.save()

        messages.success(request, "Presupuesto modificado con éxito!")
        return redirect(instance.get_absolute_url())

    context["object"] = budget
    context["form"] = form
    context["service_formset"] = service_formset
    context["taxes_formset"] = taxes_formset
    return render(request, "income/budget_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def budget_detail_view(request, pk):
    context = get_context_data(request)
    budget = get_object_or_404(Budget, pk=pk)
    services_queryset = Service.objects.filter(budget=budget)
    taxes_queryset = Tax.objects.filter(budget=budget)

    context["object"] = budget
    context["services_queryset"] = services_queryset
    context["taxes_queryset"] = taxes_queryset
    return render(request, "income/budget_detail.html", context)


@login_required
@user_passes_test(is_not_operator)
@require_POST
def budget_delete_view(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    try:
        budget.delete()
        messages.success(request, "Presupuesto eliminado con éxito!")
    except ProtectedError:
        messages.error(
            request,
            # get_delete_error_message(budget),
        )
        return redirect(budget.get_update_url())

    return redirect("budget_list")


@login_required
def send_budget(request, pk):
    context = get_context_data(request)
    budget = get_object_or_404(Budget, pk=pk)

    context["budget"] = budget
    return render_pdf_view(request, "income/budget_pdf.html", context)


# endregion
# region Hiring


@login_required
def hiring_list_view(request):
    context = get_context_data(request)
    queryset = Hiring.objects.all()
    filter_options = {
        "status": HiringStatusChoices.choices,
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = Hiring.objects.filter(
            Q(address__icontains=search_input)
            | Q(customer__name__icontains=search_input)
            | Q(start_date__icontains=search_input)
        )

    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = Hiring.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha de inicio, domicilio o cliente..."
    context["page_obj"] = page_obj
    return render(request, "income/hiring_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def hiring_create_view(request):
    context = get_context_data(request)
    form = HiringCreateForm(request.POST or None)
    service_formset = ServicesFormSet(
        request.POST or None, prefix="services", queryset=Service.objects.none()
    )
    data = {}

    # When a customer instance is selected, search for its related budgets.
    customer_id = request.GET.get("customer", "")
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
        data["customer"] = customer
        form = HiringCreateForm(request.POST or None, initial=data, customer=customer)

    # If a budget instance is selected, set initial form and formset data.
    budget_id = request.GET.get("budget", "")
    if budget_id:
        budget = get_object_or_404(Budget, pk=budget_id)
        data["customer"] = budget.customer
        data["budget"] = budget
        data["address"] = budget.address
        data["lat"] = budget.lat
        data["lng"] = budget.lng
        form = HiringCreateForm(
            request.POST or None, initial=data, customer=budget.customer
        )
        service_formset = ServicesFormSet(
            request.POST or None, prefix="services", queryset=budget.services.all()
        )

    if request.method == "POST" and all([form.is_valid(), service_formset.is_valid()]):
        instance = form.save()

        for service_form in service_formset:
            service_form.instance.budget = instance.budget
            service_form.instance.hiring = instance
        service_formset.save()

        for service in instance.services.all():
            if service.service_type.pk in [1, 2]:
                service.create_bathroom_workshop_task()
            elif service.service_type.pk in [3, 4]:
                service.create_cleaning_tasks()

        instance.update_or_create_stock_movement()
        instance.update_or_create_reminder_task()

        messages.success(request, "Contratación creada con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    context["service_formset"] = service_formset
    return render(request, "income/hiring_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def hiring_update_view(request, pk):
    context = get_context_data(request)
    hiring = get_object_or_404(Hiring, pk=pk)
    invoice = hiring.sales_invoice if hasattr(hiring, "sales_invoice") else None
    budget = hiring.budget
    form = HiringCreateForm(request.POST or None, instance=hiring)
    service_formset = ServicesFormSet(
        request.POST or None, prefix="services", queryset=hiring.services.all()
    )

    if request.method == "POST" and all([form.is_valid(), service_formset.is_valid()]):
        form.instance.budget = budget
        form.instance.sales_invoice = invoice
        instance = form.save()

        for service_form in service_formset:
            service_form.instance.budget = budget
            service_form.instance.hiring = instance
            service_form.instance.invoice = invoice
        service_formset.save()

        for service in instance.services.all():
            if service.service_type.pk in [1, 2]:
                service.update_bathroom_workshop_task()
            elif service.service_type.pk in [3, 4]:
                service.update_cleaning_tasks()

        instance.update_or_create_reminder_task()
        instance.update_or_create_stock_movement()

        messages.success(request, "Contratación modificada con éxito!")
        return redirect(instance.get_absolute_url())

    context["object"] = hiring
    context["form"] = form
    context["service_formset"] = service_formset
    return render(request, "income/hiring_form.html", context)


@login_required
def hiring_detail_view(request, pk):
    context = get_context_data(request)
    hiring = get_object_or_404(Hiring, pk=pk)
    services_queryset = Service.objects.filter(hiring=hiring)

    context["object"] = hiring
    context["services_queryset"] = services_queryset
    return render(request, "income/hiring_detail.html", context)


@login_required
@user_passes_test(is_not_operator)
@require_POST
def hiring_delete_view(request, pk):
    hiring = get_object_or_404(Hiring, pk=pk)

    try:
        hiring.delete()
        messages.success(request, "Contratación eliminada con éxito!")
    except ProtectedError:
        messages.error(
            request,
            # get_delete_error_message(hiring),
        )
        return redirect(hiring.get_update_url())

    return redirect("hiring_list")


# endregion
# region SalesInvoice


@login_required
@user_passes_test(is_not_operator)
def sales_invoice_list_view(request):
    context = get_context_data(request)
    queryset = SalesInvoice.objects.all()
    filter_options = {
        "is_paid": ((True, "Pagada"), (False, "No pagada")),
        "sale_condition": SaleConditionChoices.choices,
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = SalesInvoice.objects.filter(
            Q(customer__name__icontains=search_input)
            | Q(issue_date__icontains=search_input)
        )
    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = SalesInvoice.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha de emisión o cliente..."
    context["page_obj"] = page_obj
    return render(request, "income/invoice_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def sales_invoice_create_view(request):
    context = get_context_data(request)
    form = SalesInvoiceCreateForm(request.POST or None)
    service_formset = ServicesFormSet(
        request.POST or None, prefix="services", queryset=Service.objects.none()
    )
    taxes_formset = TaxesFormset(
        request.POST or None, prefix="taxes", queryset=Tax.objects.none()
    )
    hiring = None
    hiring_id = request.GET.get("hiring", "")

    # If a hiring instance is selected, set initial form and formset data.
    if hiring_id:
        hiring = get_object_or_404(Hiring, pk=hiring_id)
        data = {
            "hiring": hiring,
            "customer": hiring.customer,
            "notes": f"Contratación {hiring.pk} -> {hiring.address}",
        }

        if hiring.budget:
            data["sale_condition"] = hiring.budget.sale_condition
            data["subtotal"] = hiring.budget.subtotal
            data["total"] = hiring.budget.total

        form = SalesInvoiceCreateForm(request.POST or None, initial=data)
        service_formset = ServicesFormSet(
            request.POST or None, prefix="services", queryset=hiring.services.all()
        )
        taxes_formset = TaxesFormset(
            request.POST or None,
            prefix="taxes",
            queryset=(
                hiring.budget.income_taxes.all()
                if hiring.budget
                else Tax.objects.none()
            ),
        )

    if request.method == "POST" and all(
        [form.is_valid(), service_formset.is_valid(), taxes_formset.is_valid()]
    ):
        form.instance.hiring = hiring
        instance = form.save()
        for service_form in service_formset:
            service_form.instance.hiring = hiring
            service_form.instance.invoice = instance
        service_formset.save()
        for tax_form in taxes_formset:
            tax_form.instance.invoice = instance
        taxes_formset.save()

        instance.update_or_create_taxes_entry()
        instance.update_or_create_customer_movement()

        messages.success(request, "Factura de venta creada con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    context["service_formset"] = service_formset
    context["taxes_formset"] = taxes_formset
    return render(request, "income/invoice_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def sales_invoice_update_view(request, pk):
    context = get_context_data(request)
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    asiento, hiring = invoice.asiento, invoice.hiring
    form = SalesInvoiceCreateForm(request.POST or None, instance=invoice)
    service_formset = ServicesFormSet(
        request.POST or None, prefix="services", queryset=invoice.services.all()
    )
    taxes_formset = TaxesFormset(
        request.POST or None, prefix="taxes", queryset=invoice.income_taxes.all()
    )

    if request.method == "POST":
        password = request.POST.get("password", "")
        user = authenticate(username=request.user.username, password=password)

        if not user:
            messages.error(request, "La contraseña ingresada es incorrecta!")
            return redirect("salesinvoice_list")

        if all([form.is_valid(), service_formset.is_valid(), taxes_formset.is_valid()]):
            form.instance.asiento = asiento
            form.instance.hiring = hiring
            instance = form.save()

            for service_form in service_formset:
                service_form.instance.hiring = hiring
                service_form.instance.invoice = instance
            service_formset.save()
            for tax_form in taxes_formset:
                tax_form.instance.invoice = instance
            taxes_formset.save()

            instance.update_or_create_taxes_entry()
            instance.update_or_create_customer_movement()

            messages.success(request, "Factura de venta modificada con éxito!")
            return redirect(instance.get_absolute_url())

    context["object"] = invoice
    context["form"] = form
    context["service_formset"] = service_formset
    context["taxes_formset"] = taxes_formset
    return render(request, "income/invoice_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def sales_invoice_detail_view(request, pk):
    context = get_context_data(request)
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    services_queryset = invoice.services.all()
    taxes_queryset = invoice.income_taxes.all()

    context["object"] = invoice
    context["services_queryset"] = services_queryset
    context["taxes_queryset"] = taxes_queryset
    return render(request, "income/invoice_detail.html", context)


# endregion
# region IncomePayment


@login_required
@user_passes_test(is_not_operator)
def payment_list_view(request):
    context = get_context_data(request)
    queryset = IncomePayment.objects.all()
    filter_options = {
        "collector": Collector.objects.all(),
        "method": PaymentMethod.objects.all(),
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = IncomePayment.objects.filter(
            Q(pk__icontains=search_input)
            | Q(customer__name__icontains=search_input)
            | Q(issue_date__icontains=search_input)
        )

    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = IncomePayment.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha de emisión, número o cliente..."
    context["page_obj"] = page_obj
    return render(request, "income/payment_list.html", context)


@login_required
def payment_create_view(request, pk=0):
    context = get_context_data(request)
    data = {}

    if is_not_operator(request.user):
        invoice_id = request.GET.get("invoice", "")

        # Get invoice id from GET request if selected invoice.
        if invoice_id:
            invoice = get_object_or_404(SalesInvoice, pk=invoice_id)
            data["invoice"] = invoice
            data["customer"] = invoice.customer
            data["amount"] = invoice.total

    else:
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            customer = None

        data["customer"] = customer
        data["method"] = PaymentMethod.objects.get(pk=1)
        data["collector"] = request.user.collector

    form = IncomePaymentCreateForm(request.POST or None, initial=data)

    if request.method == "POST" and form.is_valid():
        instance = form.save()

        instance.update_or_create_customer_movement()
        instance.check_invoice_is_paid()

        messages.success(request, "Recibo de cobro creado con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    return render(request, "income/payment_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def payment_update_view(request, pk):
    context = get_context_data(request)
    payment = get_object_or_404(IncomePayment, pk=pk)
    asiento, invoice = payment.asiento, payment.invoice
    form = IncomePaymentCreateForm(request.POST or None, instance=payment)

    if request.method == "POST":
        password = request.POST.get("password", "")
        user = authenticate(username=request.user.username, password=password)

        if not user:
            messages.error(request, "Contraseña incorrecta!")
            return redirect("incomepayment_list")

        if form.is_valid():
            form.instance.asiento = asiento
            form.instance.invoice = invoice
            instance = form.save()

            instance.update_or_create_customer_movement()
            instance.check_invoice_is_paid()

            messages.success(request, "Recibo de cobro modificado con éxito!")
            return redirect(instance.get_absolute_url())

    context["object"] = payment
    context["form"] = form
    return render(request, "income/payment_form.html", context)


@login_required
def payment_detail_view(request, pk):
    context = get_context_data(request)
    payment = get_object_or_404(IncomePayment, pk=pk)

    context["object"] = payment
    return render(request, "income/payment_detail.html", context)


# endregion

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from configuration.models import PaymentMethod
from expenses.forms import (
    ExpensesFormset,
    ExpensesInvoiceCreateForm,
    ExpensesPaymentCreateForm,
    SupplierCreateForm,
    TaxesFormset,
)
from expenses.models import (
    Expense,
    ExpensesInvoice,
    ExpensesPayment,
    Supplier,
    SupplierMovement,
    Tax,
)
from main.models import (
    IdentificationTypeChoices,
    IvaSituationChoices,
    SaleConditionChoices,
)
from main.views import is_not_operator


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    return {
        "app": "expenses",
        "page": request_path[1],
        "model": request_path[0],
    }


@login_required
@user_passes_test(is_not_operator)
def expense_delete_view(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    parent = expense.invoice

    expense.delete()
    messages.success(request, "Gasto eliminado con éxito!")
    return redirect(parent.get_update_url())


@login_required
@user_passes_test(is_not_operator)
def tax_delete_view(request, pk):
    tax = get_object_or_404(Tax, pk=pk)
    parent = tax.invoice

    tax.delete()
    messages.success(request, "Impuesto eliminado con éxito!")
    return redirect(parent.get_update_url())


# region Supplier


@login_required
@user_passes_test(is_not_operator)
def supplier_list_view(request):
    context = get_context_data(request)
    queryset = Supplier.objects.all()
    filter_options = {
        "identification_type": IdentificationTypeChoices.choices,
        "iva_situation": IvaSituationChoices.choices,
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = request.GET.get("search_input", "")

    if search_input:
        queryset = Supplier.objects.filter(
            Q(name__icontains=search_input)
            | Q(identification_number__icontains=search_input)
            | Q(address__icontains=search_input)
        )
    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = Supplier.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = (
        "Buscar por nombre, número de identificación o domicilio..."
    )
    context["page_obj"] = page_obj
    return render(request, "expenses/supplier_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def supplier_create_view(request):
    context = get_context_data(request)
    form = SupplierCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        instance = form.save()

        messages.success(request, "Proveedor creado con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    return render(request, "expenses/supplier_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def supplier_update_view(request, pk):
    context = get_context_data(request)
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierCreateForm(request.POST or None, instance=supplier)

    if request.method == "POST" and form.is_valid():
        instance = form.save()

        messages.success(request, "Proveedor modificado con éxito!")
        return redirect(instance.get_absolute_url())

    context["object"] = supplier
    context["form"] = form
    return render(request, "expenses/supplier_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def supplier_detail_view(request, pk):
    context = get_context_data(request)
    supplier = get_object_or_404(Supplier, pk=pk)
    movement_list = SupplierMovement.objects.filter(supplier=supplier)

    context["object"] = supplier
    context["movement_list"] = movement_list
    return render(request, "expenses/supplier_detail.html", context)


# endregion
# region ExpensesInvoice


@login_required
@user_passes_test(is_not_operator)
def expenses_invoice_list_view(request):
    context = get_context_data(request)
    queryset = ExpensesInvoice.objects.all()
    filter_options = {
        "is_paid": ((True, "Pagada"), (False, "No pagada")),
        "sale_condition": SaleConditionChoices.choices,
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = ExpensesInvoice.objects.filter(
            Q(number__icontains=search_input)
            | Q(supplier__name__icontains=search_input)
            | Q(issue_date__icontains=search_input)
        )
    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = ExpensesInvoice.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha de emisión, número o proveedor..."
    context["page_obj"] = page_obj
    return render(request, "expenses/invoice_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def expenses_invoice_create_view(request):
    context = get_context_data(request)
    form = ExpensesInvoiceCreateForm(request.POST or None)
    expenses_formset = ExpensesFormset(
        request.POST or None,
        prefix="expenses",
        queryset=Expense.objects.none(),
    )
    taxes_formset = TaxesFormset(
        request.POST or None,
        prefix="taxes",
        queryset=Tax.objects.none(),
    )

    if request.method == "POST" and all(
        [form.is_valid(), expenses_formset.is_valid(), taxes_formset.is_valid()]
    ):
        instance = form.save()
        for expense_form in expenses_formset:
            expense_form.instance.invoice = instance
        expenses_formset.save()
        for tax_form in taxes_formset:
            tax_form.instance.invoice = instance
        taxes_formset.save()

        instance.update_or_create_supplier_movement()

        messages.success(request, "Factura de gastos creada con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    context["expenses_formset"] = expenses_formset
    context["taxes_formset"] = taxes_formset
    return render(request, "expenses/invoice_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def expenses_invoice_update_view(request, pk):
    context = get_context_data(request)
    invoice = get_object_or_404(ExpensesInvoice, pk=pk)
    asiento = invoice.asiento
    form = ExpensesInvoiceCreateForm(request.POST or None, instance=invoice)
    expenses_formset = ExpensesFormset(
        request.POST or None,
        prefix="expenses",
        queryset=invoice.expenses.all(),
    )
    taxes_formset = TaxesFormset(
        request.POST or None,
        prefix="taxes",
        queryset=invoice.expenses_taxes.all(),
    )

    if request.method == "POST":
        password = request.POST.get("password", "")
        user = authenticate(username=request.user.username, password=password)

        if not user:
            messages.error(request, "La contraseña ingresada es incorrecta!")
            return redirect("expensesinvoice_list")

        if all(
            [form.is_valid(), expenses_formset.is_valid(), taxes_formset.is_valid()]
        ):
            form.instance.asiento = asiento
            instance = form.save()
            for expense_form in expenses_formset:
                expense_form.instance.invoice = instance
            expenses_formset.save()
            for tax_form in taxes_formset:
                tax_form.instance.invoice = instance
            taxes_formset.save()

            instance.update_or_create_supplier_movement()

            messages.success(request, "Factura de gastos modificada con éxito!")
            return redirect(instance.get_absolute_url())

    context["object"] = invoice
    context["form"] = form
    context["expenses_formset"] = expenses_formset
    context["taxes_formset"] = taxes_formset
    return render(request, "expenses/invoice_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def expenses_invoice_detail_view(request, pk):
    context = get_context_data(request)
    invoice = get_object_or_404(ExpensesInvoice, pk=pk)
    expenses = Expense.objects.filter(invoice=invoice)
    taxes = Tax.objects.filter(invoice=invoice)

    context["object"] = invoice
    context["expenses"] = expenses
    context["taxes"] = taxes
    return render(request, "expenses/invoice_detail.html", context)


# endregion
# region ExpensesPayment


@login_required
@user_passes_test(is_not_operator)
def payment_list_view(request):
    context = get_context_data(request)
    queryset = ExpensesPayment.objects.all()
    filter_options = {
        "method": PaymentMethod.objects.all(),
        "invoice__isnull": ((True, "No imputada"), (False, "Imputada")),
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = ExpensesPayment.objects.filter(
            Q(pk__icontains=search_input)
            | Q(supplier__name__icontains=search_input)
            | Q(issue_date__icontains=search_input)
        )
    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        if "invoice__isnull" in filter_kwargs:
            is_null = filter_kwargs.get("invoice__isnull", "")
            filter_kwargs["invoice__isnull"] = True if is_null == "True" else False
        print(type(filter_kwargs.get("invoice__isnull")))
        queryset = ExpensesPayment.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha de emisión, número o proveedor..."
    context["page_obj"] = page_obj
    return render(request, "expenses/payment_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def payment_create_view(request):
    context = get_context_data(request)
    data = {}
    invoice = None
    invoice_id = request.GET.get("invoice", "")

    if invoice_id:
        invoice = get_object_or_404(ExpensesInvoice, pk=invoice_id)
        data["invoice"] = invoice
        data["supplier"] = invoice.supplier
        data["amount"] = invoice.total

    form = ExpensesPaymentCreateForm(request.POST or None, initial=data)

    if request.method == "POST" and form.is_valid():
        form.instance.invoice = invoice
        instance = form.save()

        instance.update_or_create_supplier_movement()
        instance.check_invoice_is_paid()

        messages.success(request, "Orden de pago creada con éxito!")
        return redirect(instance.get_absolute_url())

    context["form"] = form
    return render(request, "expenses/payment_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def payment_update_view(request, pk):
    context = get_context_data(request)
    payment = get_object_or_404(ExpensesPayment, pk=pk)
    asiento = payment.asiento
    form = ExpensesPaymentCreateForm(request.POST or None, instance=payment)

    if request.method == "POST":
        password = request.POST.get("password", "")
        user = authenticate(username=request.user.username, password=password)

        if not user:
            messages.error(request, "Contraseña incorrecta!")
            return redirect("expensespayment_list")

        if form.is_valid():
            form.instance.asiento = asiento
            instance = form.save()

            instance.update_or_create_supplier_movement()
            instance.check_invoice_is_paid()

            messages.success(request, "Orden de pago modificada con éxito!")
            return redirect(instance.get_absolute_url())

    context["object"] = payment
    context["form"] = form
    return render(request, "expenses/payment_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def payment_detail_view(request, pk):
    context = get_context_data(request)
    payment = get_object_or_404(ExpensesPayment, pk=pk)

    context["object"] = payment
    return render(request, "expenses/payment_detail.html", context)


# endregion

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounting.forms import CuentaCreateForm, EntryFormset, TaxTypeCreateForm
from accounting.models import Asiento, CapituloChoices, Cuenta, Rubro, Subrubro, TaxType
from main.views import is_not_operator


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    return {
        "app": "accounting",
        "page": request_path[1],
        "model": request_path[0],
    }


# region Cuenta


@login_required
@user_passes_test(is_not_operator)
def cuenta_list_view(request):
    context = get_context_data(request)
    form = CuentaCreateForm(request.POST or None)
    queryset = Cuenta.objects.all()

    context["form"] = form
    context["cuenta_list"] = queryset
    context["capitulo_list"] = CapituloChoices.labels
    context["rubro_list"] = Rubro.objects.all()
    context["subrubro_list"] = Subrubro.objects.all()
    return render(request, "accounting/cuenta_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def cuenta_create_view(request):
    context = get_context_data(request)
    form = CuentaCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Cuenta creada con éxito!")
            return redirect("cuenta_list")
        except IntegrityError as e:
            if "UNIQUE constraint" in e.args[0]:
                messages.error(
                    request,
                    "Ya existe una cuenta con el nombre y subrubro elegidos.",
                )
                return redirect("cuenta_list")

    context["form"] = form
    return render(request, "accounting/cuenta_form.html", context)


# endregion
# region TaxType


@login_required
@user_passes_test(is_not_operator)
def tax_type_list_view(request):
    context = get_context_data(request)
    queryset = TaxType.objects.all()

    context["object_list"] = queryset
    return render(request, "accounting/tax_type_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def tax_type_create_view(request):
    context = get_context_data(request)
    form = TaxTypeCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Impuesto creado con éxito!")
        return redirect("taxtype_list")

    context["form"] = form
    return render(request, "accounting/tax_type_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def tax_type_update_view(request, pk):
    context = get_context_data(request)
    tax_type = get_object_or_404(TaxType, pk=pk)
    form = TaxTypeCreateForm(request.POST or None, instance=tax_type)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Impuesto modificado con éxito!")
        return redirect("taxtype_list")

    context["object"] = tax_type
    context["form"] = form
    return render(request, "accounting/tax_type_form.html", context)


@login_required
@user_passes_test(is_not_operator)
@require_POST
def tax_type_delete_view(request, pk):
    tax_type = get_object_or_404(TaxType, pk=pk)

    try:
        tax_type.delete()
        messages.success(request, "Impuesto eliminado con éxito!")
    except ProtectedError:
        income_taxes = tax_type.income_taxes.count()
        expenses_taxes = tax_type.expenses_taxes.count()
        total = income_taxes + expenses_taxes
        messages.error(
            request,
            f"No se puede eliminar el tipo de impuesto porque tiene {total} impuesto{'s' if total > 1 else ''} relacionado{'s' if total > 1 else ''}",
        )

    return redirect("taxtype_list")


# endregion
# region Asiento


@login_required
@user_passes_test(is_not_operator)
def asiento_list_view(request):
    context = get_context_data(request)
    queryset = Asiento.objects.all()
    search_input = request.GET.get("search_input", "")

    if search_input:
        try:
            search_date = datetime.strptime(search_input, "%d/%m/%Y")
            queryset = Asiento.objects.filter(create_date=search_date)
        except ValueError:
            messages.error(
                request, "Se debe usar un formato de fecha válido: dd/mm/aaaa."
            )

    context["search_input"] = search_input
    context["search_text"] = "Buscar por fecha..."
    context["object_list"] = queryset
    return render(request, "accounting/asiento_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def asiento_create_view(request):
    context = get_context_data(request)
    entry_formset = EntryFormset(request.POST or None)

    if request.method == "POST" and entry_formset.is_valid():
        asiento = Asiento.objects.create()
        for form in entry_formset:
            form.instance.asiento = asiento
            form.save()
        messages.success(request, "Asiento creado con éxito!")
        return redirect("asiento_list")

    context["formset"] = entry_formset
    return render(request, "accounting/asiento_form.html", context)


# endregion

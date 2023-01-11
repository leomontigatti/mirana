from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounting.forms import CuentaCreateForm, EntryCreateForm, TaxTypeCreateForm
from accounting.models import (
    Asiento,
    CapituloChoices,
    Cuenta,
    Entry,
    Rubro,
    Subrubro,
    TaxType,
)


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    context = {
        "app": "configuration",
        "page": request_path[1],
        "model": request_path[0],
    }
    return context


# region Cuenta


@login_required
def cuenta_index_view(request):
    context = get_context_data(request)
    return render(request, "index.html", context)


@login_required
def cuenta_list_view(request):
    queryset = Cuenta.objects.all()
    context = {
        "cuenta_list": queryset,
        "capitulo_list": CapituloChoices.labels,
        "rubro_list": Rubro.objects.all(),
        "subrubro_list": Subrubro.objects.all(),
    }
    return render(request, "accounting/cuenta_list.html", context)


@login_required
def cuenta_create_view(request):
    form = CuentaCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cuenta creada con éxito!")
                return HttpResponse(
                    status=204, headers={"HX-Trigger": "cuentaListChanged"}
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    messages.error(
                        request,
                        "Ya existe una cuenta con el nombre y subrubro elegido.",
                    )
                    return HttpResponse(status=204)
    return render(request, "accounting/cuenta_form.html", context)


# endregion
# region TaxType


@login_required
def tax_type_index_view(request):
    context = get_context_data(request)
    return render(request, "index.html", context)


@login_required
def tax_type_list_view(request):
    queryset = TaxType.objects.all()
    context = {
        "tax_type_list": queryset,
    }
    return render(request, "accounting/tax_type_list.html", context)


@login_required
def tax_type_create_view(request):
    form = TaxTypeCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Impuesto creado con éxito!")
                return HttpResponse(
                    status=204, headers={"HX-Trigger": "tax_typeListChanged"}
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    messages.error(
                        request,
                        "Ya existe un impuesto con el nombre y porcentaje ingresados.",
                    )
                    return HttpResponse(status=204)
    return render(request, "accounting/tax_type_form.html", context)


@login_required
def tax_type_update_view(request, pk):
    tax_type = get_object_or_404(TaxType, pk=pk)
    form = TaxTypeCreateForm(request.POST or None, instance=tax_type)
    context = {
        "tax_type": tax_type,
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Impuesto modificado con éxito!")
                return HttpResponse(
                    status=204, headers={"HX-Trigger": "tax_typeListChanged"}
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    messages.error(
                        request,
                        "Ya existe un impuesto con el nombre y porcentaje ingresados.",
                    )
                    return HttpResponse(status=204)
    return render(request, "accounting/tax_type_form.html", context)


@login_required
def tax_type_delete_view(request, pk):
    tax_type = get_object_or_404(TaxType, pk=pk)
    context = get_context_data(request)
    context["object"] = tax_type
    if request.method == "POST":
        try:
            tax_type.delete()
            messages.success(request, "Impuesto eliminado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "tax_typeListChanged"}
            )
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el impuesto porque está relacionado a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# endregion
# region Asiento


@login_required
def asiento_index_view(request):
    context = get_context_data(request)
    context["search_text"] = "Buscar por fecha"
    return render(request, "index.html", context)


@login_required
def asiento_list_view(request):
    queryset = Asiento.objects.all()
    context = {
        "asiento_list": queryset,
    }
    return render(request, "accounting/asiento_list.html", context)


@login_required
def asiento_create_view(request):
    if request.method == "POST":
        asiento = Asiento(create_date=timezone.now().date())
        cuenta = request.POST.getlist("cuenta")
        debe = request.POST.getlist("debe")
        haber = request.POST.getlist("haber")
        total_debe = 0
        total_haber = 0
        for a, b, c in zip(cuenta, debe, haber):
            total_debe += int(b)
            total_haber += int(c)
            if not total_debe == total_haber:
                messages.warning(
                    request,
                    "La suma total de las columnas de debe y haber deben ser iguales.",
                )
                return HttpResponse(status=204)
            Entry.objects.create(asiento=asiento, cuenta_id=a, debe=b, haber=c)
        asiento.save()
        messages.success(request, "Asiento creado con éxito!")
        return HttpResponse(status=204, headers={"HX-Trigger": "asientoListChanged"})
    return render(request, "accounting/asiento_form.html")


@login_required
def entry_create_view(request):
    form = EntryCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, "accounting/entry_inline_form.html", context)


# endregion

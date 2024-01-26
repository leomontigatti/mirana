from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from inventory.forms import ServiceTypeCreateForm, StockAdjustmentForm
from inventory.models import (
    Bathroom,
    ServiceType,
    ServiceTypeMovement,
    StockMovement,
    StockStatusChoices,
    Workshop,
)
from main.views import is_not_operator


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    return {
        "app": "inventory",
        "page": request_path[1],
        "model": request_path[0],
    }


# region ServiceType


@login_required
@user_passes_test(is_not_operator)
def service_type_list_view(request):
    context = get_context_data(request)
    queryset = ServiceType.objects.all()
    filter_options = {
        "is_active": ((True, "Activo"), (False, "Inactivo")),
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}
    search_input = filter_kwargs.get("search_input", "")

    if search_input:
        queryset = ServiceType.objects.filter(Q(description__icontains=search_input))
    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        queryset = ServiceType.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["filter_options"] = filter_options
    context["search_input"] = search_input
    context["search_text"] = "Buscar por descripción..."
    context["page_obj"] = page_obj
    return render(request, "inventory/service_type_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def service_type_create_view(request):
    context = get_context_data(request)
    form = ServiceTypeCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.is_active = True
        form.instance.can_be_updated = True

        try:
            instance = form.save()
            messages.success(request, "Servicio creado con éxito!")
            return redirect(instance.get_absolute_url())
        except IntegrityError:
            messages.error(
                request, "Ya existe un servicio con la descripción ingresada."
            )
            return redirect("servicetype_list")

    context["form"] = form
    return render(request, "inventory/service_type_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def service_type_update_view(request, pk):
    if pk in [1, 2, 3, 4]:
        messages.error(request, "El servicio seleccionado no puede modificarse.")
        return redirect("servicetype_list")

    context = get_context_data(request)
    service_type = get_object_or_404(ServiceType, pk=pk)
    form = ServiceTypeCreateForm(request.POST or None, instance=service_type)

    if request.method == "POST" and form.is_valid():
        form.instance.is_active = True
        form.instance.can_be_updated = True
        instance = form.save()
        messages.success(request, "Servicio modificado con éxito!")
        return redirect(instance.get_absolute_url())

    context["object"] = service_type
    context["form"] = form
    return render(request, "inventory/service_type_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def service_type_detail_view(request, pk):
    context = get_context_data(request)
    service_type = get_object_or_404(ServiceType, pk=pk)
    movement_list = ServiceTypeMovement.objects.filter(service_type=service_type)

    context["object"] = service_type
    context["movement_list"] = movement_list
    return render(request, "inventory/service_type_detail.html", context)


@login_required
@user_passes_test(is_not_operator)
@require_POST
def service_type_delete_view(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)

    if service_type.pk in [1, 2, 3, 4]:
        messages.error(
            request,
            f'No se puede eliminar el tipo de servicio "{service_type.description}"',
        )
    else:
        service_type.delete()
        messages.success(request, "Tipo de servicio eliminado con éxito!")

    return redirect("servicetype_list")


@login_required
@user_passes_test(is_not_operator)
def toggle_service_type_is_active(request, pk):
    service_type = get_object_or_404(ServiceType, pk=pk)
    service_type.is_active = not service_type.is_active
    service_type.save(update_fields=["is_active"])

    return redirect(service_type.get_absolute_url())


# endregion
# region Stock


@login_required
@user_passes_test(is_not_operator)
def stock_list_view(request):
    context = get_context_data(request)
    context["bathrooms"] = {}
    context["workshops"] = {}

    filter_options = {
        "status": StockStatusChoices.choices,
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}

    if filter_kwargs:
        status = filter_kwargs.get("status", "")
        context["bathrooms"][status] = Bathroom.objects.filter(status=status).count()
        context["workshops"][status] = Workshop.objects.filter(status=status).count()
    else:
        for status in StockStatusChoices.values:
            context["bathrooms"][status] = Bathroom.objects.filter(
                status=status
            ).count()
        for status in StockStatusChoices.values:
            context["workshops"][status] = Workshop.objects.filter(
                status=status
            ).count()

    context["filter_options"] = filter_options
    return render(request, "inventory/stock_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def stock_detail_view(request, product, status):
    context = get_context_data(request)
    movement_list = StockMovement.objects.filter(
        stock=product.upper(), status=status.upper()
    )

    if product == "bathroom":
        object_list = Bathroom.objects.filter(status=status.upper())
    elif product == "workshop":
        object_list = Workshop.objects.filter(status=status.upper())

    current = object_list.count()
    form = StockAdjustmentForm(
        request.POST or None, initial={"move_amount": current}, status=status
    )

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            username=request.user.username,
            password=form.cleaned_data.get("password", ""),
        )

        if not user:
            messages.error(request, "La contraseña ingresada es incorrecta!")
            return redirect("stock_list")

        move_amount = form.cleaned_data.get("move_amount", 0)
        new_status = form.cleaned_data.get("status", "")
        reason = form.cleaned_data.get("reason", "")
        ids_qs = object_list.values("pk")[:move_amount]
        updated = object_list.filter(pk__in=ids_qs).update(status=new_status)

        StockMovement.objects.create(
            stock=product.upper(),
            status=status.upper(),
            amount=-updated,
            reason=reason,
        )
        StockMovement.objects.create(
            stock=product.upper(),
            status=new_status,
            amount=updated,
            reason=reason,
        )

        messages.success(request, "Stock modificado con éxito!")
        return redirect("stock_list")

    context["current"] = current
    context["form"] = form
    context["movement_list"] = movement_list
    context["product"] = product
    context["status"] = status
    return render(request, "inventory/stock_detail.html", context)


# endregion

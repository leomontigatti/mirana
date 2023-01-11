from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from configuration.forms import (
    OperatorCreateForm,
    PaymentMethodCreateForm,
    TaskCreateForm,
)
from configuration.models import Operator, PaymentMethod, Task


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    context = {
        "app": "configuration",
        "page": request_path[1],
        "model": request_path[0],
    }
    return context


# region Operator


@login_required
def operator_index_view(request):
    context = get_context_data(request)
    context["search_text"] = "Buscar por usuario, nombre o apellido."
    return render(request, "index.html", context)


@login_required
def operator_list_view(request):
    queryset = Operator.objects.all()
    search_input = request.POST.get("search_input") or ""
    context = {
        "operator_list": queryset,
        "search_input": search_input,
    }
    if search_input:
        filtered_queryset = queryset.filter(
            Q(user__username__icontains=search_input)
            | Q(user__first_name__icontains=search_input)
            | Q(user__last_name__icontains=search_input)
        )
        context["operator_list"] = filtered_queryset
    return render(request, "configuration/operator_list.html", context)


@login_required
def operator_create_view(request):
    form = OperatorCreateForm(request.POST or None)
    context = {
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            Operator.objects.create(user=user)
            messages.success(request, "Operario creado con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "operatorListChanged"}
            )
    return render(request, "configuration/operator_form.html", context)


@login_required
def operator_detail_view(request, pk=None):
    operator = get_object_or_404(Operator, pk=pk)
    context = get_context_data(request)
    context["operator"] = operator
    return render(request, "configuration/operator_detail.html", context)


@login_required
def operator_is_active(request, pk=None):
    operator = get_object_or_404(Operator, pk=pk)
    operator.user.is_active = not operator.user.is_active
    operator.user.save()
    return HttpResponse(status=204)


# endregion
# region Task


TASK_ACTIONS = {
    "on_way_placing_bathroom": {
        "action": "Baño: en camino a colocar",
        "message": "El operario está en camino a colocar el/los baños.",
    },
    "on_way_cleaning_bathroom": {
        "action": "Baño: en camino a limpiar",
        "message": "El operario está en camino a limpiar el/los baños.",
    },
    "on_way_removing_bathroom": {
        "action": "Baño: en camino a retirar",
        "message": "El operario está en camino a retirar el/los baños.",
    },
    "bathroom_placed": {
        "action": "Baño: colocación",
        "message": "El/los baños ya están colocados.",
    },
    "bathroom_cleaned": {
        "action": "Baño: limpieza",
        "message": "El/los baños ya están limpios.",
    },
    "bathroom_not_cleaned": {
        "action": "Baño: NO limpieza",
        "message": "El/los baños no pudieron limpiarse. Por favor comunicate con nosotros.",
    },
    "bathroom_removed": {
        "action": "Baño: retiro",
        "message": "El/los baños ya fueron retirados.",
    },
    "on_way_placing_workshop": {
        "action": "Obrador: en camino a colocar",
        "message": "El operario está en camino a colocar el/los obradores.",
    },
    "on_way_removing_workshop": {
        "action": "Obrador: en camino a retirar",
        "message": "El operario está en camino a retirar el/los obradores.",
    },
    "workshop_placed": {
        "action": "Obrador: colocación",
        "message": "El/los obradores ya están colocados.",
    },
    "workshop_removed": {
        "action": "Obrador: retiro",
        "message": "El/los obradores ya fueron retirados.",
    },
    "income_payment": {"action": "Cobrar y generar recibo"},
}


def send_action_whatsapp(phone_number, message):
    pass


@login_required
def task_index_view(request):
    context = get_context_data(request)
    return render(request, "index.html", context)


@login_required
def task_list_view(request, pk=None):
    queryset = Task.objects.all()
    context = {
        "task_list": queryset,
    }
    if pk:
        operator = Operator.objects.get(pk=pk)
        filtered_queryset = queryset.filter(operator=operator)
        context["task_list"] = filtered_queryset
        context["operator"] = operator
        return render(request, "configuration/operator_task_list.html", context)
    return render(request, "configuration/task_list.html", context)


@login_required
def task_create_view(request, pk=None):
    form = TaskCreateForm(request.POST or None)
    context = {"form": form}
    if pk:
        operator = get_object_or_404(Operator, pk=pk)
        form.initial = {"operator": operator}
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Tarea creada con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "taskListChanged"})
    return render(request, "configuration/task_form.html", context)


@login_required
def task_inline_create_view(request):
    form = TaskCreateForm(request.POST or None)
    context = {"form": form}
    return render(request, "configuration/task_inline_form.html", context)


@login_required
def task_inline_update_view(request, pk=None):
    task = get_object_or_404(Task, pk=pk)
    form = TaskCreateForm(request.POST or None, instance=task)
    context = {"form": form}
    return render(request, "configuration/task_inline_form.html", context)


@login_required
def task_update_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskCreateForm(request.POST or None, instance=task)
    context = {
        "task": task,
        "form": form,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Tarea modificada con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "taskListChanged"})
    return render(request, "configuration/task_form.html", context)


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    context = get_context_data(request)
    context["object"] = task
    if request.method == "POST":
        try:
            task.delete()
            messages.success(request, "Tarea eliminada con éxito!")
            return HttpResponse(status=204, headers={"HX-Trigger": "taskListChanged"})
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar la tarea porque está relacionada a otro registro.",
            )
            return HttpResponse(status=204)
    return render(request, "delete.html", context)


# @login_required
# def task_actions(request):
#     operator_task = get_object_or_404(OperatorTask, pk=request.POST.get("task_id"))
#     action = request.POST.get("task_action")
#     if not action == "income_payment":
#         if action == "bathroom_placed":
#             # for product in operator_task.hiring.products.all():
#             #     if not product.product_type.measurement_unit == MeasurementUnitChoices.SERVICE:
#             #         product.product_type.amount
#             operator_task.hiring.is_placed = True
#             operator_task.hiring.save()
#         send_action_whatsapp(operator_task.hiring.phone_number, TASK_ACTIONS.get(action).get("message"))
#         messages.success(request, "Novedad enviada correctamente.")
#         return redirect("operator_task_detail", operator_task.id)
#     else:
#         # Create an income payment and send it via Whatsapp.
#         return redirect("income_payment_create", operator_task.hiring.customer.id)


# @login_required
# def toggle_is_done(request, pk):
#     operator_task = OperatorTask.objects.get(pk=pk)
#     operator_task.is_done = not operator_task.is_done
#     operator_task.save()
#     return redirect("home")


# endregion
# region PaymentMethod


@login_required
def payment_method_index_view(request):
    context = get_context_data(request)
    return render(request, "index.html", context)


@login_required
def payment_method_list_view(request):
    queryset = PaymentMethod.objects.all()
    context = {
        "payment_method_list": queryset,
    }
    return render(request, "configuration/payment_method_list.html", context)


@login_required
def payment_method_create_view(request):
    form = PaymentMethodCreateForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Forma de pago creada con éxito!")
            return HttpResponse(
                status=204, headers={"HX-Trigger": "payment_methodListChanged"}
            )
    return render(request, "configuration/payment_method_form.html", context)


# @login_required
# def payment_method_update_view(request, pk):
#     payment_method = get_object_or_404(PaymentMethod, pk=pk)
#     form = PaymentMethodCreateForm(request.POST or None, instance=payment_method)
#     context = {
#         "payment_method": payment_method,
#         "form": form,
#     }
#     if form.is_valid():
#         form.save()
#         return HttpResponse(status=204, headers={'HX-Trigger': 'paymentMethodListChanged'})
#     return render(request, "configuration/payment_method_form.html", context)


# @login_required
# def payment_method_is_active(request, pk):
#     payment_method = PaymentMethod.objects.get(pk=pk)
#     payment_method.is_active = not payment_method.is_active
#     payment_method.save()
#     return HttpResponse(status=204)


# endregion

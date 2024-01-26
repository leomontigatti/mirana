from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from configuration.forms import (
    TASK_ACTIONS,
    OperatorChangePasswordForm,
    OperatorCreateForm,
    PaymentMethodCreateForm,
    TaskActionsForm,
    TaskCreateForm,
)
from configuration.models import Operator, PaymentMethod, Task, TaskPriorityChoices
from main.tasks import send_whatsapp_message
from main.views import is_not_operator


def get_context_data(request):
    request_path = request.path.strip("/").split("/")
    return {
        "app": "configuration",
        "page": request_path[1],
        "model": request_path[0],
    }


# def get_delete_error_message(instance):
#     model_name = instance._meta.verbose_name.lower()
#     article = "el" if model_name == "forma de pago" else "la"
#     suffix = "o" if model_name == "forma de pago" else "a"
#     try:
#         operator = instance.operator
#         return f"No se puede eliminar {article} {model_name} porque está relacionad{suffix} al operario {operator}."
#     except Operator.DoesNotExist:
#         hiring_id = instance.hiring.id
#         return f"No se puede eliminar {article} {model_name} porque está relacionad{suffix} a la contratación {hiring_id}."


# region Operator


@login_required
@user_passes_test(is_not_operator)
def operator_list_view(request):
    context = get_context_data(request)
    search_text = "Buscar por usuario, nombre o apellido..."
    search_input = request.GET.get("search_input", "").strip()
    queryset = Operator.objects.all()

    if search_input:
        queryset = Operator.objects.filter(
            Q(user__username__icontains=search_input)
            | Q(user__first_name__icontains=search_input)
            | Q(user__last_name__icontains=search_input)
        )

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["search_text"] = search_text
    context["search_input"] = search_input
    context["page_obj"] = page_obj
    return render(request, "configuration/operator_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def operator_create_view(request):
    context = get_context_data(request)
    form = OperatorCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        operator = Operator.objects.create(user=user)
        messages.success(request, "Operario creado con éxito!")
        return redirect(operator.get_absolute_url())

    context["form"] = form
    return render(request, "configuration/operator_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def operator_detail_view(request, pk):
    context = get_context_data(request)
    operator = get_object_or_404(Operator, pk=pk)
    queryset = Task.objects.filter(operator=operator, is_done=False)
    form = OperatorChangePasswordForm(operator.user, request.POST or None)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["object"] = operator
    context["page_obj"] = page_obj
    context["form"] = form
    return render(request, "configuration/operator_detail.html", context)


@login_required
@user_passes_test(is_not_operator)
def toggle_operator_is_active(request, pk):
    operator = get_object_or_404(Operator, pk=pk)
    operator.user.is_active = not operator.user.is_active
    operator.user.save(update_fields=["is_active"])

    return redirect(operator.get_absolute_url())


@login_required
@user_passes_test(is_not_operator)
@require_POST
def operator_password_change(request, pk):
    operator = get_object_or_404(Operator, pk=pk)
    form = OperatorChangePasswordForm(operator.user, request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Contraseña modificada con éxito!")
    else:
        for error in form.errors.values():
            messages.error(request, error.as_text())

    return redirect(operator.get_absolute_url())


# endregion
# region Task


@login_required
def task_list_view(request, date_str=""):
    context = get_context_data(request)
    # queryset: QuerySet = Task.objects.filter(start_date=timezone.now().date())
    queryset = Task.objects.all()
    filter_options = {
        "date": (
            ("today", "Hoy"),
            ("last_week", "Semana pasada"),
        ),
        "priority": TaskPriorityChoices.choices,
        "is_done": ((True, "Completa"), (False, "Incompleta")),
        "operator": Operator.objects.filter(user__is_active=True),
    }
    filter_kwargs = {key: value for key, value in request.GET.items() if value}

    if date_str:
        try:
            search_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if is_not_operator(request.user):
                queryset = Task.objects.filter(
                    start_date=search_date,
                )
            else:
                queryset = Task.objects.filter(
                    start_date=search_date,
                    operator=request.user.operator,  # type: ignore
                )
            context["search_date"] = search_date
        except ValueError:
            messages.warning(
                request, "Seleccionar un día para mostrar las tareas asignadas."
            )
            return redirect("home")

    # if search_input:
    #     try:
    #         get_date = datetime.strptime(search_input, "%d/%m/%Y").date()
    #         queryset = Task.objects.filter(start_date=get_date)
    #     except ValueError:
    #         try:
    #             get_date = datetime.strptime(search_input, "%d/%m").date()
    #             queryset = Task.objects.filter(start_date=get_date)
    #         except ValueError:
    #             queryset = Task.objects.filter(hiring_id=search_input)

    elif filter_kwargs:
        if "page" in filter_kwargs:
            del filter_kwargs["page"]
        if "date" in filter_kwargs:
            today = timezone.now().date()
            if filter_kwargs.get("date", "") == "today":
                queryset = Task.objects.filter(start_date=today)
            else:
                last_week = today - timedelta(days=today.weekday() + 7)
                queryset = Task.objects.filter(
                    start_date__gte=last_week, start_date__lte=today
                )
        else:
            queryset = Task.objects.filter(**filter_kwargs)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        selected_action = request.POST.get("selected_action", "")
        selected_tasks = request.POST.getlist("selected_tasks")
        tasks_queryset = Task.objects.filter(pk__in=selected_tasks)
        if selected_action == "realizada":
            tasks_queryset.update(is_done=True)
        elif selected_action:
            operator = get_object_or_404(Operator, pk=selected_action)
            tasks_queryset.update(operator=operator)

    operator_list = Operator.objects.filter(user__is_active=True)

    context["filter_options"] = filter_options
    # context["search_input"] = search_input
    # context["search_text"] = "Buscar por fecha de inicio o ID de contratación..."
    context["page_obj"] = page_obj
    context["operator_list"] = operator_list
    return render(request, "configuration/task_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def task_create_view(request, pk=0):
    context = get_context_data(request)
    operator = get_object_or_404(Operator, pk=pk) if pk else None
    form = TaskCreateForm(request.POST or None, initial={"operator": operator})

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea creada con éxito!")
        return redirect(operator.get_absolute_url() if operator else "task_list")

    context["form"] = form
    return render(request, "configuration/task_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def task_update_view(request, pk):
    context = get_context_data(request)
    task = get_object_or_404(Task, pk=pk)
    form = TaskCreateForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea modificada con éxito!")
        return redirect("task_list")

    context["object"] = task
    context["form"] = form
    return render(request, "configuration/task_form.html", context)


@login_required
@user_passes_test(is_not_operator)
@require_POST
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()

    messages.success(request, "Tarea eliminada con éxito!")
    return redirect("task_list")


@login_required
def task_detail_view(request, pk):
    context = get_context_data(request)
    task = get_object_or_404(Task, pk=pk)
    form = TaskActionsForm(request.POST or None, task=task)

    if request.method == "POST" and form.is_valid():
        selected_action = form.cleaned_data.get("action", "")
        if selected_action == "income_payment":
            return redirect(
                "incomepayment_create",
                pk=task.hiring.customer.pk if task.hiring else 0,
            )
        elif selected_action == "completed":
            task.is_done = True
            task.save()

            if task.service:
                task.update_or_create_stock_movement()

            if task.hiring:
                task.update_hiring_status()
        else:
            selected_task_message = TASK_ACTIONS[selected_action]["message"]
            send_whatsapp_message(
                task.hiring.customer.phone_number, selected_task_message
            )
            messages.success(request, "Mensaje de WhatsApp enviado con éxito!")

        return redirect(task.get_absolute_url())

    context["object"] = task
    context["form"] = form
    return render(request, "configuration/task_detail.html", context)


# endregion
# region PaymentMethod


@login_required
@user_passes_test(is_not_operator)
def payment_method_list_view(request):
    context = get_context_data(request)
    queryset = PaymentMethod.objects.all()

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page", "")
    page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj
    return render(request, "configuration/payment_method_list.html", context)


@login_required
@user_passes_test(is_not_operator)
def payment_method_create_view(request):
    context = get_context_data(request)
    form = PaymentMethodCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.is_active = True
        form.save()
        messages.success(request, "Forma de pago creada con éxito!")
        return redirect("paymentmethod_list")

    context["form"] = form
    return render(request, "configuration/payment_method_form.html", context)


@login_required
@user_passes_test(is_not_operator)
def payment_method_detail_view(request, pk):
    context = get_context_data(request)
    payment_method = get_object_or_404(PaymentMethod, pk=pk)

    context["object"] = payment_method
    return render(request, "configuration/payment_method_detail.html", context)


@login_required
@user_passes_test(is_not_operator)
def toggle_payment_method_is_active(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk)
    payment_method.is_active = not payment_method.is_active
    payment_method.save(update_fields=["is_active"])

    return redirect(payment_method.get_update_url())


# endregion

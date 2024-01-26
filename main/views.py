import json
import os
from calendar import LocaleHTMLCalendar
from datetime import date
from itertools import groupby

from decouple import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from configuration.models import Task, TaskPriorityChoices
from income.models import Budget, Customer, Hiring
from main.tasks import handle_webhook


def is_not_operator(user):
    return not hasattr(user, "operator")


def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    context = {"form": form, "app": "login"}

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data.get("username", ""),
            password=form.cleaned_data.get("password", ""),
        )
        if user:
            login(request, user)
            return redirect("home")

    return render(request, "registration/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


class TasksHTMLCalendar(LocaleHTMLCalendar):
    def __init__(self, tasks, year, month, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = self.group_by_day(tasks)
        self.year, self.month = year, month

    def group_by_day(self, tasks):
        def field(task):
            return task.start_date.day

        return dict([(day, list(items)) for day, items in groupby(tasks, field)])

    def formatmonth(self, *args, **kwargs):
        kwargs["theyear"] = self.year
        kwargs["themonth"] = self.month

        return super().formatmonth(*args, **kwargs)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass: str = self.cssclasses[weekday]
            cssclass += " border text-start"
            if timezone.now().date() == date(self.year, self.month, day):
                cssclass += " bg-body-secondary"
            body = []
            task_list_url = reverse(
                "task_list",
                kwargs={"date_str": f"{self.year}-{self.month}-{day}"},
            )
            body.append(
                f'<a href="{task_list_url}" class="text-decoration-none h-100 w-100 d-inline-block">'
            )
            body.append(f"{day}<br>")

            if day in self.tasks:
                urgent, medium, normal, completed = 0, 0, 0, 0
                for task in self.tasks.get(day):
                    if task.is_done:
                        completed += 1
                    elif task.priority == TaskPriorityChoices.URGENT:
                        urgent += 1
                    elif task.priority == TaskPriorityChoices.MEDIUM:
                        medium += 1
                    elif task.priority == TaskPriorityChoices.NORMAL:
                        normal += 1

                (
                    body.append(
                        f'<span class="badge text-bg-success">{completed}</span>'
                    )
                    if completed
                    else None
                )
                (
                    body.append(f'<span class="badge text-bg-warning">{medium}</span>')
                    if medium
                    else None
                )
                (
                    body.append(f'<span class="badge text-bg-danger">{urgent}</span>')
                    if urgent
                    else None
                )
                (
                    body.append(f'<span class="badge text-bg-light">{normal}</span>')
                    if normal
                    else None
                )
                body.append("</a>")

            return self.day_cell(cssclass, "".join(body))
        return self.day_cell("noday", "&nbsp;")

    def day_cell(self, cssclass, body):
        return f'<td class="{cssclass}">{body}</td>'

    def formatmonthname(self, theyear, themonth, withyear):
        month_name = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }
        body = ['<ul class="pagination justify-content-center">']

        if withyear:
            month_year = f"{month_name.get(themonth)} {theyear}"
        else:
            month_year = f"{month_name.get(themonth)}"

        if themonth == 1:
            body.append('<li class="page-item active"><a class="page-link" href="#">')
            body.append(f"{month_year}<a></li>")
            body.append('<li class="page-item">')
            body.append(f'<a class="page-link" href="?page={themonth + 1}">')
            body.append(f"{month_name.get(themonth + 1)}<a></li>")
            body.append(
                '<li class="page-item"><a class="page-link" href="?page=12">&raquo;</a></li>'
            )
        elif themonth == 12:
            body.append(
                '<li class="page-item"><a class="page-link" href="?page=1">&laquo;</a></li>'
            )
            body.append('<li class="page-item">')
            body.append(f'<a class="page-link" href="?page={themonth - 1}">')
            body.append(f"{month_name.get(themonth - 1)}<a></li>")
            body.append('<li class="page-item active"><a class="page-link" href="#">')
            body.append(f"{month_year}<a></li>")
        else:
            body.append(
                '<li class="page-item"><a class="page-link" href="?page=1">&laquo;</a></li>'
            )
            body.append('<li class="page-item">')
            body.append(f'<a class="page-link" href="?page={themonth - 1}">')
            body.append(f"{month_name.get(themonth - 1)}<a></li>")
            body.append('<li class="page-item active"><a class="page-link" href="#">')
            body.append(f"{month_year}<a></li>")
            body.append('<li class="page-item">')
            body.append(f'<a class="page-link" href="?page={themonth + 1}">')
            body.append(f"{month_name.get(themonth + 1)}<a></li>")
            body.append(
                '<li class="page-item"><a class="page-link" href="?page=12">&raquo;</a></li>'
            )
        body.append("</ul>")

        return f'<tr><th colspan="7">{"".join(body)}</th></tr>'


@login_required
def home(request):
    context = {"app": "home"}

    try:
        page_number = int(request.GET.get("page", timezone.now().month))
        if not 0 < page_number < 13:
            messages.error(
                request, "El número del mes debe ser mayor a 0 y menor a 13."
            )
            return redirect("home")
    except ValueError:
        messages.error(request, "El número del mes debe ser numérico.")
        return redirect("home")

    tasks_list = Task.objects.filter(
        start_date__month=page_number,
        start_date__year=timezone.now().year,
    )

    if is_not_operator(request.user):
        calendar = TasksHTMLCalendar(
            tasks_list, timezone.now().year, page_number, 6, "es_AR.UTF-8"
        )
    else:
        operator_tasks = tasks_list.filter(operator=request.user.operator)
        calendar = TasksHTMLCalendar(
            operator_tasks, timezone.now().year, page_number, 6, "es_AR.UTF-8"
        )

    paginator = Paginator(range(12), 1)
    page_obj = paginator.get_page(page_number)

    context["calendar"] = mark_safe(calendar.formatmonth())
    context["page_obj"] = page_obj
    return render(request, "home.html", context)


@login_required
def render_map(request):
    context = {
        "lat": "-31.420972762427905",
        "lng": "-64.49906945228577",
        "maps_api_key": config("MAPS_API_KEY"),
    }
    return render(request, "map.html", context)


@login_required
def get_location(request, model, pk):
    context = {"maps_api_key": config("MAPS_API_KEY")}

    if model == "budget":
        object = get_object_or_404(Budget, pk=pk)
    elif model == "hiring":
        object = get_object_or_404(Hiring, pk=pk)

    context["object"] = object
    context["lat"] = object.lat
    context["lng"] = object.lng
    return render(request, "map.html", context)


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode", "")
        verify_token = request.GET.get("hub.verify_token", "")
        challenge = request.GET.get("hub.challenge", "")

        if mode == "subscribe" and verify_token == config("WEBHOOK_VERIFY_TOKEN"):
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse("error", status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        if "object" in data and "entry" in data:
            if data["object"] == "whatsapp_business_account":
                handle_webhook(data)
                return HttpResponse(data, status=403)
        return HttpResponse("error", status=403)


def link_callback(uri, rel):
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    if not os.path.isfile(path):
        raise Exception("media URI must start with %s or %s" % (sUrl, mUrl))
    return path


def render_pdf_view(request, template_path, context):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response

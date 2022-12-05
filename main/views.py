from calendar import LocaleHTMLCalendar
from datetime import date

from decouple import config

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic.base import ContextMixin

from income.models import Customer, Receipt
from inventory.models import Warehouse
from main.forms import UserLoginForm


class CustomContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        request_path = self.request.path.strip("/").split("/")
        extra_context = {
            "app": self.model._meta.app_label,
            "page": request_path[1],
            "model": request_path[0],
        }
        return {**super().get_context_data(**kwargs), **extra_context}


class CustomHTMLCalendar(LocaleHTMLCalendar):
    cssclasses = [style + " border" for style in LocaleHTMLCalendar.cssclasses]

    def formatmonth(self, *args, **kwargs):
        kwargs["theyear"] = date.today().year
        kwargs["themonth"] = date.today().month
        return super().formatmonth(*args, **kwargs)


@login_required
def home(request):
    """
    Redirect the :model:`auth.User` depending on its type.
    **Context:**
    ``app``
        The app name for the html title.
    **Template:**
    :template:`home.html`.
    """

    calendar = CustomHTMLCalendar(locale="es_AR").formatmonth()
    extra_context = {
        "app": "home",
        "calendar": mark_safe(calendar),
        "today": date.today().day,
    }

    if request.user.is_superuser:
        return redirect(reverse_lazy("admin:index"))
    return render(request, "home.html", extra_context)


@login_required
def render_map(request):
    context = {
        "coords": "(-31.420972762427905, -64.49906945228577)",
        "maps_api_key": config("MAPS_API_KEY"),
    }
    return render(request, "map.html", context)


@login_required
def get_location(request, pk):
    request_path = request.path.strip("/").split("/")
    coords = ""
    if request_path[0] == "customer":
        coords = Customer.objects.get(pk=pk).location
    elif request_path[0] == "warehouse":
        coords = Warehouse.objects.get(pk=pk).location
    else:
        coords = Receipt.objects.get(pk=pk).location
    context = {
        "coords": coords,
        "maps_api_key": config("MAPS_API_KEY"),
    }
    return render(request, "get_location.html", context)


class UserLogin(LoginView):

    success_url = "home"
    form_class = UserLoginForm
    extra_context = {"app": "login"}

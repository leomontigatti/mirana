import json
from calendar import LocaleHTMLCalendar
from datetime import date

from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin

from configuration.models import Operator
from income.models import Customer, Hiring
from inventory.models import Warehouse


def is_operator(user):
    """
    Check if the :model:`auth.User` is an Operator instance.
    """
    try:
        user.operator
        return True
    except ObjectDoesNotExist:
        return False


class CustomContextMixin(LoginRequiredMixin, UserPassesTestMixin, ContextMixin):
    """
    Check if the :model:`auth.User` is authenticated and if it's superuser or operator.
    """

    def test_func(self):
        user = self.request.user
        if is_operator(user):
            return False
        return True

    def handle_no_permission(self):
        messages.warning(self.request, "No tenés permisos para realizar esa acción.")
        return redirect("home")

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
    if request.user.is_superuser:
        return redirect(reverse_lazy("admin:index"))
    elif is_operator(request.user):
        context = {
            "app": "operator_home",
            # "operator_tasks": OperatorTask.objects.filter(
            #     operator=request.user.operator,
            #     # date=timezone.now().date(),
            # )
        }
        return render(request, "operator_home.html", context)
    else:
        # hiring_coords = [hiring.location for hiring in Hiring.objects.all()]
        # print(json.dumps(hiring_coords))
        hiring_json = serializers.serialize(
            "json", Hiring.objects.all(), fields=("location")
        )
        context = {
            "app": "home",
            "coords": "(-31.420972762427905, -64.49906945228577)",
            "maps_api_key": config("MAPS_API_KEY"),
            "hiring_json": hiring_json,
        }
        return render(request, "home.html", context)


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
    # else:
    #     coords = Receipt.objects.get(pk=pk).location
    context = {
        "coords": coords,
        "maps_api_key": config("MAPS_API_KEY"),
    }
    return render(request, "get_location.html", context)

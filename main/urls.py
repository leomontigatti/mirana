from django.urls import path

from main import views

urlpatterns = [
    path("", views.home, name="home"),
    path("operator/", views.home, name="operator_home"),
    path("map/", views.render_map, name="render_map"),
]

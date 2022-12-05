from django.urls import path

from main import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.UserLogin.as_view(), name="login"),
    path("map/", views.render_map, name="render_map"),
]

from django.urls import path

from main import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("map/", views.render_map, name="render_map"),
    path("location/<str:model>/<int:pk>/", views.get_location, name="get_location"),
    path("webhook/", views.whatsapp_webhook, name="whatsapp_webhook"),  # type: ignore
]

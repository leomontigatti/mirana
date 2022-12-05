from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounting.urls")),
    path("", include("income.urls")),
    path("", include("inventory.urls")),
    path("", include("main.urls")),
]

from django.urls import include, path

from inventory import views
from main.views import get_location

urlpatterns = [
    path(
        "servicetype/",
        include(
            [
                path("list/", views.service_type_list_view, name="servicetype_list"),
                path(
                    "create/", views.service_type_create_view, name="servicetype_create"
                ),
                path(
                    "update/<int:pk>/",
                    views.service_type_update_view,
                    name="servicetype_update",
                ),
                path(
                    "detail/<int:pk>/",
                    views.service_type_detail_view,
                    name="servicetype_detail",
                ),
                path(
                    "delete/<int:pk>/",
                    views.service_type_delete_view,
                    name="servicetype_delete",
                ),
                path(
                    "is_active/<int:pk>/",
                    views.toggle_service_type_is_active,
                    name="toggle_servicetype_is_active",
                ),
            ],
        ),
    ),
    path(
        "stock/",
        include(
            [
                path("list/", views.stock_list_view, name="stock_list"),
                path(
                    "detail/<str:product>/<str:status>/",
                    views.stock_detail_view,
                    name="stock_detail",
                ),
            ],
        ),
    ),
]

from django.urls import include, path

from inventory import views

urlpatterns = [
    path(
        "service_type/",
        include(
            [
                path(
                    "index/", views.service_type_index_view, name="service_type_index"
                ),
                # path("list/<str:option>/<str:value>/", views.service_type_list_view, name="service_type_list"),
                path("list/", views.service_type_list_view, name="service_type_list"),
                path(
                    "create/",
                    views.service_type_create_view,
                    name="service_type_create",
                ),
                path(
                    "update/<int:pk>/",
                    views.service_type_update_view,
                    name="service_type_update",
                ),
                path(
                    "delete/<int:pk>/",
                    views.service_type_delete_view,
                    name="service_type_delete",
                ),
            ],
        ),
    ),
    path(
        "warehouse/",
        include(
            [
                path("index/", views.warehouse_index_view, name="warehouse_index"),
                path("list/", views.warehouse_list_view, name="warehouse_list"),
                path("create/", views.warehouse_create_view, name="warehouse_create"),
                path(
                    "update/<int:pk>/",
                    views.warehouse_update_view,
                    name="warehouse_update",
                ),
                path(
                    "delete/<int:pk>/",
                    views.warehouse_delete_view,
                    name="warehouse_delete",
                ),
            ],
        ),
    ),
    path(
        "stock/",
        include(
            [
                path("index/", views.stock_index_view, name="stock_index"),
                path("list/", views.stock_list_view, name="stock_list"),
                path("create/", views.stock_create_view, name="stock_create"),
                path("update/<int:pk>/", views.stock_update_view, name="stock_update"),
                path("delete/<int:pk>/", views.stock_delete_view, name="stock_delete"),
            ],
        ),
    ),
]

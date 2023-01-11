from django.urls import include, path

from accounting import views

urlpatterns = [
    path(
        "cuenta/",
        include(
            [
                path("index/", views.cuenta_index_view, name="cuenta_index"),
                path("list/", views.cuenta_list_view, name="cuenta_list"),
                path("create/", views.cuenta_create_view, name="cuenta_create"),
            ]
        ),
    ),
    path(
        "tax_type/",
        include(
            [
                path("index/", views.tax_type_index_view, name="tax_type_index"),
                path("list/", views.tax_type_list_view, name="tax_type_list"),
                path("create/", views.tax_type_create_view, name="tax_type_create"),
                path(
                    "update/<int:pk>/",
                    views.tax_type_update_view,
                    name="tax_type_update",
                ),
                path(
                    "delete/<int:pk>/",
                    views.tax_type_delete_view,
                    name="tax_type_delete",
                ),
            ]
        ),
    ),
    path(
        "asiento/",
        include(
            [
                path("index/", views.asiento_index_view, name="asiento_index"),
                path("list/", views.asiento_list_view, name="asiento_list"),
                path("create/", views.asiento_create_view, name="asiento_create"),
            ]
        ),
    ),
    path(
        "entry/",
        include(
            [
                path("create/", views.entry_create_view, name="entry_create"),
            ]
        ),
    ),
]

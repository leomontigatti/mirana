from django.urls import include, path

from accounting import views

urlpatterns = [
    path(
        "cuenta/",
        include(
            [
                path("list/", views.cuenta_list_view, name="cuenta_list"),
                path("create/", views.cuenta_create_view, name="cuenta_create"),
            ]
        ),
    ),
    path(
        "taxtype/",
        include(
            [
                path("list/", views.tax_type_list_view, name="taxtype_list"),
                path("create/", views.tax_type_create_view, name="taxtype_create"),
                path(
                    "update/<int:pk>/",
                    views.tax_type_update_view,
                    name="taxtype_update",
                ),
                path(
                    "delete/<int:pk>/",
                    views.tax_type_delete_view,
                    name="taxtype_delete",
                ),
            ]
        ),
    ),
    path(
        "asiento/",
        include(
            [
                path("list/", views.asiento_list_view, name="asiento_list"),
                path("create/", views.asiento_create_view, name="asiento_create"),
            ]
        ),
    ),
]

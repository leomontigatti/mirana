from __future__ import annotations

from django.urls import include, path

from accounting import views

urlpatterns = [
    path(
        "rubro/",
        include(
            [
                path("create/", views.RubroCreateView.as_view(), name="rubro_create"),
            ]
        ),
    ),
    path(
        "subrubro/",
        include(
            [
                path(
                    "create/",
                    views.SubrubroCreateView.as_view(),
                    name="subrubro_create",
                ),
            ]
        ),
    ),
    path(
        "cuenta/",
        include(
            [
                path("list/", views.CuentaListView.as_view(), name="cuenta_list"),
                path("create/", views.CuentaCreateView.as_view(), name="cuenta_create"),
            ]
        ),
    ),
    path(
        "taxtype/",
        include(
            [
                path("list/", views.TaxTypeListView.as_view(), name="taxtype_list"),
                path(
                    "create/", views.TaxTypeCreateView.as_view(), name="taxtype_create"
                ),
            ]
        ),
    ),
]

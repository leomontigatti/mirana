from django.urls import include, path

from income import views
from main.views import get_location

urlpatterns = [
    path(
        "customer/",
        include(
            [
                path(
                    "list/",
                    views.CustomerListView.as_view(),
                    name="customer_list",
                ),
                path(
                    "create/",
                    views.CustomerCreateView.as_view(),
                    name="customer_create",
                ),
                path(
                    "update/<int:pk>/",
                    views.CustomerUpdateView.as_view(),
                    name="customer_update",
                ),
                path(
                    "location/<int:pk>/",
                    get_location,
                    name="customer_location",
                ),
            ]
        ),
    ),
]

for app in ["budget", "hiring", "invoice"]:
    urlpatterns.append(
        path(
            f"{app}/",
            include(
                [
                    path("list/", views.ReceiptListView.as_view(), name=f"{app}_list"),
                    path(
                        "create/",
                        views.ReceiptCreateView.as_view(),
                        name=f"{app}_create",
                    ),
                    path(
                        "update/<int:pk>/",
                        views.ReceiptUpdateView.as_view(),
                        name=f"{app}_update",
                    ),
                    path(
                        "delete/<int:pk>/",
                        views.ReceiptDeleteView.as_view(),
                        name=f"{app}_delete",
                    ),
                    path(
                        "location/<int:pk>/",
                        get_location,
                        name=f"{app}_location",
                    ),
                ]
            ),
        ),
    )

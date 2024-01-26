from django.urls import include, path

from income import views

urlpatterns = [
    path(
        "customer/",
        include(
            [
                path("list/", views.customer_list_view, name="customer_list"),
                path("create/", views.customer_create_view, name="customer_create"),
                path(
                    "update/<int:pk>/",
                    views.customer_update_view,
                    name="customer_update",
                ),
                path(
                    "detail/<int:pk>/",
                    views.customer_detail_view,
                    name="customer_detail",
                ),
                path(
                    "movements/<int:pk>/",
                    views.render_customer_movements,
                    name="customer_movements",
                ),
            ]
        ),
    ),
    path(
        "budget/",
        include(
            [
                path("list/", views.budget_list_view, name="budget_list"),
                path("create/", views.budget_create_view, name="budget_create"),
                path(
                    "update/<int:pk>/", views.budget_update_view, name="budget_update"
                ),
                path(
                    "detail/<int:pk>/", views.budget_detail_view, name="budget_detail"
                ),
                path(
                    "delete/<int:pk>/", views.budget_delete_view, name="budget_delete"
                ),
                path(
                    "send_budget/<int:pk>/",
                    views.send_budget,
                    name="send_budget",
                ),
            ]
        ),
    ),
    path(
        "hiring/",
        include(
            [
                path("list/", views.hiring_list_view, name="hiring_list"),
                path("create/", views.hiring_create_view, name="hiring_create"),
                path(
                    "update/<int:pk>/", views.hiring_update_view, name="hiring_update"
                ),
                path(
                    "detail/<int:pk>/", views.hiring_detail_view, name="hiring_detail"
                ),
                path(
                    "delete/<int:pk>/", views.hiring_delete_view, name="hiring_delete"
                ),
            ]
        ),
    ),
    path(
        "salesinvoice/",
        include(
            [
                path("list/", views.sales_invoice_list_view, name="salesinvoice_list"),
                path(
                    "create/",
                    views.sales_invoice_create_view,
                    name="salesinvoice_create",
                ),
                path(
                    "update/<int:pk>/",
                    views.sales_invoice_update_view,
                    name="salesinvoice_update",
                ),
                path(
                    "detail/<int:pk>/",
                    views.sales_invoice_detail_view,
                    name="salesinvoice_detail",
                ),
            ]
        ),
    ),
    path(
        "incomepayment/",
        include(
            [
                path(
                    "list/",
                    views.payment_list_view,
                    name="incomepayment_list",
                ),
                path(
                    "create/<int:pk>/",
                    views.payment_create_view,
                    name="incomepayment_create",
                ),
                path(
                    "create/",
                    views.payment_create_view,
                    name="incomepayment_create",
                ),
                path(
                    "update/<int:pk>/",
                    views.payment_update_view,
                    name="incomepayment_update",
                ),
                path(
                    "detail/<int:pk>/",
                    views.payment_detail_view,
                    name="incomepayment_detail",
                ),
            ]
        ),
    ),
    path(
        "service/",
        include(
            [
                path(
                    "delete/<str:model>/<int:pk>/",
                    views.service_delete_view,
                    name="service_delete",
                ),
            ]
        ),
    ),
    path(
        "tax/",
        include(
            [
                path(
                    "delete/<str:model>/<int:pk>/",
                    views.tax_delete_view,
                    name="tax_delete",
                ),
            ]
        ),
    ),
]

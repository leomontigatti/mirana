from django.urls import include, path

from income import views
from main.views import get_location

urlpatterns = [
    path(
        "customer/",
        include(
            [
                path("index/", views.customer_index_view, name="customer_index"),
                path("list/", views.customer_list_view, name="customer_list"),
                path("create/", views.customer_create_view, name="customer_create"),
                path(
                    "update/<int:pk>/",
                    views.customer_update_view,
                    name="customer_update",
                ),
                path(
                    "delete/<int:pk>/",
                    views.customer_delete_view,
                    name="customer_delete",
                ),
            ]
        ),
    ),
    path(
        "budget/",
        include(
            [
                path("index/", views.budget_index_view, name="budget_index"),
                path("list/", views.budget_list_view, name="budget_list"),
                path(
                    "update_or_create/<int:pk>/",
                    views.budget_update_or_create_view,
                    name="budget_update_or_create",
                ),
                path(
                    "update_or_create/",
                    views.budget_update_or_create_view,
                    name="budget_update_or_create",
                ),
                path(
                    "create/", views.budget_create_form_view, name="budget_create_form"
                ),
                path(
                    "update/<int:pk>/",
                    views.budget_update_form_view,
                    name="budget_update_form",
                ),
                path(
                    "delete/<int:pk>/", views.budget_delete_view, name="budget_delete"
                ),
            ]
        ),
    ),
    path(
        "hiring/",
        include(
            [
                path("index/", views.hiring_index_view, name="hiring_index"),
                path("list/", views.hiring_list_view, name="hiring_list"),
                path(
                    "update_or_create/<int:pk>/",
                    views.hiring_update_or_create_view,
                    name="hiring_update_or_create",
                ),
                path(
                    "update_or_create/",
                    views.hiring_update_or_create_view,
                    name="hiring_update_or_create",
                ),
                path(
                    "create/", views.hiring_create_form_view, name="hiring_create_form"
                ),
                path(
                    "update/<int:pk>/",
                    views.hiring_update_form_view,
                    name="hiring_update_form",
                ),
                path(
                    "delete/<int:pk>/", views.hiring_delete_view, name="hiring_delete"
                ),
            ]
        ),
    ),
    path(
        "service/",
        include(
            [
                path("create/", views.service_create_view, name="service_create"),
                path(
                    "update/<int:pk>/", views.service_update_view, name="service_update"
                ),
            ]
        ),
    ),
    path(
        "tax/",
        include(
            [
                path("create/", views.tax_create_view, name="tax_create"),
                path("update/<int:pk>/", views.tax_update_view, name="tax_update"),
            ]
        ),
    ),
    path(
        "receipt/",
        include(
            [
                path(
                    "create/",
                    views.receipt_customer_create_view,
                    name="receipt_customer_create",
                ),
            ]
        ),
    ),
    # path(
    #     "income_payment/",
    #     include(
    #         [
    #             path(
    #                 "list/",
    #                 views.IncomePaymentListView.as_view(),
    #                 name="income_payment_list",
    #             ),
    #             path(
    #                 "create/",
    #                 views.IncomePaymentCreateView.as_view(),
    #                 name="income_payment_create",
    #             ),
    #             path(
    #                 "create/<int:pk>/",
    #                 views.IncomePaymentCreateView.as_view(),
    #                 name="income_payment_create",
    #             ),
    #             path(
    #                 "update/<int:pk>/",
    #                 views.IncomePaymentUpdateView.as_view(),
    #                 name="income_payment_update",
    #             ),
    #         ]
    #     )
    # )
]

# for app in ["budget", "hiring", "invoice"]:
#     urlpatterns.append(
#         path(
#             f"{app}/",
#             include(
#                 [
#                     path("list/", views.ReceiptListView.as_view(), name=f"{app}_list"),
#                     path(
#                         "create/",
#                         views.ReceiptCreateView.as_view(),
#                         name=f"{app}_create",
#                     ),
#                     path(
#                         "update/<int:pk>/",
#                         views.ReceiptUpdateView.as_view(),
#                         name=f"{app}_update",
#                     ),
#                     path(
#                         "delete/<int:pk>/",
#                         views.ReceiptDeleteView.as_view(),
#                         name=f"{app}_delete",
#                     ),
#                     path(
#                         "location/<int:pk>/",
#                         get_location,
#                         name=f"{app}_location",
#                     ),
#                 ]
#             ),
#         ),
#     )

from django.urls import include, path

from configuration import views

urlpatterns = [
    path(
        "operator/",
        include(
            [
                path("list/", views.operator_list_view, name="operator_list"),
                path("create/", views.operator_create_view, name="operator_create"),
                path(
                    "detail/<int:pk>/",
                    views.operator_detail_view,
                    name="operator_detail",
                ),
                path(
                    "is_active/<int:pk>/",
                    views.toggle_operator_is_active,
                    name="toggle_operator_is_active",
                ),
                path(
                    "password_change/<int:pk>/",
                    views.operator_password_change,
                    name="operator_password_change",
                ),
            ]
        ),
    ),
    path(
        "task/",
        include(
            [
                path("list/<str:date_str>/", views.task_list_view, name="task_list"),
                path("list/", views.task_list_view, name="task_list"),
                path("create/<int:pk>/", views.task_create_view, name="task_create"),
                path("create/", views.task_create_view, name="task_create"),
                path("update/<int:pk>/", views.task_update_view, name="task_update"),
                path("delete/<int:pk>/", views.task_delete_view, name="task_delete"),
                path("detail/<int:pk>/", views.task_detail_view, name="task_detail"),
            ]
        ),
    ),
    path(
        "paymentmethod/",
        include(
            [
                path(
                    "list/", views.payment_method_list_view, name="paymentmethod_list"
                ),
                path(
                    "create/",
                    views.payment_method_create_view,
                    name="paymentmethod_create",
                ),
                path(
                    "detail/<int:pk>/",
                    views.payment_method_detail_view,
                    name="paymentmethod_detail",
                ),
                path(
                    "is_active/<int:pk>/",
                    views.toggle_payment_method_is_active,
                    name="toggle_paymentmethod_is_active",
                ),
            ]
        ),
    ),
]

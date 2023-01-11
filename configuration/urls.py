from django.urls import include, path

from configuration import views

urlpatterns = [
    path(
        "operator/",
        include(
            [
                path("index/", views.operator_index_view, name="operator_index"),
                path("list/", views.operator_list_view, name="operator_list"),
                path("create/", views.operator_create_view, name="operator_create"),
                path(
                    "detail/<int:pk>/",
                    views.operator_detail_view,
                    name="operator_detail",
                ),
                path(
                    "is_active/<int:pk>/",
                    views.operator_is_active,
                    name="operator_is_active",
                ),
            ]
        ),
    ),
    path(
        "task/",
        include(
            [
                path("index/", views.task_index_view, name="task_index"),
                path("list/<int:pk>", views.task_list_view, name="task_list"),
                path("list/", views.task_list_view, name="task_list"),
                path("create/<int:pk>/", views.task_create_view, name="task_create"),
                path("create/", views.task_create_view, name="task_create"),
                path("update/<int:pk>/", views.task_update_view, name="task_update"),
                path("delete/<int:pk>/", views.task_delete_view, name="task_delete"),
                path(
                    "inline_create/",
                    views.task_inline_create_view,
                    name="task_inline_create",
                ),
                path(
                    "inline_update/<int:pk>/",
                    views.task_inline_update_view,
                    name="task_inline_update",
                ),
                # path("task_actions/", views.task_actions, name="task_actions"),
                # path("is_done/<int:pk>/", views.toggle_is_done, name="toggle_is_done"),
            ]
        ),
    ),
    path(
        "payment_method/",
        include(
            [
                path(
                    "index/",
                    views.payment_method_index_view,
                    name="payment_method_index",
                ),
                path(
                    "list/", views.payment_method_list_view, name="payment_method_list"
                ),
                path(
                    "create/",
                    views.payment_method_create_view,
                    name="payment_method_create",
                ),
                # path("update/<int:pk>/", views.payment_method_update_view, name="payment_method_update"),
                # path("is_active/<int:pk>/", views.payment_method_is_active, name="payment_method_is_active"),
            ]
        ),
    ),
]

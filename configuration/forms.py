from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

from configuration.models import PaymentMethod, Task


def add_html_class_to_label(original_function):
    def class_to_label_tag(self, *args, **kwargs):
        required_field = format_html("""<span class="required-field"> *</span>""")
        label_suffix = required_field if self.field.required else ""
        return original_function(
            self, attrs={"class": "text-muted m-2"}, label_suffix=label_suffix
        )

    return class_to_label_tag


forms.BoundField.label_tag = add_html_class_to_label(forms.BoundField.label_tag)


class OperatorCreateForm(UserCreationForm):
    """
    Form for creating a new 'operario' instance, related to :model:`auth.User`
    """

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("task_start_date")
        end_date = cleaned_data.get("task_end_date")
        try:
            if start_date < timezone.now().date():
                self.add_error(
                    "task_start_date",
                    ValidationError(
                        "La fecha de inicio no puede ser anterior al día de hoy."
                    ),
                )
        except TypeError:
            self.add_error(
                "task_start_date", ValidationError("Ingrese una fecha válida.")
            )
        try:
            if end_date < start_date:
                self.add_error(
                    "task_end_date",
                    ValidationError(
                        "La fecha de finalización no puede ser anterior a la de inicio."
                    ),
                )
        except TypeError:
            self.add_error(
                "task_start_date", ValidationError("Ingrese una fecha válida.")
            )
        return cleaned_data


class PaymentMethodCreateForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = "__all__"

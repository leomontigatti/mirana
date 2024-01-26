from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from configuration.models import PaymentMethod, Task
from income.models import Hiring


class OperatorCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True


class OperatorChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = "__all__"


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"
        widgets = {
            "start_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "class": "form-control rounded-end",
                    "type": "date",
                },
            ),
        }

    def clean(self) -> None:
        super().clean()
        # Check the task "Recordatorio de cobranza" doesn't exists for this hiring
        description = self.cleaned_data.get("description", "").lower()
        hiring = self.cleaned_data.get("hiring", None)
        if hiring and description == "Recordatorio de cobranza":
            raise ValidationError(
                {
                    "description": ValidationError(
                        'La descripción no puede ser igual a "Recordatorio de cobranza"'
                    ),
                }
            )


class PaymentMethodCreateForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


TASK_ACTIONS = {
    "completed": {
        "description": "Marcar como completa",
    },
    "income_payment": {
        "description": "Cobrar y generar recibo",
    },
    "on_way_placing_bathroom": {
        "description": "Baño: Informar en camino a colocar",
        "message": "El operario está en camino a colocar el/los baños.",
    },
    "on_way_cleaning_bathroom": {
        "description": "Baño: Informar en camino a limpiar",
        "message": "El operario está en camino a limpiar el/los baños.",
    },
    "on_way_removing_bathroom": {
        "description": "Baño: Informar en camino a retirar",
        "message": "El operario está en camino a retirar el/los baños.",
    },
    "bathroom_placed": {
        "description": "Baño: Informar colocación",
        "message": "El/los baños ya están colocados.",
    },
    "bathroom_cleaned": {
        "description": "Baño: Informar limpieza",
        "message": "El/los baños ya están limpios.",
    },
    "bathroom_not_cleaned": {
        "description": "Baño: Informar la NO limpieza",
        "message": "El/los baños no pudieron limpiarse. Por favor comunicate con nosotros.",
    },
    "bathroom_removed": {
        "description": "Baño: Informar retiro",
        "message": "El/los baños ya fueron retirados.",
    },
    "on_way_placing_workshop": {
        "description": "Obrador: Informar en camino a colocar",
        "message": "El operario está en camino a colocar el/los obradores.",
    },
    "on_way_removing_workshop": {
        "description": "Obrador: en camino a retirar",
        "message": "El operario está en camino a retirar el/los obradores.",
    },
    "workshop_placed": {
        "description": "Obrador: colocación",
        "message": "El/los obradores ya están colocados.",
    },
    "workshop_removed": {
        "description": "Obrador: retiro",
        "message": "El/los obradores ya fueron retirados.",
    },
}


def get_actions_choices(task):
    task_actions = []
    if not task.hiring and not task.is_done:
        for key, value in TASK_ACTIONS.items():
            if "message" not in value:
                task_actions.append((key, value.get("description")))
    elif task.is_done:
        for key, value in TASK_ACTIONS.items():
            if key == "income_payment":
                task_actions.append((key, value.get("description")))
    else:
        for key, value in TASK_ACTIONS.items():
            task_actions.append((key, value.get("description")))

    return task_actions


class TaskActionsForm(forms.Form):
    def __init__(self, *args, task, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["action"].choices = get_actions_choices(task)

    action = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
        label="Acciones",
    )

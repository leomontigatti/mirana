from django import forms
from django.core.exceptions import ValidationError

from accounting.models import Asiento, Cuenta, Entry, TaxType


def add_class_to_label(original_function):
    def class_to_label_tag(self, *args, **kwargs):
        required_field = {"class": "fw-bold"}
        attrs = required_field if self.field.required else {}
        return original_function(self, attrs=attrs, label_suffix="")

    return class_to_label_tag


forms.BoundField.label_tag = add_class_to_label(forms.BoundField.label_tag)


class CuentaCreateForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ["name", "subrubro"]

    def clean(self):
        super().clean()

        # Upper case a cuenta's name to check uniqueness.
        name = self.cleaned_data.get("name", "").upper()
        subrubro = self.cleaned_data.get("subrubro", "")
        if Cuenta.objects.filter(name=name, subrubro=subrubro).exists():
            raise ValidationError(
                {
                    "name": ValidationError(
                        "Ya existe una cuenta con el nombre ingresado en el subrubro seleccionado."
                    ),
                    "subrubro": ValidationError(
                        "Ya existe una cuenta con el nombre ingresado en el subrubro seleccionado."
                    ),
                }
            )


class TaxTypeCreateForm(forms.ModelForm):
    class Meta:
        model = TaxType
        fields = "__all__"

    def clean(self):
        super().clean()

        # Upper case a tax's name to check uniqueness.
        name = self.cleaned_data.get("name", "").upper()
        percentage = self.cleaned_data.get("percentage", "")
        if TaxType.objects.filter(name=name, percentage=percentage).exists():
            raise ValidationError(
                {
                    "name": ValidationError(
                        "Ya existe un impuesto con el nombre y el porcentaje ingresados."
                    ),
                    "percentage": ValidationError(
                        "Ya existe un impuesto con el nombre y el porcentaje ingresados."
                    ),
                }
            )


class EntryCreateForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = "__all__"
        widgets = {
            "cuenta": forms.Select(attrs={"class": "form-select"}),
            "debe": forms.NumberInput(attrs={"class": "form-control text-center"}),
            "haber": forms.NumberInput(attrs={"class": "form-control text-center"}),
        }


class BaseEntryFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        # Check the debe and haber total sum is equal.
        debe = 0
        haber = 0
        for form in self.forms:
            debe += form.cleaned_data.get("debe", 0)
            haber += form.cleaned_data.get("haber", 0)
        if not debe == haber:
            raise ValidationError(
                "La suma total de las columnas de debe y haber debe ser igual."
            )


EntryFormset = forms.inlineformset_factory(
    Asiento,
    Entry,
    form=EntryCreateForm,
    formset=BaseEntryFormSet,
    extra=0,
    can_delete=False,
    min_num=2,
    validate_min=True,
)

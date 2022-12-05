from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.html import format_html


def add_class_to_label(original_function):
    def class_to_label_tag(self, *args, **kwargs):
        required_field = format_html("""<span class="required-field"> *</span>""")
        label_suffix = required_field if self.field.required else ""
        return original_function(
            self, attrs={"class": "fw-bold m-2"}, label_suffix=label_suffix
        )

    return class_to_label_tag


forms.BoundField.label_tag = add_class_to_label(forms.BoundField.label_tag)


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nombre de usuario"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Contraseña"}
        )
    )

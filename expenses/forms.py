from django import forms
from django.core.exceptions import ValidationError

from configuration.models import PaymentMethod
from expenses.models import Expense, ExpensesInvoice, ExpensesPayment, Supplier, Tax
from income.forms import TaxesBaseFormSet


class SupplierCreateForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

    def clean(self) -> None:
        super().clean()
        identification_type = self.cleaned_data.get("identification_type", None)
        identification_number = self.cleaned_data.get("identification_number", None)

        # Check identification type and number are unique together.
        if Supplier.objects.filter(
            identification_number=identification_number,
            identification_type=identification_type,
        ).exists():
            raise ValidationError(
                {
                    "identification_type": ValidationError(
                        "Ya existe un proveedor con el tipo y número de identificación ingresados."
                    ),
                    "identification_number": ValidationError(
                        "Ya existe un proveedor con el tipo y número de identificación ingresados."
                    ),
                }
            )

        # Check identification type and number length.
        if identification_type == "CUIT" and len(identification_number) != 11:
            raise ValidationError(
                {
                    "identification_number": ValidationError(
                        "El número de CUIT debe contener 11 caracteres sin guiones."
                    ),
                }
            )
        elif identification_type == "DNI" and len(identification_number) != 8:
            raise ValidationError(
                {
                    "identification_number": ValidationError(
                        "El número de DNI debe contener 8 caracteres sin puntos."
                    ),
                }
            )


class ExpensesInvoiceCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields.get("issue_date").initial = None
        self.fields.get("due_date").initial = None

    class Meta:
        model = ExpensesInvoice
        fields = "__all__"
        widgets = {
            "issue_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "class": "form-control rounded-end",
                    "type": "date",
                },
            ),
            "due_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "class": "form-control rounded-end",
                    "type": "date",
                },
            ),
        }

    def clean(self) -> None:
        super().clean()

        # Check issue and due dates.
        issue_date = self.cleaned_data.get("issue_date", None)
        due_date = self.cleaned_data.get("due_date", None)
        if issue_date and due_date and (due_date < issue_date):
            raise ValidationError(
                {
                    "due_date": ValidationError(
                        "La fecha de vencimiento no puede ser anterior a la de emisión."
                    ),
                }
            )


class ExpensesPaymentCreateForm(forms.ModelForm):
    class Meta:
        model = ExpensesPayment
        fields = "__all__"
        widgets = {
            "issue_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "class": "form-control rounded-end",
                    "type": "date",
                },
            ),
        }

    def clean(self) -> None:
        super().clean()

        # Check supplier and invoice supplier match.
        invoice = self.cleaned_data.get("invoice", None)
        supplier = self.cleaned_data.get("supplier", None)
        if invoice and invoice.supplier != supplier:
            raise ValidationError(
                {
                    "supplier": ValidationError(
                        "El proveedor seleccionado debe ser el mismo al de la factura a imputar."
                    ),
                }
            )

        # Check a reference is given depending on the method.
        method = self.cleaned_data.get("method", None)
        reference = self.cleaned_data.get("reference", "")
        if method and method.cuenta.subrubro_id != 1 and not reference:
            raise ValidationError(
                {
                    "reference": ValidationError(
                        "Debe ingresarse una referencia para la forma de pago seleccionada."
                    ),
                }
            )


class ExpenseCreateForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = "__all__"
        widgets = {
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                },
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                    "onchange": "setExpenseSubtotal()",
                },
            ),
            "unitario": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                    "onchange": "setExpenseSubtotal()",
                },
            ),
            "expense_subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                    "readonly": "",
                },
            ),
        }


ExpensesFormset = forms.modelformset_factory(
    Expense, ExpenseCreateForm, extra=0, min_num=1
)


class TaxCreateForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = "__all__"
        widgets = {
            "tax_type": forms.Select(
                attrs={
                    "class": "form-select rounded-start",
                    "onchange": "setTaxSubtotal()",
                },
            ),
            "tax_subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control text-center rounded-end",
                    "readonly": "",
                },
            ),
        }


TaxesFormset = forms.modelformset_factory(Tax, TaxCreateForm, formset=TaxesBaseFormSet)

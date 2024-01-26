from django import forms
from django.core.exceptions import ValidationError

from income.models import (
    Budget,
    Customer,
    Hiring,
    IncomePayment,
    SalesInvoice,
    Service,
    Tax,
)


class CustomerCreateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

    def clean(self):
        super().clean()
        identification_type = self.cleaned_data.get("identification_type", "")
        identification_number = self.cleaned_data.get("identification_number", "")

        # Check identification type and number are unique together.
        if Customer.objects.filter(
            identification_number=identification_number,
            identification_type=identification_type,
        ).exists():
            raise ValidationError(
                {
                    "identification_type": ValidationError(
                        "Ya existe un cliente con el tipo y número de identificación ingresados."
                    ),
                    "identification_number": ValidationError(
                        "Ya existe un cliente con el tipo y número de identificación ingresados."
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


class BudgetCreateForm(forms.ModelForm):
    class Meta:
        model = Budget
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


class HiringCreateForm(forms.ModelForm):
    def __init__(self, *args, customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        if customer:
            self.fields["budget"].queryset = customer.budgets.filter(
                hiring__isnull=True
            )
        else:
            self.fields["budget"].queryset = Budget.objects.none()

    class Meta:
        model = Hiring
        fields = "__all__"
        widgets = {
            "start_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "class": "form-control rounded-end",
                    "type": "date",
                },
            ),
            "end_date": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "class": "form-control rounded-end",
                    "type": "date",
                },
            ),
        }

    def clean(self):
        super().clean()

        # Check issue and due dates.
        start_date = self.cleaned_data.get("start_date", None)
        end_date = self.cleaned_data.get("end_date", None)
        if start_date and end_date and (end_date < start_date):
            raise ValidationError(
                {
                    "end_date": ValidationError(
                        "La fecha de finalización no puede ser anterior a la de inicio."
                    ),
                }
            )


class SalesInvoiceCreateForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
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

    def clean(self):
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


class IncomePaymentCreateForm(forms.ModelForm):
    class Meta:
        model = IncomePayment
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

    def clean(self):
        super().clean()

        # Check customer and invoice customer match.
        invoice = self.cleaned_data.get("invoice", None)
        customer = self.cleaned_data.get("customer", None)
        if invoice and not invoice.customer == customer:
            raise ValidationError(
                {
                    "customer": ValidationError(
                        "El cliente seleccionado debe ser el mismo al de la factura a imputar."
                    ),
                }
            )

        # Check a reference is given depending on the method.
        method = self.cleaned_data.get("method", None)
        reference = self.cleaned_data.get("reference", "")
        if method.cuenta.subrubro_id != 1 and not reference:
            raise ValidationError(
                {
                    "reference": ValidationError(
                        "Debe ingresarse una referencia para la forma de pago seleccionada."
                    ),
                }
            )


class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"
        widgets = {
            "service_type": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                    "onchange": "setServiceSubtotal()",
                },
            ),
            "unitario": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                    "onchange": "setServiceSubtotal()",
                },
            ),
            "service_subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control text-center",
                    "readonly": "",
                },
            ),
        }

    def clean(self):
        super().clean()

        # Check there are available bathrooms and/or workshops.
        service_type = self.cleaned_data.get("service_type", None)
        amount = self.cleaned_data.get("amount", 0)
        if service_type:
            if service_type.pk == 1 and amount > service_type.bathrooms.count():
                raise ValidationError(
                    "La cantidad de baños demandada no puede ser mayor a la disponible."
                )
            elif service_type.pk == 2 and amount > service_type.workshops.count():
                raise ValidationError(
                    "La cantidad de obradores demandada no puede ser mayor a la disponible."
                )


class ServicesBaseFormSet(forms.BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        # Check that there are not duplicated service types.
        service_types = []
        for form in self.forms:
            service_type = form.cleaned_data.get("service_type", None)
            if service_type in service_types:
                raise ValidationError(
                    "El comprobante no puede tener servicios iguales."
                )
            service_types.append(service_type)


ServicesFormSet = forms.modelformset_factory(
    Service, ServiceCreateForm, formset=ServicesBaseFormSet, extra=0, min_num=1
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


class TaxesBaseFormSet(forms.BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        # Check that there are not duplicated tax types.
        tax_types = []
        for form in self.forms:
            tax_type = form.cleaned_data.get("tax_type", None)
            if tax_type in tax_types:
                raise ValidationError(
                    "El comprobante no puede tener impuestos iguales."
                )
            tax_types.append(tax_type)


TaxesFormset = forms.modelformset_factory(Tax, TaxCreateForm, formset=TaxesBaseFormSet)

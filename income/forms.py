from django import forms

from income.models import Budget, Customer, Hiring, IncomePayment, Service, Tax


class CustomerCreateForm(forms.ModelForm):
    """
    Form for creating or updating a customer, related to :model:`income.Customer`.
    """

    class Meta:
        model = Customer
        fields = "__all__"


class BudgetCreateForm(forms.ModelForm):
    """
    Form for creating or updating a budget, related to :model:`income.Budget`.
    """

    class Meta:
        model = Budget
        fields = "__all__"


class HiringCreateForm(forms.ModelForm):
    """
    Form for creating or updating a hiring, related to :model:`income.Hiring`.
    """

    class Meta:
        model = Hiring
        fields = "__all__"


class IncomePaymentCreateForm(forms.ModelForm):
    """
    Form for creating an income payment, related to :model:`income.IncomePayment`.
    """

    class Meta:
        model = IncomePayment
        fields = "__all__"


class ServiceCreateForm(forms.ModelForm):
    """
    Form for creating a service, related to :model:`income.Service`.
    """

    class Meta:
        model = Service
        exclude = "__all__"


class TaxCreateForm(forms.ModelForm):
    """
    Form for creating a tax, related to :model:`income.Tax`.
    """

    class Meta:
        model = Tax
        exclude = "__all__"

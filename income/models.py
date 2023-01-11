from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from accounting.models import Asiento, CapituloChoices, Cuenta, TaxType
from inventory.models import ServiceType
from main.models import (
    BaseContact,
    BaseReceipt,
    PaymentOptionChoices,
    SaleTermTypeChoices,
)


class Customer(BaseContact):
    """
    Store a single 'Customer' instance, inherits from :model:`main.BaseContact`.
    Related to :model:`accounting.Cuenta`.
    """

    cuenta_activo = models.OneToOneField(
        Cuenta,
        verbose_name="Cuenta activo",
        on_delete=models.PROTECT,
        blank=True,
        related_name="customer_activo",
        limit_choices_to={"subrubro__rubro__capitulo": CapituloChoices.ACTIVO},
    )
    cuenta_pasivo = models.OneToOneField(
        Cuenta,
        verbose_name="Cuenta pasivo",
        on_delete=models.PROTECT,
        blank=True,
        related_name="customer_pasivo",
        limit_choices_to={"subrubro__rubro__capitulo": CapituloChoices.PASIVO},
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        constraints = [
            models.UniqueConstraint(
                fields=["identification_type", "identification_number"],
                name="customer_uniqueness",
            )
        ]

    def __str__(self) -> str:
        return self.name


class Budget(BaseReceipt):
    """
    Store a single 'budget' instance, inherits from :model:`main.BaseReceipt`.
    Related to :model:`income.Customer`.
    """

    customer = models.ForeignKey(
        Customer,
        verbose_name="Cliente",
        related_name="budgets",
        on_delete=models.PROTECT,
    )
    issue_date = models.DateField(
        verbose_name="Fecha de emisión",
        default=date.today,
    )
    due_date = models.DateField(
        verbose_name="Fecha de vencimiento",
        default=date.today() + timedelta(days=15),
    )
    sale_term = models.CharField(
        verbose_name="Plazo de venta",
        max_length=50,
        choices=SaleTermTypeChoices.choices,
        default=SaleTermTypeChoices.CASH,
    )
    subtotal = models.FloatField(
        verbose_name="Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    total = models.FloatField(
        verbose_name="Total",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"

    def __str__(self):
        return f"{self.customer} - {self.address}"

    def clean(self):
        if self.due_date < self.issue_date:
            raise ValidationError(
                "La fecha de vencimiento no puede ser anterior a la fecha de emisión."
            )


class Hiring(BaseReceipt):
    """
    Store a single 'hiring' instance, inherits from :model:`main.BaseReceipt`.
    Related to :model:`income.Customer`.
    """

    customer = models.ForeignKey(
        Customer,
        verbose_name="Cliente",
        related_name="hiring",
        on_delete=models.PROTECT,
    )
    budget = models.OneToOneField(
        Budget,
        verbose_name="Presupuesto",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        limit_choices_to={
            "hiring__isnull": True,
        },
    )
    is_placed = models.BooleanField(
        verbose_name="Colocado",
        default=False,
    )
    is_clean = models.BooleanField(
        verbose_name="Limpio",
        default=True,
    )
    start_date = models.DateField(
        verbose_name="Fecha de inicio",
        default=date.today,
    )
    end_date = models.DateField(
        verbose_name="Fecha de finalización",
        default=date.today() + timedelta(days=15),
    )

    class Meta:
        verbose_name = "Contratación"
        verbose_name_plural = "Contrataciones"

    def __str__(self) -> str:
        return f"{self.customer} - {self.address}"

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                "La fecha de vencimiento no puede ser anterior a la fecha de emisión."
            )


class Invoice(BaseReceipt):
    """
    Store a single 'invoice' instance, inherits from :model:`main.BaseReceipt`.
    Related to :model:`income.Customer` and :model:`accounting.Asiento`.
    """

    asiento = models.OneToOneField(
        Asiento, verbose_name="Asiento", on_delete=models.PROTECT, blank=True, null=True
    )
    cai = models.CharField(
        verbose_name="Número de CAI",
        max_length=100,
        blank=True,
        null=True,
    )
    is_paid = models.BooleanField(
        verbose_name="Pagada",
        default=False,
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name="Cliente",
        related_name="invoices",
        on_delete=models.PROTECT,
    )
    budget = models.OneToOneField(
        Budget,
        verbose_name="Presupuesto",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        limit_choices_to={
            "invoice__isnull": True,
        },
    )
    has_electronic_invoice = models.BooleanField(
        verbose_name="Tiene factura electrónica",
        default=False,
    )
    issue_date = models.DateField(
        verbose_name="Fecha de emisión",
        default=date.today,
    )
    due_date = models.DateField(
        verbose_name="Fecha de vencimiento",
        default=date.today() + timedelta(days=15),
    )
    sale_term = models.CharField(
        verbose_name="Plazo de venta",
        max_length=50,
        choices=SaleTermTypeChoices.choices,
        default=SaleTermTypeChoices.CASH,
    )
    subtotal = models.FloatField(
        verbose_name="Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    total = models.FloatField(
        verbose_name="Total",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"{self.customer} - {self.address}"

    def clean(self):
        if self.due_date < self.issue_date:
            raise ValidationError(
                "La fecha de vencimiento no puede ser anterior a la fecha de emisión."
            )

    # def set_is_paid(self):
    #     total = 0
    #     for payment in self.income_payments.all():
    #         total += payment.amount
    #     if total == self.total:
    #         self.is_paid = True
    #         self.save()


class Service(models.Model):
    """
    Store a single 'service' instance, related to :model:`inventory.ServiceType`,
    :model:`income.Budget`, :model:`income.Hiring` and :model:`income.Invoice`.
    """

    service_type = models.ForeignKey(
        ServiceType,
        verbose_name="Tipo de servicio",
        related_name="services",
        on_delete=models.PROTECT,
        limit_choices_to={"is_active": True},
        blank=True,
    )
    amount = models.PositiveIntegerField(
        verbose_name="Cantidad",
        default=0,
    )
    unitario = models.FloatField(
        verbose_name="Unitario",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    service_subtotal = models.FloatField(
        verbose_name="Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    budget = models.ForeignKey(
        Budget,
        verbose_name="Presupuesto",
        related_name="services",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    hiring = models.ForeignKey(
        Hiring,
        verbose_name="Contratación",
        related_name="services",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    invoice = models.ForeignKey(
        Invoice,
        verbose_name="Facturas",
        related_name="services",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.service_type


class Tax(models.Model):
    """
    Store a single 'tax' instance, related to :model:`accounting.TaxType`,
    :model:`income.Budget`, :model:`income.Hiring` and :model:`income.Invoice`.
    """

    tax_type = models.ForeignKey(
        TaxType,
        verbose_name="Tipo de impuesto",
        related_name="taxes",
        on_delete=models.PROTECT,
        blank=True,
    )
    tax_subtotal = models.FloatField(
        verbose_name="Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    budget = models.ForeignKey(
        Budget,
        verbose_name="Presupuesto",
        related_name="taxes",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    hiring = models.ForeignKey(
        Hiring,
        verbose_name="Contratación",
        related_name="taxes",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    invoice = models.ForeignKey(
        Invoice,
        verbose_name="Facturas",
        related_name="taxes",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"

    def __str__(self):
        return self.tax_type


class IncomePayment(models.Model):
    """
    Store a single 'income payment' instance, related to :model:`income.Invoice` and
    :model:`income.Customer`.
    """

    invoice = models.ForeignKey(
        Invoice,
        verbose_name="Factura",
        on_delete=models.PROTECT,
        related_name="income_payments",
        blank=True,
        null=True,
        limit_choices_to={"is_paid": False},
    )
    customer = models.ForeignKey(
        Customer,
        verbose_name="Cliente",
        related_name="income_payments",
        on_delete=models.PROTECT,
    )
    option = models.CharField(
        verbose_name="Cobrador",
        max_length=50,
        choices=PaymentOptionChoices.choices,
    )
    method = models.ForeignKey(
        "configuration.PaymentMethod",
        verbose_name="Forma de pago",
        on_delete=models.PROTECT,
        limit_choices_to={"is_active": True},
    )
    amount = models.FloatField(verbose_name="Monto")
    issue_date = models.DateField(
        verbose_name="Fecha de emisión",
        default=date.today,
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación", auto_now=True
    )

    class Meta:
        verbose_name = "Cobro"
        verbose_name_plural = "Cobros"
        ordering = ("issue_date",)

    def __str__(self) -> str:
        return f"{self.customer} - {self.amount}"

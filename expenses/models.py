from datetime import date

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounting.models import Asiento, Cuenta, Entry, TaxType
from main.models import (
    BaseContact,
    BaseInvoice,
    ReceiptLetterChoices,
    validate_is_numeric,
)


class Supplier(BaseContact):
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["identification_type", "identification_number"],
                name="supplier_uniqueness",
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("supplier_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("supplier_update", kwargs={"pk": self.pk})

    def get_balance(self):
        balance = 0
        for movement in self.supplier_movements.all():
            balance += movement.amount
        return balance


class ExpensesInvoice(BaseInvoice):
    letter = models.CharField(
        "Letra",
        max_length=1,
        choices=ReceiptLetterChoices.choices,
        default=ReceiptLetterChoices.A,
    )
    sales_point = models.CharField(
        "Punto de venta",
        max_length=3,
        validators=[validate_is_numeric],
    )
    number = models.CharField(
        "Número",
        max_length=9,
        validators=[validate_is_numeric],
    )
    supplier = models.ForeignKey(
        Supplier,
        models.PROTECT,
        related_name="invoices",
        verbose_name="Proveedor",
    )
    cuenta_egreso = models.ForeignKey(
        Cuenta,
        models.PROTECT,
        related_name="expenses_invoices",
        verbose_name="Cuenta de egreso",
        limit_choices_to={"subrubro": 36},
    )

    class Meta:
        verbose_name = "Factura de gastos"
        verbose_name_plural = "Facturas de gastos"
        ordering = ["-issue_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["letter", "sales_point", "number", "supplier"],
                name="expensesinvoice_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.supplier} -> Factura N° {self.letter}-{self.sales_point}-{self.number}"

    def get_absolute_url(self):
        return reverse("expensesinvoice_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("expensesinvoice_update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Complete sales point and number with zeros.
        # self.sales_point = self.sales_point.zfill(3)
        # self.number = self.number.zfill(9)

        # Get or create an asiento instance.
        try:
            asiento = self.asiento
        except Asiento.DoesNotExist:
            asiento = Asiento.objects.create(create_date=timezone.now().date)
            self.asiento = asiento

        # Update or create 'proveedores' entry instance.
        cuenta_proveedores = Cuenta.objects.get(pk=12)
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=cuenta_proveedores,
            defaults={"haber": -self.total},
        )

        # Update or create invoice's cuenta egreso entry instance.
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=self.cuenta_egreso,
            defaults={"debe": self.subtotal},
        )

        return super().save(*args, **kwargs)

    def update_or_create_taxes_entry(self):
        # Create an entry instance for every tax.
        for tax in self.income_taxes.all():
            Entry.objects.update_or_create(
                asiento=self.asiento,
                cuenta=tax.tax_type.cuenta_activo,
                defaults={"debe": tax.tax_subtotal},
            )

    def update_or_create_supplier_movement(self):
        SupplierMovement.objects.update_or_create(
            supplier=self.supplier,
            invoice=self,
            defaults={
                "amount": self.total,
            },
        )


class Expense(models.Model):
    description = models.CharField(
        "Descripción",
        max_length=100,
    )
    amount = models.PositiveIntegerField(
        "Cantidad",
        default=0,
    )
    unitario = models.FloatField(
        "Unitario",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    expense_subtotal = models.FloatField(
        "Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    invoice = models.ForeignKey(
        ExpensesInvoice,
        models.CASCADE,
        related_name="expenses",
        verbose_name="Factura de gastos",
        blank=True,
    )

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Tax(models.Model):
    tax_type = models.ForeignKey(
        TaxType,
        models.CASCADE,
        related_name="expenses_taxes",
        verbose_name="Tipo de impuesto",
    )
    tax_subtotal = models.FloatField(
        "Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    invoice = models.ForeignKey(
        ExpensesInvoice,
        models.CASCADE,
        related_name="expenses_taxes",
        verbose_name="Factura de gastos",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"
        constraints = [
            models.UniqueConstraint(
                fields=["tax_type", "invoice"],
                name="expensesinvoice_tax_uniqueness",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tax_type} - $ {self.tax_subtotal}"


class ExpensesPayment(models.Model):
    invoice = models.ForeignKey(
        ExpensesInvoice,
        models.SET_NULL,
        related_name="expenses_payments",
        limit_choices_to={"is_paid": False},
        verbose_name="A imputar en",
        blank=True,
        null=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        models.PROTECT,
        related_name="expenses_payments",
        verbose_name="Proveedor",
    )
    method = models.ForeignKey(
        "configuration.PaymentMethod",
        models.PROTECT,
        related_name="expenses_payments",
        limit_choices_to={"is_active": True},
        verbose_name="Forma de pago",
    )
    reference = models.CharField(
        "Referencia",
        max_length=50,
        blank=True,
        null=True,
        help_text="Número de cheque, transferencia o depósito.",
    )
    amount = models.FloatField(
        "Monto",
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    issue_date = models.DateField(
        "Fecha de emisión",
        default=date.today,
    )
    change_date = models.DateTimeField("Fecha de modificación", auto_now=True)
    asiento = models.OneToOneField(
        Asiento,
        models.PROTECT,
        related_name="expenses_payment",
        verbose_name="Asiento",
        blank=True,
    )

    class Meta:
        verbose_name = "Recibo de pago"
        verbose_name_plural = "Recibos de pago"
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.supplier} - $ {self.amount}"

    def get_absolute_url(self):
        return reverse("expensespayment_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("expensespayment_update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        try:
            asiento = self.asiento
        except Asiento.DoesNotExist:
            asiento = Asiento.objects.create(create_date=timezone.now().date)
            self.asiento = asiento

        # Update or create 'proveedores' entry instance.
        cuenta_proveedores = Cuenta.objects.get(pk=12)
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=cuenta_proveedores,
            defaults={"debe": self.amount},
        )

        # Update or create payment method's cuenta entry instance.
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=self.method.cuenta,
            defaults={"haber": -self.amount},
        )

        return super().save(*args, **kwargs)

    def update_or_create_supplier_movement(self):
        SupplierMovement.objects.update_or_create(
            supplier=self.supplier,
            payment=self,
            defaults={
                "amount": -self.amount,
            },
        )

    def check_invoice_is_paid(self):
        invoice = self.invoice
        if invoice:
            total = 0.0
            for payment in invoice.expenses_payments.all():
                total += payment.amount
                if total >= invoice.total:
                    invoice.is_paid = True
                else:
                    invoice.is_paid = False
                invoice.save()


class SupplierMovement(models.Model):
    create_date = models.DateField(
        "Fecha de creación",
        auto_now=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        models.CASCADE,
        related_name="supplier_movements",
        verbose_name="Proveedor",
    )
    invoice = models.OneToOneField(
        ExpensesInvoice,
        models.CASCADE,
        related_name="supplier_movement",
        verbose_name="Factura de gastos",
        null=True,
    )
    payment = models.OneToOneField(
        ExpensesPayment,
        models.CASCADE,
        related_name="supplier_movement",
        verbose_name="Recibo de pago",
        null=True,
    )
    amount = models.FloatField("Monto")

    class Meta:
        verbose_name = "Movimiento de proveedor"
        verbose_name_plural = "Movimientos de proveedor"
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.supplier} - $ {self.amount}"

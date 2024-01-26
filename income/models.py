from datetime import date, timedelta

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounting.models import Asiento, Cuenta, Entry, TaxType
from configuration.models import Task
from inventory.models import ServiceType, StockMovement, StockStatusChoices
from main.models import (
    BaseContact,
    BaseInvoice,
    ReceiptLetterChoices,
    SaleConditionChoices,
    validate_is_numeric,
)


class HiringStatusChoices(models.TextChoices):
    PLACING_PENDING = "PLACING_PENDING", "Colocación pendiente"
    PENDING_BATHROOM = "PENDING_BATHROOM", "Colocación de baño pendiente"
    PENDING_WORKSHOP = "PENDING_WORKSHOP", "Colocación de obrador pendiente"
    ONGOING = "ONGOING", "En curso"
    CLEANING_PENDING = "CLEANING_PENDING", "Limpieza pendiente"
    COLLECTION_PENDING = "COLLECTION_PENDING", "Cobro pendiente"
    CHARGED = "CHARGED", "Cobrada"


def create_task(service, date, description):
    return Task(
        service=service,
        description=description,
        hiring=service.hiring if hasattr(service, "hiring") else None,
        start_date=date,
    )


class Customer(BaseContact):
    has_whatsapp_acceptance = models.BooleanField(
        "Acepta mensajes de WhatsApp", default=False
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["identification_type", "identification_number"],
                name="customer_uniqueness",
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("customer_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("customer_update", kwargs={"pk": self.pk})

    def get_balance(self):
        balance = 0
        for movement in self.customer_movements.all():
            balance += movement.amount
        return balance


class Budget(models.Model):
    customer = models.ForeignKey(
        Customer,
        models.PROTECT,
        related_name="budgets",
        verbose_name="Cliente",
    )
    address = models.CharField("Domicilio", max_length=200)
    lat = models.CharField(
        "Latitud",
        max_length=20,
    )
    lng = models.CharField(
        "Longitud",
        max_length=20,
    )
    issue_date = models.DateField(
        "Fecha de emisión",
        default=date.today,
    )
    sale_condition = models.CharField(
        "Condición de venta",
        max_length=50,
        default=SaleConditionChoices.CASH,
        choices=SaleConditionChoices.choices,
    )
    notes = models.TextField(
        "Notas",
        max_length=300,
        blank=True,
        null=True,
        default="Este presupuesto tiene validez por 15 días desde su fecha de emisión.",
    )
    subtotal = models.FloatField(
        "Subtotal",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    total = models.FloatField(
        "Total",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        ordering = ["issue_date"]

    def __str__(self):
        return f"Nº {self.pk} -> {self.address}"

    def get_absolute_url(self):
        return reverse("budget_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("budget_update", kwargs={"pk": self.pk})


class Hiring(models.Model):
    customer = models.ForeignKey(
        Customer,
        models.PROTECT,
        related_name="hiring",
        verbose_name="Cliente",
    )
    budget = models.OneToOneField(
        Budget,
        models.PROTECT,
        related_name="hiring",
        limit_choices_to={
            "hiring__isnull": True,
        },
        verbose_name="Presupuesto",
        blank=True,
        null=True,
    )
    address = models.CharField("Domicilio", max_length=200)
    lat = models.CharField(
        "Latitud",
        max_length=20,
    )
    lng = models.CharField(
        "Longitud",
        max_length=20,
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        default=HiringStatusChoices.PLACING_PENDING,
        choices=HiringStatusChoices.choices,
    )
    start_date = models.DateField("Fecha de inicio")
    end_date = models.DateField("Fecha de finalización")
    notes = models.TextField(
        "Notas",
        max_length=300,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Contratación"
        verbose_name_plural = "Contrataciones"
        ordering = ["-pk"]

    def __str__(self):
        return f"Nº {self.pk} -> {self.customer}"

    def get_absolute_url(self):
        return reverse("hiring_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("hiring_update", kwargs={"pk": self.pk})

    def update_or_create_stock_movement(self):
        for service in self.services.all():
            service_type = service.service_type

            if service_type.pk in [1, 2]:
                if service_type.bathrooms.exists():
                    stock = "BATHROOM"
                    object_list = service_type.bathrooms.filter(
                        status=StockStatusChoices.AVAILABLE
                    )
                elif service_type.workshops.exists():
                    stock = "WORKSHOP"
                    object_list = service_type.workshops.filter(
                        status=StockStatusChoices.AVAILABLE
                    )

                ids_qs = object_list.values("pk")[: service.amount]
                updated = object_list.filter(pk__in=ids_qs).update(
                    status=StockStatusChoices.PROMISED
                )

                StockMovement.objects.update_or_create(
                    service=service,
                    stock=stock,
                    status=StockStatusChoices.AVAILABLE,
                    defaults={
                        "amount": -updated,
                    },
                )
                StockMovement.objects.update_or_create(
                    service=service,
                    stock=stock,
                    status=StockStatusChoices.PROMISED,
                    defaults={
                        "amount": updated,
                    },
                )

    def update_or_create_reminder_task(self):
        Task.objects.update_or_create(
            hiring=self,
            description="Recordatorio de cobranza",
            defaults={
                "start_date": self.end_date - timedelta(days=3),
            },
        )


class SalesInvoice(BaseInvoice):
    letter = models.CharField(
        "Letra",
        max_length=1,
        blank=True,
        null=True,
        choices=ReceiptLetterChoices.choices,
    )
    sales_point = models.CharField(
        "Punto de venta",
        max_length=3,
        blank=True,
        null=True,
        validators=[validate_is_numeric],
    )
    number = models.CharField(
        "Número",
        max_length=9,
        blank=True,
        null=True,
        validators=[validate_is_numeric],
    )
    customer = models.ForeignKey(
        Customer,
        models.PROTECT,
        related_name="invoices",
        verbose_name="Cliente",
    )
    hiring = models.OneToOneField(
        Hiring,
        models.PROTECT,
        related_name="sales_invoice",
        limit_choices_to={
            "sales_invoice__isnull": True,
        },
        verbose_name="Contratación",
        blank=True,
        null=True,
    )
    has_electronic_invoice = models.BooleanField(
        "Tiene factura electrónica",
        default=False,
    )

    class Meta:
        verbose_name = "Factura de venta"
        verbose_name_plural = "Facturas de venta"
        ordering = ["-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["letter", "sales_point", "number", "customer"],
                name="salesinvoice_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.customer} -> Factura N° {self.pk}"

    def get_absolute_url(self):
        return reverse("salesinvoice_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("salesinvoice_update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Get or create an asiento instance.
        try:
            asiento = self.asiento
        except Asiento.DoesNotExist:
            asiento = Asiento.objects.create(create_date=timezone.now().date)
            self.asiento = asiento

        # Update or create 'créditos por ventas' entry instance.
        cuenta_debe = Cuenta.objects.get(pk=10)
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=cuenta_debe,
            defaults={"debe": self.total},
        )

        # Update or create 'ventas' entry instance.
        cuenta_ventas = Cuenta.objects.get(pk=22)
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=cuenta_ventas,
            defaults={"haber": -self.subtotal},
        )

        return super().save(*args, **kwargs)

    def update_or_create_taxes_entry(self):
        # Create an entry instance for every tax.
        for tax in self.income_taxes.all():
            Entry.objects.update_or_create(
                asiento=self.asiento,
                cuenta=tax.tax_type.cuenta_pasivo,
                defaults={"haber": -tax.tax_subtotal},
            )

    def update_or_create_customer_movement(self):
        CustomerMovement.objects.update_or_create(
            customer=self.customer,
            invoice=self,
            defaults={
                "amount": -self.total,
            },
        )


class Service(models.Model):
    service_type = models.ForeignKey(
        ServiceType,
        models.CASCADE,
        related_name="services",
        limit_choices_to={"is_active": True},
        verbose_name="Tipo de servicio",
    )
    amount = models.PositiveSmallIntegerField(
        "Cantidad",
        default=0,
    )
    unitario = models.FloatField(
        "Unitario",
        blank=True,
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    service_subtotal = models.FloatField(
        "Subtotal",
        blank=True,
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    budget = models.ForeignKey(
        Budget,
        models.SET_NULL,
        related_name="services",
        verbose_name="Presupuesto",
        blank=True,
        null=True,
    )
    hiring = models.ForeignKey(
        Hiring,
        models.SET_NULL,
        related_name="services",
        verbose_name="Contratación",
        blank=True,
        null=True,
    )
    invoice = models.ForeignKey(
        SalesInvoice,
        models.SET_NULL,
        related_name="services",
        verbose_name="Factura de venta",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return f"{self.service_type} - {self.amount}"

    def create_bathroom_workshop_task(self):
        description = "Colocar baño" if self.service_type.pk == 1 else "Colocar obrador"
        task = create_task(self, self.hiring.start_date, description)
        task.save()

    def update_bathroom_workshop_task(self):
        task = self.tasks.first()
        task.start_date = self.hiring.start_date
        task.save()

    def create_cleaning_tasks(self):
        today = self.hiring.start_date
        tasks = []

        while today < self.hiring.end_date:
            if self.service_type.pk == 3 and today.weekday() in [1, 3]:
                tasks.append(create_task(self, today, "Limpieza"))
            elif self.service_type.pk == 4 and today.weekday() in [0, 2, 4]:
                tasks.append(create_task(self, today, "Limpieza"))

            today += timedelta(days=1)
        Task.objects.bulk_create(tasks)

    def update_cleaning_tasks(self):
        today = self.hiring.start_date
        tasks = list(self.tasks.all())
        while today < self.hiring.end_date:
            if today == self.hiring.start_date:
                today += timedelta(days=1)
                continue
            elif self.service_type.pk == 3 and today.weekday() in [1, 3]:
                try:
                    tasks[0].start_date = today
                    tasks[0].save()
                    del tasks[0]
                except IndexError:
                    task = create_task(self, today, "Limpieza")
                    task.save()
            elif self.service_type.pk == 4 and today.weekday() in [0, 2, 4]:
                try:
                    tasks[0].start_date = today
                    tasks[0].save()
                    del tasks[0]
                except IndexError:
                    task = create_task(self, today, "Limpieza")
                    task.save()
            today += timedelta(days=1)

        if tasks:
            for task in tasks:
                task.delete()


class Tax(models.Model):
    tax_type = models.ForeignKey(
        TaxType,
        models.CASCADE,
        related_name="income_taxes",
        verbose_name="Tipo de impuesto",
        blank=True,
    )
    tax_subtotal = models.FloatField(
        "Subtotal",
        default=0,
        blank=True,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0."),
        ],
    )
    budget = models.ForeignKey(
        Budget,
        models.SET_NULL,
        related_name="income_taxes",
        verbose_name="Presupuesto",
        blank=True,
        null=True,
    )
    invoice = models.ForeignKey(
        SalesInvoice,
        models.SET_NULL,
        related_name="income_taxes",
        verbose_name="Factura de venta",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"
        constraints = [
            models.UniqueConstraint(
                fields=["tax_type", "invoice"],
                name="salesinvoice_tax_uniqueness",
            ),
        ]

    def __str__(self):
        return f"{self.tax_type} - $ {self.tax_subtotal}"


class IncomePayment(models.Model):
    invoice = models.ForeignKey(
        SalesInvoice,
        models.SET_NULL,
        related_name="income_payments",
        limit_choices_to={"is_paid": False},
        verbose_name="A imputar en",
        blank=True,
        null=True,
    )
    customer = models.ForeignKey(
        Customer,
        models.PROTECT,
        related_name="income_payments",
        verbose_name="Cliente",
        blank=True,
        null=True,
    )
    collector = models.ForeignKey(
        "configuration.Collector",
        models.PROTECT,
        related_name="income_payments",
        verbose_name="Cobrador",
    )
    method = models.ForeignKey(
        "configuration.PaymentMethod",
        models.PROTECT,
        related_name="income_payments",
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
        related_name="income_payment",
        verbose_name="Asiento",
        blank=True,
    )

    class Meta:
        verbose_name = "Recibo de cobro"
        verbose_name_plural = "Recibos de cobro"
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.customer} - $ {self.amount}"

    def get_absolute_url(self):
        return reverse("incomepayment_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("incomepayment_update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        try:
            asiento = self.asiento
        except Asiento.DoesNotExist:
            asiento = Asiento.objects.create(create_date=timezone.now().date)
            self.asiento = asiento

        if self.customer:
            cuenta_haber = Cuenta.objects.get(pk=10)
        else:
            cuenta_haber = Cuenta.objects.get(pk=13)

        # Update or create 'créditos por ventas' or 'anticipo de clientes' entry instance.
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=cuenta_haber,
            defaults={"haber": -self.amount},
        )

        # Update or create payment method cuenta's entry instance.
        Entry.objects.update_or_create(
            asiento=asiento,
            cuenta=self.method.cuenta,
            defaults={"debe": self.amount},
        )

        return super().save(*args, **kwargs)

    def update_or_create_customer_movement(self):
        CustomerMovement.objects.update_or_create(
            customer=self.customer,
            payment=self,
            defaults={
                "amount": self.amount,
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


class CustomerMovement(models.Model):
    create_date = models.DateTimeField(
        "Fecha de creación",
        auto_now=True,
    )
    customer = models.ForeignKey(
        Customer,
        models.CASCADE,
        related_name="customer_movements",
        verbose_name="Cliente",
    )
    invoice = models.OneToOneField(
        SalesInvoice,
        models.CASCADE,
        related_name="customer_movement",
        verbose_name="Factura de venta",
        null=True,
    )
    payment = models.OneToOneField(
        IncomePayment,
        models.CASCADE,
        related_name="customer_movement",
        verbose_name="Recibo de cobro",
        null=True,
    )
    amount = models.FloatField("Monto")

    class Meta:
        verbose_name = "Movimiento de cliente"
        verbose_name_plural = "Movimientos de clientes"
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.customer} - $ {self.amount}"

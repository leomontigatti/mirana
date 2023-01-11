from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def validate_tax_type_characters(value):
    """
    Check the name does not contain reserved characters.
    """
    reserved_characters = "()"
    if reserved_characters in value:
        raise ValidationError(f"El nombre no puede contener '{reserved_characters}'.")


class CapituloChoices(models.TextChoices):
    ACTIVO = "Activo"
    PASIVO = "Pasivo"
    PATRIMONIO = "Patrimonio"
    INGRESOS = "Ingresos"
    EGRESOS = "Egresos"


class Rubro(models.Model):
    """
    Store a single 'rubro' instance.
    """

    capitulo = models.CharField(
        verbose_name="Capítulo", max_length=50, choices=CapituloChoices.choices
    )
    name = models.CharField(verbose_name="Nombre", max_length=100)

    class Meta:
        verbose_name = "Rubro"
        verbose_name_plural = "Rubros"

    def __str__(self) -> str:
        return self.name


class Subrubro(models.Model):
    """
    Store a single 'subrubro' instance.
    """

    rubro = models.ForeignKey(
        Rubro,
        verbose_name="Rubro",
        on_delete=models.PROTECT,
        related_name="subrubros",
    )
    name = models.CharField(verbose_name="Nombre", max_length=100)

    def __str__(self) -> str:
        return self.name


class Cuenta(models.Model):
    """
    Store a single 'cuenta' instance.
    """

    subrubro = models.ForeignKey(
        Subrubro,
        verbose_name="Subrubro",
        on_delete=models.PROTECT,
        related_name="cuentas",
    )
    name = models.CharField(verbose_name="Nombre", max_length=100)
    debe = models.FloatField(verbose_name="Debe", default=0)
    haber = models.FloatField(verbose_name="Haber", default=0)

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
        ordering = ("subrubro",)
        constraints = [
            models.UniqueConstraint(
                fields=["subrubro", "name"],
                name="cuenta_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.subrubro} - {self.name}"

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        return super().save(*args, **kwargs)

    def calcular_debe(self):
        debe = 0
        if self.entries.exists():
            for entry in self.entries.all():
                debe += entry.debe
        self.save()
        # if self.customer.exists():
        #     for receipt in self.customer.receipts.filter(receipt_type="INVOICE"):
        #         debe += receipt.total
        # Falta hacer la parte cuando se le paga a un proveedor

    def calcular_haber(self):
        haber = 0
        if self.entries.exists():
            for entry in self.entries.all():
                haber += entry.haber
        self.save()
        # haber = 0
        # if self.supplier.exists():
        #     for receipt in self.supplier.receipts.filter(receipt_type="INVOICE"):
        #         haber += receipt.total
        # if self.customer.exists():
        #     for income_payment in self.customer.income_payments.all():
        #         haber += income_payment.amount
        # self.haber = haber
        # self.save()

    def calcular_saldo(self):
        return self.debe - self.haber


class TaxType(models.Model):
    """
    Store a single 'tax' instance.
    """

    name = models.CharField(
        verbose_name="Nombre", max_length=100, validators=[validate_tax_type_characters]
    )
    percentage = models.FloatField(
        verbose_name="Porcentaje",
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    create_date = models.DateTimeField(
        verbose_name="Fecha de creación",
        auto_now=True,
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Tipo de impuesto"
        verbose_name_plural = "Tipos de impuesto"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "percentage"],
                name="tax_type_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        return super().save(*args, **kwargs)


class Asiento(models.Model):
    """
    Store a single 'Asiento' instance.
    """

    create_date = models.DateField(
        verbose_name="Fecha de creación",
        blank=True,
        validators=[
            MaxValueValidator(
                timezone.now().date(),
                "La fecha de creación no puede ser posterior al día de hoy.",
            )
        ],
    )

    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"

    def __str__(self):
        return f"{self.id} - {self.create_date}"


class Entry(models.Model):
    """
    Store a single asiento 'Entry' instance, related to :model:`accounting.Asiento`.
    """

    asiento = models.ForeignKey(
        Asiento,
        verbose_name="Asiento",
        on_delete=models.PROTECT,
        related_name="entries",
    )
    cuenta = models.ForeignKey(
        Cuenta,
        verbose_name="Cuenta",
        on_delete=models.PROTECT,
        related_name="entries",
    )
    debe = models.FloatField(
        verbose_name="Debe",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    haber = models.FloatField(
        verbose_name="Haber",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"

    def __str__(self):
        return f"{self.asiento} - {self.cuenta}"

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from accounting.models import Asiento


def validate_is_numeric(value) -> None:
    if not value.isnumeric():
        raise ValidationError(
            "Asegúrese de que el valor sea solo de caracteres numéricos."
        )


class IvaSituationChoices(models.TextChoices):
    RM = "RM", "Responsable Monotributo"
    RI = "RI", "Responsable Inscripto"
    RNI = "RNI", "Responsable No Inscripto"
    EXC = "EX", "Exento"
    CF = "CF", "Consumidor Final"


class IdentificationTypeChoices(models.TextChoices):
    CUIT = "CUIT", "CUIT"
    PASSPORT = "PASSPORT", "Pasaporte"
    DNI = "DNI", "DNI"
    OTHER = "OTHER", "Otro"


class ReceiptLetterChoices(models.TextChoices):
    A = "A"
    B = "B"
    C = "C"
    X = "X"


class SaleConditionChoices(models.TextChoices):
    CASH = "CASH", "Contado efectivo"
    TERM15 = "TERM15", "A plazo - 15 días"
    TERM30 = "TERM30", "A plazo - 30 días"
    TERM60 = "TERM60", "A plazo - 60 días"
    OTHER = "OTHER", "Otro"


class BaseContact(models.Model):
    identification_type = models.CharField(
        verbose_name="Tipo de identificación",
        max_length=50,
        choices=IdentificationTypeChoices.choices,
        default=IdentificationTypeChoices.CUIT,
    )
    identification_number = models.CharField(
        verbose_name="Número de identificación",
        max_length=11,
        help_text="8 números sin puntos para DNI, 11 números sin guiones para CUIT/CUIL.",
        validators=[
            validate_is_numeric,
            MinLengthValidator(
                8, "Asegúrese de que este valor sea mayor o igual a 8 caracteres."
            ),
        ],
    )
    name = models.CharField(
        verbose_name="Nombre o Razón Social",
        max_length=200,
    )
    iva_situation = models.CharField(
        verbose_name="Situación frente IVA",
        max_length=100,
        choices=IvaSituationChoices.choices,
        default=IvaSituationChoices.RI,
    )
    address = models.CharField(verbose_name="Domicilio fiscal", max_length=200)
    phone_number = models.CharField(
        verbose_name="Número de teléfono",
        max_length=10,
        help_text="Código de area sin 0 y número sin 15.",
        validators=[
            validate_is_numeric,
            MinLengthValidator(
                10, "Asegúrese de que este valor sea igual a 10 caracteres."
            ),
        ],
    )
    notes = models.TextField(
        verbose_name="Notas",
        max_length=300,
        blank=True,
        null=True,
        help_text="Piso, número de departamento u otras aclaraciones.",
    )
    create_date = models.DateField(
        verbose_name="Fecha de alta",
        auto_now_add=True,
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación",
        auto_now=True,
    )

    class Meta:
        abstract = True
        ordering = ["name"]


class BaseInvoice(models.Model):
    issue_date = models.DateField(
        verbose_name="Fecha de emisión",
        default=date.today,
    )
    due_date = models.DateField(
        verbose_name="Fecha de vencimiento",
        default=date.today() + timedelta(days=15),
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación", auto_now=True
    )
    sale_condition = models.CharField(
        verbose_name="Condición de compra",
        max_length=50,
        choices=SaleConditionChoices.choices,
        default=SaleConditionChoices.CASH,
    )
    notes = models.TextField(
        verbose_name="Notas",
        max_length=300,
        blank=True,
        null=True,
    )
    cae = models.CharField(
        verbose_name="Número de CAE",
        max_length=100,
        blank=True,
        null=True,
        validators=[validate_is_numeric],
    )
    is_paid = models.BooleanField(
        verbose_name="Pagada",
        default=False,
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
    asiento = models.OneToOneField(
        Asiento,
        verbose_name="Asiento",
        on_delete=models.PROTECT,
        blank=True,
    )

    class Meta:
        abstract = True

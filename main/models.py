from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models


def is_operator(user):
    try:
        user.operator
        return True
    except ObjectDoesNotExist:
        return False


def validate_is_numeric(value):
    """
    Check the value to be numeric.
    """
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


class SaleTermTypeChoices(models.TextChoices):
    CASH = "CASH", "Contado"
    TERM15 = "TERM15", "A plazo - 15 días"
    TERM30 = "TERM30", "A plazo - 30 días"
    TERM60 = "TERM60", "A plazo - 60 días"
    OTHER = "OTHER", "Otro"


class PaymentOptionChoices(models.TextChoices):
    ADMIN = "ADMIN", "Administración"
    MARIANO = "MARIANO"
    OPERATOR = "OPERATOR", "Operario"


class BaseContact(models.Model):
    """
    Abstract model for extending in income and expenses.
    """

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
        ordering = ("name",)


class BaseReceipt(models.Model):
    """
    Abstract model for extending in income and expenses.
    """

    address = models.CharField(
        verbose_name="Domicilio",
        max_length=200,
        blank=True,
    )
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
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación", auto_now=True
    )
    location = models.CharField(
        verbose_name="Ubicación", max_length=50, blank=True, null=True
    )

    class Meta:
        abstract = True

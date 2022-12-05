from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from accounting.models import Cuenta


def validate_phone_number(value):
    """
    Validate the phone number's format and length is correct.
    """

    if not len(value) == 10 or not value.isnumeric():
        raise ValidationError("El teléfono debe contener 10 caracteres numéricos.")


class SituacionIvaChoices(models.TextChoices):
    RM = "RM", "Responsable Monotributo"
    RI = "RI", "Responsable Inscripto"
    RNI = "RNI", "Responsable No Inscripto"
    EXC = "EXC", "Excento"
    CF = "CF", "Consumidor Final"


class IdentificationTypeChoices(models.TextChoices):
    CUIT = "CUIT", "CUIT"
    PASSPORT = "PASSPORT", "Pasaporte"
    DNI = "DNI", "DNI"
    OTHER = "OTHER", "Otro"


class saleTermTypeChoices(models.TextChoices):
    CASH = "CASH", "Contado"
    TERM15 = "TERM15", "A plazo - 15 días"
    TERM30 = "TERM30", "A plazo - 30 días"
    TERM60 = "TERM60", "A plazo - 60 días"
    OTHER = "OTHER", "Otro"


class BaseContact(models.Model):
    """
    Store a single 'Contact' instance, related to :model:`accounting.Cuenta`.
    """

    cuenta = models.OneToOneField(
        Cuenta,
        verbose_name="Cuenta",
        on_delete=models.RESTRICT,
        blank=True,
    )
    identification_type = models.CharField(
        verbose_name="Tipo de identificación",
        max_length=50,
        choices=IdentificationTypeChoices.choices,
        default=IdentificationTypeChoices.CUIT,
    )
    identification_number = models.CharField(
        verbose_name="Número de identificación",
        max_length=20,
        help_text="8 números sin puntos para DNI, 11 números sin guiones para CUIT/CUIL",
    )
    name = models.CharField(
        verbose_name="Nombre o Razón Social",
        max_length=200,
    )
    situacion_iva = models.CharField(
        verbose_name="Situación frente IVA",
        max_length=100,
        choices=SituacionIvaChoices.choices,
        default=SituacionIvaChoices.RI,
    )
    address = models.CharField(verbose_name="Domicilio", max_length=200)
    location = models.CharField(verbose_name="Ubicación", max_length=50)
    phone_number = models.CharField(
        verbose_name="Número de teléfono",
        max_length=10,
        help_text="Código de area sin 0 y número sin 15.",
        validators=[validate_phone_number],
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
        default=date.today,
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación",
        auto_now=True,
    )

    class Meta:
        abstract = True


class BaseReceipt(models.Model):
    """
    Store a single 'Receipt' instance, related to :model:`income.Customer`.
    """

    issue_date = models.DateField(
        verbose_name="Fecha de emisión",
        default=date.today,
    )
    address = models.CharField(
        verbose_name="Domicilio",
        max_length=200,
    )
    location = models.CharField(
        verbose_name="Ubicación", max_length=50, blank=True, null=True
    )
    phone_number = models.CharField(
        verbose_name="Número de teléfono",
        max_length=10,
        help_text="Código de area sin 0 y número sin 15.",
        validators=[validate_phone_number],
    )
    due_date = models.DateField(
        verbose_name="Fecha de vencimiento",
        default=date.today() + timedelta(days=15),
    )
    notes = models.TextField(
        verbose_name="Notas",
        max_length=300,
        blank=True,
        null=True,
    )
    cai = models.CharField(
        verbose_name="Número de CAI",
        max_length=100,
        blank=True,
        null=True,
    )
    # is_paid = models.OneToOneField(
    #     "self",
    #     verbose_name="Tiene recibo",
    #     related_name="invoice",
    #     on_delete=models.RESTRICT,
    #     blank=True,
    #     null=True,
    # )
    sale_term = models.CharField(
        verbose_name="Plazo de venta",
        max_length=50,
        choices=saleTermTypeChoices.choices,
        default=saleTermTypeChoices.CASH,
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación", auto_now=True
    )
    subtotal = models.FloatField(
        verbose_name="Subtotal",
        default=0,
    )
    total = models.FloatField(
        verbose_name="Total",
        default=0,
    )

    class Meta:
        abstract = True
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        ordering = ("issue_date",)

    def clean(self):
        """
        Ckeck the due date is not before the issue date.
        """

        if self.due_date < self.issue_date:
            raise ValidationError(
                "La fecha de vencimiento no puede ser menor a la fecha de emisión."
            )


class Issuing(models.Model):
    """
    Store a single 'Client' instance, related to :model:`contabilidad.Cuenta`
    """

    identification_number = models.CharField(
        verbose_name="Número de CUIT",
        max_length=20,
        help_text="11 números sin guiones.",
        unique=True,
    )
    name = models.CharField(
        verbose_name="Nombre o Razón Social",
        max_length=200,
    )
    situacion_iva = models.CharField(
        verbose_name="Situación frente al IVA",
        max_length=100,
        choices=SituacionIvaChoices.choices,
    )
    address = models.CharField(verbose_name="Domicilio", max_length=200)
    create_date = models.DateTimeField(verbose_name="Fecha de alta", auto_now_add=True)
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación", auto_now=True
    )

    class Meta:
        verbose_name = "Emisor"
        verbose_name_plural = "Emisores"
        ordering = ("name",)

    def __str__(self):
        return self.name

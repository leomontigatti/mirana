from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


def validate_tax_type_characters(value):
    """
    Check the tax type name does not contain reserved characters.
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
    capitulo = models.CharField(
        "Capítulo", max_length=50, choices=CapituloChoices.choices
    )
    name = models.CharField("Nombre", max_length=100)

    class Meta:
        verbose_name = "Rubro"
        verbose_name_plural = "Rubros"

    def __str__(self):
        return self.name


class Subrubro(models.Model):
    rubro = models.ForeignKey(
        Rubro,
        models.RESTRICT,
        related_name="subrubros",
        verbose_name="Rubro",
    )
    name = models.CharField("Nombre", max_length=100)

    class Meta:
        verbose_name = "Subrubro"
        verbose_name_plural = "Subrubros"

    def __str__(self) -> str:
        return self.name


class Cuenta(models.Model):
    subrubro = models.ForeignKey(
        Subrubro,
        models.PROTECT,
        related_name="cuentas",
        verbose_name="Subrubro",
    )
    name = models.CharField("Nombre", max_length=100)
    debe = models.FloatField("Debe", default=0)
    haber = models.FloatField("Haber", default=0)

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
        ordering = ["subrubro"]
        constraints = [
            models.UniqueConstraint(
                fields=["subrubro", "name"],
                name="cuenta_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.subrubro} - {self.name}"

    def save(self, *args, **kwargs):
        # Upper case a cuenta's name to check uniqueness.
        self.name = self.name.upper()
        return super().save(*args, **kwargs)


class TaxType(models.Model):
    name = models.CharField(
        "Nombre", max_length=100, validators=[validate_tax_type_characters]
    )
    percentage = models.FloatField(
        "Alícuota",
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    create_date = models.DateTimeField(
        "Fecha de creación",
        auto_now=True,
    )
    change_date = models.DateTimeField(
        "Fecha de modificación",
        auto_now=True,
    )
    cuenta_activo = models.ForeignKey(
        Cuenta,
        models.PROTECT,
        related_name="taxtype_activo",
        verbose_name="Cuenta activo",
        limit_choices_to={"subrubro_id": 3},
    )
    cuenta_pasivo = models.ForeignKey(
        Cuenta,
        models.PROTECT,
        related_name="taxtype_pasivo",
        verbose_name="Cuenta pasivo",
        limit_choices_to={"subrubro_id": 21},
    )

    class Meta:
        verbose_name = "Tipo de impuesto"
        verbose_name_plural = "Tipos de impuesto"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "percentage"],
                name="tax_type_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

    def get_update_url(self):
        return reverse("taxtype_update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Upper case a tax's name to check uniqueness.
        self.name = self.name.upper()
        return super().save(*args, **kwargs)


class Asiento(models.Model):
    create_date = models.DateField(
        "Fecha de creación",
        blank=True,
        auto_now=True,
    )

    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"

    def __str__(self):
        return f"{self.pk} - {self.create_date}"


class Entry(models.Model):
    asiento = models.ForeignKey(
        Asiento,
        models.CASCADE,
        related_name="entries",
        verbose_name="Asiento",
    )
    cuenta = models.ForeignKey(
        Cuenta,
        models.PROTECT,
        related_name="entries",
        verbose_name="Cuenta",
    )
    debe = models.FloatField(
        "Debe",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )
    haber = models.FloatField(
        "Haber",
        default=0,
        validators=[
            MinValueValidator(0, "Asegúrese de que este valor sea mayor o igual a 0.")
        ],
    )

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ["-debe"]

    def __str__(self):
        return f"{self.asiento} - {self.cuenta}"

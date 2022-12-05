from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse
from django.urls import reverse


def validate_taxtype_characters(value):
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
    Store a single 'Rubro' instance.
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
    Store a single 'Subrubro' instance.
    """

    rubro = models.ForeignKey(
        Rubro,
        verbose_name="Rubro",
        on_delete=models.RESTRICT,
        related_name="subrubros",
    )
    name = models.CharField(verbose_name="Nombre", max_length=100)

    def __str__(self) -> str:
        return self.name


class Cuenta(models.Model):
    """
    Store a single 'Cuenta' instance.
    """

    subrubro = models.ForeignKey(
        Subrubro,
        verbose_name="Subrubro",
        on_delete=models.RESTRICT,
        related_name="cuentas",
    )
    name = models.CharField(
        verbose_name="Nombre",
        max_length=100,
    )
    debe = models.FloatField(
        verbose_name="Debe",
        default=0,
    )
    haber = models.FloatField(
        verbose_name="Haber",
        default=0,
    )

    def __str__(self) -> str:
        return self.name

    def aumenta_debe(self, amount) -> None:
        self.debe += amount
        self.save()

    def aumenta_haber(self, amount) -> None:
        self.haber += amount
        self.save()

    def calcular_saldo(self):
        return self.debe - self.haber


class TaxType(models.Model):
    """
    Store a single 'Tax' instance.
    """

    name = models.CharField(
        verbose_name="Nombre",
        max_length=200,
    )
    percentage = models.FloatField(verbose_name="Porcentaje")
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

    def __str__(self) -> str:
        return f"{self.name} ({self.percentage}%)"

from django.core.validators import StepValueValidator
from django.db import models

from accounting.models import Cuenta


class ServiceType(models.Model):
    """
    Store a single 'service type' instance, related to :model:`accounting.Cuenta`,
    :model:`inventory.Warehouse` and :model:`inventory.Stock`.
    """

    cuenta = models.ForeignKey(
        Cuenta,
        verbose_name="Cuenta de ventas",
        on_delete=models.PROTECT,
        related_name="service_type",
        limit_choices_to={"subrubro": 28},
        default=15,
    )
    description = models.CharField(
        verbose_name="Descripción",
        max_length=200,
    )
    reference_code = models.CharField(
        verbose_name="Código de referencia",
        max_length=20,
        help_text="Código único de identificación del producto. Máximo 20 caracteres.",
        unique=True,
    )
    stock = models.ForeignKey(
        "Stock",
        verbose_name="Stock",
        on_delete=models.PROTECT,
        related_name="service_type",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        verbose_name="Activo",
        default=True,
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
        verbose_name = "Tipo de servicio"
        verbose_name_plural = "Tipos de servicio"

    def __str__(self):
        return self.description


class Warehouse(models.Model):
    """
    Store a single 'Warehouse' instance.
    """

    name = models.CharField(verbose_name="Nombre", max_length=50)
    address = models.CharField(verbose_name="Domicilio", max_length=200)
    notes = models.TextField(
        verbose_name="Notas",
        max_length=300,
        blank=True,
        null=True,
        help_text="Piso, número de departamento u otras aclaraciones.",
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
        verbose_name = "Depósito"
        verbose_name_plural = "Depósitos"

    def __str__(self):
        return f"{self.name.title()}"


class Stock(models.Model):
    """
    Store a single 'stock' instance, related to :model:`inventory.Warehouse`.
    """

    product = models.CharField(verbose_name="Producto", max_length=200)
    cuenta = models.ForeignKey(
        Cuenta,
        verbose_name="Cuenta de inventario",
        on_delete=models.PROTECT,
        related_name="stock",
        limit_choices_to={"subrubro": 9},
        default=7,
    )
    warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Depósito",
        on_delete=models.PROTECT,
        related_name="stock",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Cantidad",
        default=0,
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
        verbose_name = "Stock"
        verbose_name_plural = "Stock"
        ordering = ("product", "warehouse", "amount")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse"],
                name="stock_uniqueness",
            )
        ]

    def __str__(self):
        return f"{self.product} - Depósito {self.warehouse} - {self.amount} unidades"

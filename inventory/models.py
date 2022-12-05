from django.db import models

from accounting.models import Cuenta


class MeasurementUnitChoices(models.TextChoices):
    SERVICE = "SERVICE", "Servicio"
    UNIT = "UNIT", "Unidad"
    KILOGRAM = "KILOGRAM", "Kilogramo"
    GRAM = "GRAM", "Gramo"
    METER = "METER", "Metro"
    SQUARE_METER = "SQUARE METER", "Metro cuadrado"
    CUBIC_METER = "CUBIC METER", "Metro cúbico"
    LITER = "LITER", "Litro"
    MILLILITER = "MILLILITER", "Mililitro"


class Category(models.Model):
    """
    Store a single 'Category' instance.
    """

    name = models.CharField(
        verbose_name="Nombre",
        max_length=200,
        unique=True,
    )
    notes = models.TextField(
        verbose_name="Notas",
        max_length=300,
        blank=True,
        null=True,
        help_text="Descripción",
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
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ("name",)

    def __str__(self):
        return self.name.title()


class ProductType(models.Model):
    """
    Store a single 'ProductType' instance, related to :model:`accounting.Cuenta`
    and :model:`inventory.Warehouse`.
    """

    cuenta = models.ForeignKey(
        Cuenta,
        verbose_name="Cuenta contable",
        on_delete=models.RESTRICT,
        related_name="products",
        limit_choices_to={"subrubro": 29},
    )
    name = models.CharField(
        verbose_name="Nombre",
        max_length=200,
    )
    reference_code = models.CharField(
        verbose_name="Código de referencia",
        max_length=20,
        help_text="Código único de indentificación del producto. Máximo 20 caracteres.",
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Unidad de medida",
        max_length=20,
        choices=MeasurementUnitChoices.choices,
        default=MeasurementUnitChoices.SERVICE,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Categoría",
        on_delete=models.RESTRICT,
        related_name="products",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Descripción",
        max_length=300,
        blank=True,
        null=True,
        help_text="Descripción.",
    )
    create_date = models.DateTimeField(
        verbose_name="Fecha de creación",
        auto_now=True,
    )
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación",
        auto_now=True,
    )
    is_active = models.BooleanField(
        verbose_name="Activo",
        default=True,
    )

    class Meta:
        verbose_name = "Tipo de producto"
        verbose_name_plural = "Tipos de producto"
        ordering = ("-change_date",)

    def __str__(self):
        return self.name.title()


class Warehouse(models.Model):
    """
    Store a single 'Warehouse' instance.
    """

    name = models.CharField(verbose_name="Nombre", max_length=50)
    address = models.CharField(verbose_name="Domicilio", max_length=200)
    location = models.CharField(verbose_name="Ubicación", max_length=50)
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
    Store a single 'Stock' instance, related to :model:`inventory.ProductType`
    and :model:`inventory.Warehouse`.
    """

    cuenta = models.ForeignKey(
        Cuenta,
        verbose_name="Cuenta de inventario",
        on_delete=models.RESTRICT,
        related_name="stocks",
        limit_choices_to={"subrubro": 10},
    )
    producttype = models.ForeignKey(
        ProductType,
        verbose_name="Producto",
        on_delete=models.RESTRICT,
        related_name="stocks",
        limit_choices_to={"is_active": True},
    )
    warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Depósito",
        on_delete=models.RESTRICT,
        related_name="stocks",
    )
    amount = models.FloatField(
        verbose_name="Cantidad",
        max_length=20,
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
        verbose_name_plural = "Stocks"
        ordering = (
            "producttype",
            "warehouse",
            "amount",
        )

    def __str__(self):
        return f"{self.producttype.name} {self.warehouse.name} {self.amount}"

from django.db import models

from accounting.models import TaxType
from inventory.models import ProductType
from main.models import BaseContact, BaseReceipt


class Customer(BaseContact):
    """
    Store a single 'Customer' instance, inherits from :model:`main.BaseContact`.
    """

    class Meta:
        verbose_name: str = "Cliente"
        verbose_name_plural: str = "Clientes"
        ordering: tuple = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["identification_type", "identification_number"],
                name="customer_uniqueness",
            )
        ]

    def __str__(self) -> str:
        return self.name


class Receipt(BaseReceipt):
    """
    Store a single 'Receipt' instance, inherits from :model:`main.BaseReceipt`
    and relates to :model:`income.Customer`.
    """

    customer = models.ForeignKey(
        Customer,
        verbose_name="Cliente",
        related_name="receipts",
        on_delete=models.RESTRICT,
    )
    receipt_type: str = models.CharField(
        verbose_name="Tipo de comprobante",
        max_length=50,
        blank=True,
    )
    has_invoice = models.OneToOneField(
        "self",
        verbose_name="Tiene factura",
        related_name="hiring",
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    has_electronic_invoice = models.BooleanField(
        verbose_name="Tiene factura electrónica",
        default=False,
    )
    has_hiring = models.OneToOneField(
        "self",
        verbose_name="Tiene contratación",
        related_name="budget",
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    is_placed = models.BooleanField(
        verbose_name="Colocado",
        default=False,
    )
    is_clean = models.BooleanField(
        verbose_name="Limpio",
        default=True,
    )

    def __str__(self) -> str:
        return f"{self.customer} - {self.address}"


class Product(models.Model):
    """
    Store a single 'Product' instance, related to :model:`inventory.ProductType`,
    :model:`income.Receipt`.
    """

    product_type = models.ForeignKey(
        ProductType,
        verbose_name="Tipo de producto",
        related_name="products",
        on_delete=models.RESTRICT,
        limit_choices_to={"is_active": True},
    )
    amount = models.FloatField(verbose_name="Cantidad", default=0)
    unitario = models.FloatField(verbose_name="Unitario", default=0)
    subtotal = models.FloatField(verbose_name="Subtotal", default=0)
    receipt = models.ForeignKey(
        Receipt,
        verbose_name="Comprobante",
        related_name="products",
        on_delete=models.RESTRICT,
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ("product_type",)

    def __str__(self) -> str:
        return f"{self.product_type}"


class Tax(models.Model):
    """
    Store a single 'Tax' instance, related to :model:`accounting.TaxType`,
    :model:`income.Receipt`.
    """

    tax_type = models.ForeignKey(
        TaxType,
        verbose_name="Tipo de impuesto",
        related_name="taxes",
        on_delete=models.RESTRICT,
    )
    subtotal = models.FloatField(verbose_name="Subtotal", default=0)
    receipt = models.ForeignKey(
        Receipt,
        verbose_name="Comprobante",
        related_name="taxes",
        on_delete=models.RESTRICT,
    )

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"
        ordering = ("tax_type",)

    def __str__(self) -> str:
        return f"{self.tax_type}"

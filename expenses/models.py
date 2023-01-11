from django.db import models

from main.models import BaseContact


class ReceiptTypeChoices(models.TextChoices):
    PURCHASE_ORDER = "PURCHASE_ORDER", "Orden de compra"
    INVOICE = "INVOICE", "Factura"


class Supplier(BaseContact):
    """
    Store a single 'Supplier' instance, inherits from :model:`main.BaseContact`.
    """

    class Meta:
        verbose_name: str = "Proveedor"
        verbose_name_plural: str = "Proveedores"
        ordering: tuple = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["identification_type", "identification_number"],
                name="supplier_uniqueness",
            )
        ]

    def __str__(self) -> str:
        return self.name

    # def save(self, *args, **kwargs) -> None:
    #     self.full_clean()
    #     super().save(*args, **kwargs)


class Receipt(models.Model):
    """
    Store a single 'Receipt' instance, inherits from :model:`main.BaseReceipt`
    and relates to :model:`income.Supplier`.
    """

    supplier: Supplier = models.ForeignKey(
        Supplier,
        verbose_name="Proveedor",
        related_name="receipts",
        on_delete=models.PROTECT,
    )
    receipt_type: str = models.CharField(
        verbose_name="Tipo de comprobante",
        max_length=50,
        choices=ReceiptTypeChoices.choices,
    )

    class Meta:
        verbose_name: str = "Comprobante"
        verbose_name_plural: str = "Comprobantes"
        ordering: tuple = ("receipt_type",)

    def __str__(self) -> str:
        return f"{self.id} {self.customer}"

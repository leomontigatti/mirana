from django.db import models
from django.urls import reverse


class StockStatusChoices(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Disponible"
    PROMISED = "PROMISED", "Prometido"
    PLACED = "PLACED", "Colocado"
    MAINTENANCE = "MAINTENANCE", "En mantenimiento"


class ServiceType(models.Model):
    description = models.CharField(
        "Descripción",
        max_length=200,
        unique=True,
    )
    is_active = models.BooleanField(
        "Activo",
        default=True,
    )
    can_be_updated = models.BooleanField(
        "Puede modificarse",
        default=True,
    )
    create_date = models.DateTimeField(
        "Fecha de creación",
        auto_now=True,
    )
    change_date = models.DateTimeField(
        "Fecha de modificación",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Tipo de servicio"
        verbose_name_plural = "Tipos de servicio"
        ordering = ["description"]

    def __str__(self):
        return self.description.title()

    def get_absolute_url(self):
        return reverse("servicetype_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("servicetype_update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        self.description = self.description.upper()
        return super().save(*args, **kwargs)


class Bathroom(models.Model):
    service_type = models.ForeignKey(
        ServiceType,
        models.PROTECT,
        related_name="bathrooms",
        verbose_name="Tipo de servicio",
    )
    status = models.CharField(
        "Estado",
        max_length=50,
        default=StockStatusChoices.AVAILABLE,
        choices=StockStatusChoices.choices,
    )
    create_date = models.DateTimeField(
        "Fecha de creación",
        auto_now=True,
    )
    change_date = models.DateTimeField(
        "Fecha de modificación",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Baño"
        verbose_name_plural = "Baños"


class Workshop(models.Model):
    service_type = models.ForeignKey(
        ServiceType,
        models.PROTECT,
        related_name="workshops",
        verbose_name="Tipo de servicio",
    )
    status = models.CharField(
        "Estado",
        max_length=50,
        default=StockStatusChoices.AVAILABLE,
        choices=StockStatusChoices.choices,
    )
    create_date = models.DateTimeField(
        "Fecha de creación",
        auto_now=True,
    )
    change_date = models.DateTimeField(
        "Fecha de modificación",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Obrador"
        verbose_name_plural = "Obradores"


# class Stock(models.Model):
#     product = models.CharField("Producto", max_length=200)
#     service_type = models.ForeignKey(
#         ServiceType,
#         models.PROTECT,
#         related_name="stocks",
#         verbose_name="Tipo de servicio",
#     )
#     amount = models.PositiveIntegerField(
#         "Cantidad",
#         default=0,
#     )
#     status = models.CharField(
#         "Estado",
#         max_length=50,
#         default=StockStatusChoices.AVAILABLE,
#         choices=StockStatusChoices.choices,
#     )
#     create_date = models.DateTimeField(
#         "Fecha de creación",
#         auto_now=True,
#     )
#     change_date = models.DateTimeField(
#         "Fecha de modificación",
#         auto_now=True,
#     )

#     class Meta:
#         verbose_name: str = "Stock"
#         verbose_name_plural: str = "Stock"
#         ordering: List[str] = ["product", "warehouse", "amount"]
#         constraints: List[Any] = [
#             models.UniqueConstraint(
#                 fields=["product", "warehouse", "status"],
#                 name="stock_uniqueness",
#             ),
#         ]

#     def __str__(self) -> str:
#         return f"{self.warehouse} - {self.product.title()} {self.get_status_display()}"  # type: ignore

#     def get_absolute_url(self) -> str:
#         return reverse("stock_detail", kwargs={"pk": self.pk})

#     def get_update_url(self) -> str:
#         return reverse("stock_update", kwargs={"pk": self.pk})

#     def save(self, *args, **kwargs) -> None:
#         # Upper case a product's name to check uniqueness.
#         self.product = self.product.upper()
#         return super().save(*args, **kwargs)

#     def set_amount(self) -> None:
#         total: int = 0
#         for movement in self.stock_movements.all():  # type: ignore
#             total += movement.amount
#         self.amount = total


class ServiceTypeMovement(models.Model):
    create_date = models.DateField(
        "Fecha de creación",
        auto_now=True,
    )
    service_type = models.ForeignKey(
        ServiceType,
        models.PROTECT,
        related_name="servicetype_movements",
        verbose_name="Servicio",
    )
    sales_invoice = models.ForeignKey(
        "income.SalesInvoice",
        models.PROTECT,
        related_name="servicetype_movements",
        verbose_name="Factura de venta",
        null=True,
    )
    amount = models.FloatField("Monto")

    class Meta:
        verbose_name = "Movimiento de servicio"
        verbose_name_plural = "Movimientos de servicio"
        ordering = ["create_date"]

    def __str__(self):
        return f"{self.service_type} - {self.amount}"


class StockMovement(models.Model):
    create_date = models.DateField(
        "Fecha de creación",
        auto_now=True,
    )
    stock = models.CharField(
        "Stock",
        max_length=50,
        default="BATHROOM",
        choices=[("BATHROOM", "Baño"), ("WORKSHOP", "Obrador")],
    )
    status = models.CharField(
        "Estado",
        max_length=50,
        default=StockStatusChoices.AVAILABLE,
        choices=StockStatusChoices.choices,
    )
    service = models.ForeignKey(
        "income.Service",
        models.CASCADE,
        related_name="stock_movements",
        verbose_name="Servicio",
        null=True,
    )
    task = models.ForeignKey(
        "configuration.Task",
        models.CASCADE,
        related_name="stock_movements",
        verbose_name="Tarea",
        null=True,
    )
    amount = models.SmallIntegerField("Cantidad")
    reason = models.TextField("Motivo", max_length=300, null=True)

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        ordering = ["create_date"]

    def __str__(self):
        return f"{self.stock} - {self.amount}"

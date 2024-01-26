import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("configuration", "0001_initial"),
        ("income", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="Descripción"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
                (
                    "can_be_updated",
                    models.BooleanField(default=True, verbose_name="Puede modificarse"),
                ),
                (
                    "create_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "change_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo de servicio",
                "verbose_name_plural": "Tipos de servicio",
                "ordering": ["description"],
            },
        ),
        migrations.CreateModel(
            name="Bathroom",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AVAILABLE", "Disponible"),
                            ("PROMISED", "Prometido"),
                            ("PLACED", "Colocado"),
                            ("MAINTENANCE", "En mantenimiento"),
                        ],
                        default="AVAILABLE",
                        max_length=50,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "create_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "change_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                (
                    "service_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bathrooms",
                        to="inventory.servicetype",
                        verbose_name="Tipo de servicio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Baño",
                "verbose_name_plural": "Baños",
            },
        ),
        migrations.CreateModel(
            name="ServiceTypeMovement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "create_date",
                    models.DateField(auto_now=True, verbose_name="Fecha de creación"),
                ),
                ("amount", models.FloatField(verbose_name="Monto")),
                (
                    "sales_invoice",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="servicetype_movements",
                        to="income.salesinvoice",
                        verbose_name="Factura de venta",
                    ),
                ),
                (
                    "service_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="servicetype_movements",
                        to="inventory.servicetype",
                        verbose_name="Servicio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Movimiento de servicio",
                "verbose_name_plural": "Movimientos de servicio",
                "ordering": ["create_date"],
            },
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "create_date",
                    models.DateField(auto_now=True, verbose_name="Fecha de creación"),
                ),
                (
                    "stock",
                    models.CharField(
                        choices=[("BATHROOM", "Baño"), ("WORKSHOP", "Obrador")],
                        default="BATHROOM",
                        max_length=50,
                        verbose_name="Stock",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AVAILABLE", "Disponible"),
                            ("PROMISED", "Prometido"),
                            ("PLACED", "Colocado"),
                            ("MAINTENANCE", "En mantenimiento"),
                        ],
                        default="AVAILABLE",
                        max_length=50,
                        verbose_name="Estado",
                    ),
                ),
                ("amount", models.SmallIntegerField(verbose_name="Cantidad")),
                (
                    "reason",
                    models.TextField(max_length=300, null=True, verbose_name="Motivo"),
                ),
                (
                    "service",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_movements",
                        to="income.service",
                        verbose_name="Servicio",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_movements",
                        to="configuration.task",
                        verbose_name="Tarea",
                    ),
                ),
            ],
            options={
                "verbose_name": "Movimiento de stock",
                "verbose_name_plural": "Movimientos de stock",
                "ordering": ["create_date"],
            },
        ),
        migrations.CreateModel(
            name="Workshop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AVAILABLE", "Disponible"),
                            ("PROMISED", "Prometido"),
                            ("PLACED", "Colocado"),
                            ("MAINTENANCE", "En mantenimiento"),
                        ],
                        default="AVAILABLE",
                        max_length=50,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "create_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "change_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                (
                    "service_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="workshops",
                        to="inventory.servicetype",
                        verbose_name="Tipo de servicio",
                    ),
                ),
            ],
            options={
                "verbose_name": "Obrador",
                "verbose_name_plural": "Obradores",
            },
        ),
    ]

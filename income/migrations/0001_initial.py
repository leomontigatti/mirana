import datetime

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import main.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounting", "0001_initial"),
        ("configuration", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
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
                ("address", models.CharField(max_length=200, verbose_name="Domicilio")),
                ("lat", models.CharField(max_length=20, verbose_name="Latitud")),
                ("lng", models.CharField(max_length=20, verbose_name="Longitud")),
                (
                    "issue_date",
                    models.DateField(
                        default=datetime.date.today, verbose_name="Fecha de emisión"
                    ),
                ),
                (
                    "sale_condition",
                    models.CharField(
                        choices=[
                            ("CASH", "Contado efectivo"),
                            ("TERM15", "A plazo - 15 días"),
                            ("TERM30", "A plazo - 30 días"),
                            ("TERM60", "A plazo - 60 días"),
                            ("OTHER", "Otro"),
                        ],
                        default="CASH",
                        max_length=50,
                        verbose_name="Condición de venta",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        default="Este presupuesto tiene validez por 15 días desde su fecha de emisión.",
                        max_length=300,
                        null=True,
                        verbose_name="Notas",
                    ),
                ),
                (
                    "subtotal",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Subtotal",
                    ),
                ),
                (
                    "total",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Total",
                    ),
                ),
            ],
            options={
                "verbose_name": "Presupuesto",
                "verbose_name_plural": "Presupuestos",
                "ordering": ["issue_date"],
            },
        ),
        migrations.CreateModel(
            name="Customer",
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
                    "identification_type",
                    models.CharField(
                        choices=[
                            ("CUIT", "CUIT"),
                            ("PASSPORT", "Pasaporte"),
                            ("DNI", "DNI"),
                            ("OTHER", "Otro"),
                        ],
                        default="CUIT",
                        max_length=50,
                        verbose_name="Tipo de identificación",
                    ),
                ),
                (
                    "identification_number",
                    models.CharField(
                        help_text="8 números sin puntos para DNI, 11 números sin guiones para CUIT/CUIL.",
                        max_length=11,
                        validators=[
                            main.models.validate_is_numeric,
                            django.core.validators.MinLengthValidator(
                                8,
                                "Asegúrese de que este valor sea mayor o igual a 8 caracteres.",
                            ),
                        ],
                        verbose_name="Número de identificación",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200, verbose_name="Nombre o Razón Social"
                    ),
                ),
                (
                    "iva_situation",
                    models.CharField(
                        choices=[
                            ("RM", "Responsable Monotributo"),
                            ("RI", "Responsable Inscripto"),
                            ("RNI", "Responsable No Inscripto"),
                            ("EX", "Exento"),
                            ("CF", "Consumidor Final"),
                        ],
                        default="RI",
                        max_length=100,
                        verbose_name="Situación frente IVA",
                    ),
                ),
                (
                    "address",
                    models.CharField(max_length=200, verbose_name="Domicilio fiscal"),
                ),
                (
                    "phone_number",
                    models.CharField(
                        help_text="Código de area sin 0 y número sin 15.",
                        max_length=10,
                        validators=[
                            main.models.validate_is_numeric,
                            django.core.validators.MinLengthValidator(
                                10,
                                "Asegúrese de que este valor sea igual a 10 caracteres.",
                            ),
                        ],
                        verbose_name="Número de teléfono",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Piso, número de departamento u otras aclaraciones.",
                        max_length=300,
                        null=True,
                        verbose_name="Notas",
                    ),
                ),
                (
                    "create_date",
                    models.DateField(auto_now_add=True, verbose_name="Fecha de alta"),
                ),
                (
                    "change_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                (
                    "has_whatsapp_acceptance",
                    models.BooleanField(
                        default=False, verbose_name="Acepta mensajes de WhatsApp"
                    ),
                ),
            ],
            options={
                "verbose_name": "Cliente",
                "verbose_name_plural": "Clientes",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CustomerMovement",
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
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de creación"
                    ),
                ),
                ("amount", models.FloatField(verbose_name="Monto")),
            ],
            options={
                "verbose_name": "Movimiento de cliente",
                "verbose_name_plural": "Movimientos de clientes",
                "ordering": ["-pk"],
            },
        ),
        migrations.CreateModel(
            name="Hiring",
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
                ("address", models.CharField(max_length=200, verbose_name="Domicilio")),
                ("lat", models.CharField(max_length=20, verbose_name="Latitud")),
                ("lng", models.CharField(max_length=20, verbose_name="Longitud")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PLACING_PENDING", "Colocación pendiente"),
                            ("PENDING_BATHROOM", "Colocación de baño pendiente"),
                            ("PENDING_WORKSHOP", "Colocación de obrador pendiente"),
                            ("ONGOING", "En curso"),
                            ("CLEANING_PENDING", "Limpieza pendiente"),
                            ("COLLECTION_PENDING", "Cobro pendiente"),
                            ("CHARGED", "Cobrada"),
                        ],
                        default="PLACING_PENDING",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="Fecha de inicio")),
                ("end_date", models.DateField(verbose_name="Fecha de finalización")),
                (
                    "notes",
                    models.TextField(
                        blank=True, max_length=300, null=True, verbose_name="Notas"
                    ),
                ),
            ],
            options={
                "verbose_name": "Contratación",
                "verbose_name_plural": "Contrataciones",
                "ordering": ["-pk"],
            },
        ),
        migrations.CreateModel(
            name="IncomePayment",
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
                    "reference",
                    models.CharField(
                        blank=True,
                        help_text="Número de cheque, transferencia o depósito.",
                        max_length=50,
                        null=True,
                        verbose_name="Referencia",
                    ),
                ),
                (
                    "amount",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Monto",
                    ),
                ),
                (
                    "issue_date",
                    models.DateField(
                        default=datetime.date.today, verbose_name="Fecha de emisión"
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
                "verbose_name": "Recibo de cobro",
                "verbose_name_plural": "Recibos de cobro",
                "ordering": ["-pk"],
            },
        ),
        migrations.CreateModel(
            name="SalesInvoice",
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
                    "issue_date",
                    models.DateField(
                        default=datetime.date.today, verbose_name="Fecha de emisión"
                    ),
                ),
                (
                    "due_date",
                    models.DateField(
                        default=datetime.date(2024, 2, 10),
                        verbose_name="Fecha de vencimiento",
                    ),
                ),
                (
                    "change_date",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de modificación"
                    ),
                ),
                (
                    "sale_condition",
                    models.CharField(
                        choices=[
                            ("CASH", "Contado efectivo"),
                            ("TERM15", "A plazo - 15 días"),
                            ("TERM30", "A plazo - 30 días"),
                            ("TERM60", "A plazo - 60 días"),
                            ("OTHER", "Otro"),
                        ],
                        default="CASH",
                        max_length=50,
                        verbose_name="Condición de compra",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, max_length=300, null=True, verbose_name="Notas"
                    ),
                ),
                (
                    "cae",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        validators=[main.models.validate_is_numeric],
                        verbose_name="Número de CAE",
                    ),
                ),
                ("is_paid", models.BooleanField(default=False, verbose_name="Pagada")),
                (
                    "subtotal",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Subtotal",
                    ),
                ),
                (
                    "total",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Total",
                    ),
                ),
                (
                    "letter",
                    models.CharField(
                        blank=True,
                        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("X", "X")],
                        max_length=1,
                        null=True,
                        verbose_name="Letra",
                    ),
                ),
                (
                    "sales_point",
                    models.CharField(
                        blank=True,
                        max_length=3,
                        null=True,
                        validators=[main.models.validate_is_numeric],
                        verbose_name="Punto de venta",
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        blank=True,
                        max_length=9,
                        null=True,
                        validators=[main.models.validate_is_numeric],
                        verbose_name="Número",
                    ),
                ),
                (
                    "has_electronic_invoice",
                    models.BooleanField(
                        default=False, verbose_name="Tiene factura electrónica"
                    ),
                ),
            ],
            options={
                "verbose_name": "Factura de venta",
                "verbose_name_plural": "Facturas de venta",
                "ordering": ["-pk"],
            },
        ),
        migrations.CreateModel(
            name="Service",
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
                    "amount",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Cantidad"
                    ),
                ),
                (
                    "unitario",
                    models.FloatField(
                        blank=True,
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Unitario",
                    ),
                ),
                (
                    "service_subtotal",
                    models.FloatField(
                        blank=True,
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Subtotal",
                    ),
                ),
            ],
            options={
                "verbose_name": "Servicio",
                "verbose_name_plural": "Servicios",
            },
        ),
        migrations.CreateModel(
            name="Tax",
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
                    "tax_subtotal",
                    models.FloatField(
                        blank=True,
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Subtotal",
                    ),
                ),
            ],
            options={
                "verbose_name": "Impuesto",
                "verbose_name_plural": "Impuestos",
            },
        ),
        migrations.AddConstraint(
            model_name="customer",
            constraint=models.UniqueConstraint(
                fields=("identification_type", "identification_number"),
                name="customer_uniqueness",
            ),
        ),
        migrations.AddField(
            model_name="budget",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="budgets",
                to="income.customer",
                verbose_name="Cliente",
            ),
        ),
        migrations.AddField(
            model_name="customermovement",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_movements",
                to="income.customer",
                verbose_name="Cliente",
            ),
        ),
        migrations.AddField(
            model_name="hiring",
            name="budget",
            field=models.OneToOneField(
                blank=True,
                limit_choices_to={"hiring__isnull": True},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hiring",
                to="income.budget",
                verbose_name="Presupuesto",
            ),
        ),
        migrations.AddField(
            model_name="hiring",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hiring",
                to="income.customer",
                verbose_name="Cliente",
            ),
        ),
        migrations.AddField(
            model_name="incomepayment",
            name="asiento",
            field=models.OneToOneField(
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="income_payment",
                to="accounting.asiento",
                verbose_name="Asiento",
            ),
        ),
        migrations.AddField(
            model_name="incomepayment",
            name="collector",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="income_payments",
                to="configuration.collector",
                verbose_name="Cobrador",
            ),
        ),
        migrations.AddField(
            model_name="incomepayment",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="income_payments",
                to="income.customer",
                verbose_name="Cliente",
            ),
        ),
        migrations.AddField(
            model_name="incomepayment",
            name="method",
            field=models.ForeignKey(
                limit_choices_to={"is_active": True},
                on_delete=django.db.models.deletion.PROTECT,
                related_name="income_payments",
                to="configuration.paymentmethod",
                verbose_name="Forma de pago",
            ),
        ),
        migrations.AddField(
            model_name="customermovement",
            name="payment",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_movement",
                to="income.incomepayment",
                verbose_name="Recibo de cobro",
            ),
        ),
        migrations.AddField(
            model_name="salesinvoice",
            name="asiento",
            field=models.OneToOneField(
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="accounting.asiento",
                verbose_name="Asiento",
            ),
        ),
        migrations.AddField(
            model_name="salesinvoice",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="invoices",
                to="income.customer",
                verbose_name="Cliente",
            ),
        ),
        migrations.AddField(
            model_name="salesinvoice",
            name="hiring",
            field=models.OneToOneField(
                blank=True,
                limit_choices_to={"sales_invoice__isnull": True},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sales_invoice",
                to="income.hiring",
                verbose_name="Contratación",
            ),
        ),
        migrations.AddField(
            model_name="incomepayment",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_paid": False},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="income_payments",
                to="income.salesinvoice",
                verbose_name="A imputar en",
            ),
        ),
        migrations.AddField(
            model_name="customermovement",
            name="invoice",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_movement",
                to="income.salesinvoice",
                verbose_name="Factura de venta",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="budget",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="services",
                to="income.budget",
                verbose_name="Presupuesto",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="hiring",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="services",
                to="income.hiring",
                verbose_name="Contratación",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="services",
                to="income.salesinvoice",
                verbose_name="Factura de venta",
            ),
        ),
    ]

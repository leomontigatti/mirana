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
            name="Supplier",
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
            ],
            options={
                "verbose_name": "Proveedor",
                "verbose_name_plural": "Proveedores",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SupplierMovement",
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
            ],
            options={
                "verbose_name": "Movimiento de proveedor",
                "verbose_name_plural": "Movimientos de proveedor",
                "ordering": ["-pk"],
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
        migrations.CreateModel(
            name="ExpensesInvoice",
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
                        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("X", "X")],
                        default="A",
                        max_length=1,
                        verbose_name="Letra",
                    ),
                ),
                (
                    "sales_point",
                    models.CharField(
                        max_length=3,
                        validators=[main.models.validate_is_numeric],
                        verbose_name="Punto de venta",
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        max_length=9,
                        validators=[main.models.validate_is_numeric],
                        verbose_name="Número",
                    ),
                ),
                (
                    "asiento",
                    models.OneToOneField(
                        blank=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="accounting.asiento",
                        verbose_name="Asiento",
                    ),
                ),
                (
                    "cuenta_egreso",
                    models.ForeignKey(
                        limit_choices_to={"subrubro": 36},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="expenses_invoices",
                        to="accounting.cuenta",
                        verbose_name="Cuenta de egreso",
                    ),
                ),
            ],
            options={
                "verbose_name": "Factura de gastos",
                "verbose_name_plural": "Facturas de gastos",
                "ordering": ["-issue_date"],
            },
        ),
        migrations.CreateModel(
            name="Expense",
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
                    models.CharField(max_length=100, verbose_name="Descripción"),
                ),
                (
                    "amount",
                    models.PositiveIntegerField(default=0, verbose_name="Cantidad"),
                ),
                (
                    "unitario",
                    models.FloatField(
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
                    "expense_subtotal",
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
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expenses",
                        to="expenses.expensesinvoice",
                        verbose_name="Factura de gastos",
                    ),
                ),
            ],
            options={
                "verbose_name": "Gasto",
                "verbose_name_plural": "Gastos",
            },
        ),
        migrations.CreateModel(
            name="ExpensesPayment",
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
                (
                    "asiento",
                    models.OneToOneField(
                        blank=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="expenses_payment",
                        to="accounting.asiento",
                        verbose_name="Asiento",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"is_paid": False},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="expenses_payments",
                        to="expenses.expensesinvoice",
                        verbose_name="A imputar en",
                    ),
                ),
                (
                    "method",
                    models.ForeignKey(
                        limit_choices_to={"is_active": True},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="expenses_payments",
                        to="configuration.paymentmethod",
                        verbose_name="Forma de pago",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recibo de pago",
                "verbose_name_plural": "Recibos de pago",
                "ordering": ["-pk"],
            },
        ),
        migrations.AddConstraint(
            model_name="supplier",
            constraint=models.UniqueConstraint(
                fields=("identification_type", "identification_number"),
                name="supplier_uniqueness",
            ),
        ),
        migrations.AddField(
            model_name="expensespayment",
            name="supplier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="expenses_payments",
                to="expenses.supplier",
                verbose_name="Proveedor",
            ),
        ),
        migrations.AddField(
            model_name="expensesinvoice",
            name="supplier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="invoices",
                to="expenses.supplier",
                verbose_name="Proveedor",
            ),
        ),
        migrations.AddField(
            model_name="suppliermovement",
            name="invoice",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="supplier_movement",
                to="expenses.expensesinvoice",
                verbose_name="Factura de gastos",
            ),
        ),
        migrations.AddField(
            model_name="suppliermovement",
            name="payment",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="supplier_movement",
                to="expenses.expensespayment",
                verbose_name="Recibo de pago",
            ),
        ),
        migrations.AddField(
            model_name="suppliermovement",
            name="supplier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="supplier_movements",
                to="expenses.supplier",
                verbose_name="Proveedor",
            ),
        ),
        migrations.AddField(
            model_name="tax",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses_taxes",
                to="expenses.expensesinvoice",
                verbose_name="Factura de gastos",
            ),
        ),
        migrations.AddField(
            model_name="tax",
            name="tax_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses_taxes",
                to="accounting.taxtype",
                verbose_name="Tipo de impuesto",
            ),
        ),
        migrations.AddConstraint(
            model_name="expensesinvoice",
            constraint=models.UniqueConstraint(
                fields=("letter", "sales_point", "number", "supplier"),
                name="expensesinvoice_uniqueness",
            ),
        ),
        migrations.AddConstraint(
            model_name="tax",
            constraint=models.UniqueConstraint(
                fields=("tax_type", "invoice"), name="expensesinvoice_tax_uniqueness"
            ),
        ),
    ]

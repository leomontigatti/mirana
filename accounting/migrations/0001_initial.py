import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import accounting.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Asiento",
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
            ],
            options={
                "verbose_name": "Asiento",
                "verbose_name_plural": "Asientos",
            },
        ),
        migrations.CreateModel(
            name="Cuenta",
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
                ("name", models.CharField(max_length=100, verbose_name="Nombre")),
                ("debe", models.FloatField(default=0, verbose_name="Debe")),
                ("haber", models.FloatField(default=0, verbose_name="Haber")),
            ],
            options={
                "verbose_name": "Cuenta",
                "verbose_name_plural": "Cuentas",
                "ordering": ["subrubro"],
            },
        ),
        migrations.CreateModel(
            name="Rubro",
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
                    "capitulo",
                    models.CharField(
                        choices=[
                            ("Activo", "Activo"),
                            ("Pasivo", "Pasivo"),
                            ("Patrimonio", "Patrimonio"),
                            ("Ingresos", "Ingresos"),
                            ("Egresos", "Egresos"),
                        ],
                        max_length=50,
                        verbose_name="Capítulo",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Nombre")),
            ],
            options={
                "verbose_name": "Rubro",
                "verbose_name_plural": "Rubros",
            },
        ),
        migrations.CreateModel(
            name="Entry",
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
                    "debe",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Debe",
                    ),
                ),
                (
                    "haber",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Haber",
                    ),
                ),
                (
                    "asiento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entries",
                        to="accounting.asiento",
                        verbose_name="Asiento",
                    ),
                ),
                (
                    "cuenta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="entries",
                        to="accounting.cuenta",
                        verbose_name="Cuenta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Entrada",
                "verbose_name_plural": "Entradas",
                "ordering": ["-debe"],
            },
        ),
        migrations.CreateModel(
            name="Subrubro",
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
                ("name", models.CharField(max_length=100, verbose_name="Nombre")),
                (
                    "rubro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="subrubros",
                        to="accounting.rubro",
                        verbose_name="Rubro",
                    ),
                ),
            ],
            options={
                "verbose_name": "Subrubro",
                "verbose_name_plural": "Subrubros",
            },
        ),
        migrations.AddField(
            model_name="cuenta",
            name="subrubro",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cuentas",
                to="accounting.subrubro",
                verbose_name="Subrubro",
            ),
        ),
        migrations.CreateModel(
            name="TaxType",
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
                    "name",
                    models.CharField(
                        max_length=100,
                        validators=[accounting.models.validate_tax_type_characters],
                        verbose_name="Nombre",
                    ),
                ),
                (
                    "percentage",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Asegúrese de que este valor sea mayor o igual a 0."
                            )
                        ],
                        verbose_name="Alícuota",
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
                    "cuenta_activo",
                    models.ForeignKey(
                        limit_choices_to={"subrubro_id": 3},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="taxtype_activo",
                        to="accounting.cuenta",
                        verbose_name="Cuenta activo",
                    ),
                ),
                (
                    "cuenta_pasivo",
                    models.ForeignKey(
                        limit_choices_to={"subrubro_id": 21},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="taxtype_pasivo",
                        to="accounting.cuenta",
                        verbose_name="Cuenta pasivo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo de impuesto",
                "verbose_name_plural": "Tipos de impuesto",
                "ordering": ["name"],
            },
        ),
        migrations.AddConstraint(
            model_name="cuenta",
            constraint=models.UniqueConstraint(
                fields=("subrubro", "name"), name="cuenta_uniqueness"
            ),
        ),
        migrations.AddConstraint(
            model_name="taxtype",
            constraint=models.UniqueConstraint(
                fields=("name", "percentage"), name="tax_type_uniqueness"
            ),
        ),
    ]

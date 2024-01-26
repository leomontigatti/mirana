import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounting", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Issuing",
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
                    "identification_number",
                    models.CharField(
                        help_text="11 números sin guiones.",
                        max_length=20,
                        unique=True,
                        verbose_name="Número de CUIT",
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
                        max_length=100,
                        verbose_name="Situación frente al IVA",
                    ),
                ),
                ("address", models.CharField(max_length=200, verbose_name="Domicilio")),
                (
                    "create_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de alta"
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
                "verbose_name": "Emisor",
                "verbose_name_plural": "Emisores",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Task",
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
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="Descripción",
                    ),
                ),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Normal"), (2, "Media"), (3, "Urgente")],
                        default=1,
                        verbose_name="Prioridad",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="Fecha de inicio")),
                (
                    "is_done",
                    models.BooleanField(default=False, verbose_name="Terminada"),
                ),
            ],
            options={
                "verbose_name": "Tarea",
                "verbose_name_plural": "Tareas",
                "ordering": ["start_date", "-priority"],
            },
        ),
        migrations.CreateModel(
            name="Collector",
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
                    models.CharField(max_length=20, unique=True, verbose_name="Nombre"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cobrador",
                "verbose_name_plural": "Cobradores",
            },
        ),
        migrations.CreateModel(
            name="Operator",
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
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Operario",
                "verbose_name_plural": "Operarios",
                "ordering": ["user"],
            },
        ),
        migrations.CreateModel(
            name="PaymentMethod",
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
                ("is_active", models.BooleanField(default=True, verbose_name="Activo")),
                (
                    "cuenta",
                    models.ForeignKey(
                        limit_choices_to={"subrubro__in": (1, 2, 4)},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_methods",
                        to="accounting.cuenta",
                        verbose_name="Cuenta contable",
                    ),
                ),
            ],
            options={
                "verbose_name": "Forma de cobro",
                "verbose_name_plural": "Formas de cobro",
                "ordering": ["name"],
            },
        ),
    ]

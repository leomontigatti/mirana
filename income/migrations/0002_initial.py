import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounting", "0001_initial"),
        ("income", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="service_type",
            field=models.ForeignKey(
                limit_choices_to={"is_active": True},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="services",
                to="inventory.servicetype",
                verbose_name="Tipo de servicio",
            ),
        ),
        migrations.AddField(
            model_name="tax",
            name="budget",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="income_taxes",
                to="income.budget",
                verbose_name="Presupuesto",
            ),
        ),
        migrations.AddField(
            model_name="tax",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="income_taxes",
                to="income.salesinvoice",
                verbose_name="Factura de venta",
            ),
        ),
        migrations.AddField(
            model_name="tax",
            name="tax_type",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="income_taxes",
                to="accounting.taxtype",
                verbose_name="Tipo de impuesto",
            ),
        ),
        migrations.AddConstraint(
            model_name="salesinvoice",
            constraint=models.UniqueConstraint(
                fields=("letter", "sales_point", "number", "customer"),
                name="salesinvoice_uniqueness",
            ),
        ),
        migrations.AddConstraint(
            model_name="tax",
            constraint=models.UniqueConstraint(
                fields=("tax_type", "invoice"), name="salesinvoice_tax_uniqueness"
            ),
        ),
    ]

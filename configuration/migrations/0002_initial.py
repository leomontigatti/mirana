import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("configuration", "0001_initial"),
        ("income", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="hiring",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(("status", "CHARGED"), _negated=True),
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tasks",
                to="income.hiring",
                verbose_name="Contratación",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="operator",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"user__is_active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tasks",
                to="configuration.operator",
                verbose_name="Operario",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tasks",
                to="income.service",
                verbose_name="Servicio",
            ),
        ),
    ]

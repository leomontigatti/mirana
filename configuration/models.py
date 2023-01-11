from django.contrib.auth.models import User
from django.db import models

from accounting.models import Cuenta
from income.models import Hiring
from main.models import IvaSituationChoices


class TaskFrequencyChoices(models.TextChoices):
    DAILY = "DAILY", "Diaria"
    WEEKLY = "WEEKLY", "Semanal"
    MONTHLY = "MONTHLY", "Mensual"
    UNIQUE = "UNIQUE", "Única"


class TaskPriorityChoices(models.IntegerChoices):
    NORMAL = 1, "Normal"
    MEDIUM = 2, "Media"
    URGENT = 3, "Urgente"


class Issuing(models.Model):
    """
    Store a single 'issuing' instance.
    """

    identification_number = models.CharField(
        verbose_name="Número de CUIT",
        max_length=20,
        help_text="11 números sin guiones.",
        unique=True,
    )
    name = models.CharField(
        verbose_name="Nombre o Razón Social",
        max_length=200,
    )
    iva_situation = models.CharField(
        verbose_name="Situación frente al IVA",
        max_length=100,
        choices=IvaSituationChoices.choices,
    )
    address = models.CharField(verbose_name="Domicilio", max_length=200)
    create_date = models.DateTimeField(verbose_name="Fecha de alta", auto_now_add=True)
    change_date = models.DateTimeField(
        verbose_name="Fecha de modificación", auto_now=True
    )

    class Meta:
        verbose_name = "Emisor"
        verbose_name_plural = "Emisores"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Operator(models.Model):
    """
    Store a single 'operator' instance, related to :model:`auth.User`
    """

    user = models.OneToOneField(User, verbose_name="Usuario", on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Operario"
        verbose_name_plural = "Operarios"
        ordering = ("user",)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Task(models.Model):
    """
    Store a single 'task' instance, related to :model:`configuration.Operator`
    """

    operator = models.ForeignKey(
        Operator,
        verbose_name="Operario",
        on_delete=models.PROTECT,
        related_name="tasks",
        blank=True,
        null=True,
    )
    description = models.CharField(verbose_name="Descripción", max_length=200)
    priority = models.IntegerField(
        verbose_name="Prioridad",
        choices=TaskPriorityChoices.choices,
        default=TaskPriorityChoices.NORMAL,
    )
    task_start_date = models.DateField(
        verbose_name="Fecha de inicio", blank=True, null=True
    )
    task_end_date = models.DateField(
        verbose_name="Fecha de finalización", blank=True, null=True
    )
    frequency = models.CharField(
        verbose_name="Frecuencia",
        max_length=50,
        choices=TaskFrequencyChoices.choices,
        default=TaskFrequencyChoices.MONTHLY,
    )
    is_done = models.BooleanField(verbose_name="Terminada", default=False)
    hiring = models.ForeignKey(
        Hiring,
        verbose_name="Contratación",
        on_delete=models.CASCADE,
        related_name="tasks",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ("task_start_date",)

    def __str__(self):
        return (
            f"{self.task_start_date.strftime('%d/%m/%Y')} - {self.description}"
            if self.task_start_date
            else self.description
        )


class PaymentMethod(models.Model):
    """
    Store a single 'payment method' instance, related to :model:`accounting.Cuenta`.
    """

    cuenta = models.OneToOneField(
        Cuenta,
        verbose_name="Cuenta contable",
        on_delete=models.PROTECT,
        limit_choices_to={"subrubro__in": (1, 2, 4)},
    )
    name = models.CharField(verbose_name="Nombre", max_length=100)
    is_active = models.BooleanField(verbose_name="Activo", default=True)

    class Meta:
        verbose_name = "Forma de pago"
        verbose_name_plural = "Formas de pago"

    def __str__(self):
        return self.name

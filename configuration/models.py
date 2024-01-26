from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from accounting.models import Cuenta
from inventory.models import StockMovement, StockStatusChoices
from main.models import IvaSituationChoices


class TaskPriorityChoices(models.IntegerChoices):
    NORMAL = 1, "Normal"
    MEDIUM = 2, "Media"
    URGENT = 3, "Urgente"


class Collector(models.Model):
    user = models.OneToOneField(User, models.PROTECT, verbose_name="Usuario")
    name = models.CharField("Nombre", max_length=20, unique=True)

    class Meta:
        verbose_name = "Cobrador"
        verbose_name_plural = "Cobradores"

    def __str__(self):
        return self.name


class Issuing(models.Model):
    identification_number = models.CharField(
        "Número de CUIT",
        max_length=20,
        help_text="11 números sin guiones.",
        unique=True,
    )
    name = models.CharField(
        "Nombre o Razón Social",
        max_length=200,
    )
    iva_situation = models.CharField(
        "Situación frente al IVA",
        max_length=100,
        choices=IvaSituationChoices.choices,
    )
    address = models.CharField("Domicilio", max_length=200)
    create_date = models.DateTimeField("Fecha de alta", auto_now_add=True)
    change_date = models.DateTimeField("Fecha de modificación", auto_now=True)

    class Meta:
        verbose_name = "Emisor"
        verbose_name_plural = "Emisores"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    cuenta = models.ForeignKey(
        Cuenta,
        models.PROTECT,
        related_name="payment_methods",
        verbose_name="Cuenta contable",
        limit_choices_to={"subrubro__in": (1, 2, 4)},
    )
    name = models.CharField("Nombre", max_length=100)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Forma de cobro"
        verbose_name_plural = "Formas de cobro"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("paymentmethod_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("paymentmethod_update", kwargs={"pk": self.pk})


class Operator(models.Model):
    user = models.OneToOneField(User, models.PROTECT, verbose_name="Usuario")

    class Meta:
        verbose_name = "Operario"
        verbose_name_plural = "Operarios"
        ordering = ["user"]

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        # Create and assign new collector when created.
        if self._state.adding:
            Collector.objects.create(
                user=self.user,
                name=f"Operario: {self.user.first_name} {self.user.last_name}",
            )
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("operator_detail", kwargs={"pk": self.pk})


class Task(models.Model):
    operator = models.ForeignKey(
        Operator,
        models.SET_NULL,
        related_name="tasks",
        limit_choices_to={"user__is_active": True},
        verbose_name="Operario",
        blank=True,
        null=True,
    )
    description = models.CharField(
        "Descripción",
        max_length=200,
        blank=True,
        null=True,
    )
    service = models.ForeignKey(
        "income.Service",
        models.CASCADE,
        related_name="tasks",
        verbose_name="Servicio",
        blank=True,
        null=True,
    )
    priority = models.PositiveSmallIntegerField(
        "Prioridad",
        choices=TaskPriorityChoices.choices,
        default=TaskPriorityChoices.NORMAL,
    )
    start_date = models.DateField("Fecha de inicio")
    is_done = models.BooleanField("Terminada", default=False)
    hiring = models.ForeignKey(
        "income.Hiring",
        models.CASCADE,
        related_name="tasks",
        limit_choices_to=~models.Q(status="CHARGED"),
        verbose_name="Contratación",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ["start_date", "-priority"]

    def __str__(self):
        if self.description:
            return self.description.title()
        else:
            return self.service.service_type.description.title()

    def get_absolute_url(self):
        return reverse("task_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse("task_update", kwargs={"pk": self.pk})

    def update_hiring_status(self):
        hiring = self.hiring
        has_bathroom, has_workshop = False, False
        bathroom_placed, workshop_placed = False, False

        if all(
            [
                self.service,
                self.service.service_type,
                self.service.service_type.pk in [3, 4],
            ]
        ):
            hiring.status = "ONGOING"
        else:
            for task in hiring.tasks.all():
                if all(
                    [
                        task.service,
                        task.service.service_type,
                        task.service.service_type.pk == 1,
                    ]
                ):
                    has_bathroom = True
                    bathroom_placed = True if task.is_done else False
                elif all(
                    [
                        task.service,
                        task.service.service_type,
                        task.service.service_type.pk == 2,
                    ]
                ):
                    has_workshop = True
                    workshop_placed = True if task.is_done else False

            if bathroom_placed and has_workshop and not workshop_placed:
                hiring.status = "PENDING_WORKSHOP"
            elif workshop_placed and has_bathroom and not bathroom_placed:
                hiring.status = "PENDING_BATHROOM"
            else:
                hiring.status = "ONGOING"
        hiring.save()

    def update_or_create_stock_movement(self):
        service = self.service
        service_type = service.service_type

        if service_type.pk in [1, 2]:
            if service_type.bathrooms.exists():
                stock = "BATHROOM"
                object_list = service_type.bathrooms.filter(
                    status=StockStatusChoices.PROMISED
                )
            elif service_type.workshops.exists():
                stock = "WORKSHOP"
                object_list = service_type.workshops.filter(
                    status=StockStatusChoices.PROMISED
                )

            ids_qs = object_list.values("pk")[: service.amount]
            updated = object_list.filter(pk__in=ids_qs).update(
                status=StockStatusChoices.PLACED
            )

            StockMovement.objects.update_or_create(
                task=self,
                stock=stock,
                status=StockStatusChoices.PROMISED,
                defaults={
                    "amount": -updated,
                },
            )
            StockMovement.objects.update_or_create(
                task=self,
                stock=stock,
                status=StockStatusChoices.PLACED,
                defaults={
                    "amount": updated,
                },
            )

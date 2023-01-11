from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter
def to_spanish(obj):
    LABELS = {
        "login": "acceder",
        "home": "inicio",
        "list": "lista",
        "create": "crear",
        "detail": "detalle",
        "update": "modificar",
        "accounting": "contabilidad",
        "tax_type": "impuesto",
        "cuenta": "cuenta",
        "income": "ingresos",
        "customer": "cliente",
        "iva_situation": "situación frente IVA",
        "identification_type": "tipo de identificación",
        "budget": "presupuesto",
        "hiring": "contratación",
        "invoice": "factura",
        "income_payment": "recibo de cobro",
        "inventory": "inventario",
        "warehouse": "depósito",
        "stock": "stock",
        "is_active": "estado",
        "configuration": "configuración",
        "operator": "operario",
        "task": "tarea",
        "operator_task": "tarea",
        "configuration": "configuración",
        "payment_method": "forma de pago",
        "asiento": "asiento manual",
        "service_type": "servicio",
    }
    return LABELS.get(obj)


@register.filter
def to_spanish_plural(obj):
    LABELS = {
        "tax_type": "impuestos",
        "cuenta": "cuentas contables",
        "customer": "clientes",
        "budget": "presupuestos",
        "hiring": "contrataciones",
        "invoice": "facturas",
        "income_payment": "recibos de cobro",
        "category": "categorías",
        "warehouse": "depósitos",
        "stock": "stock",
        "task": "tareas",
        "operator": "operarios",
        "payment_method": "formas de pago",
        "service_type": "servicios",
        "asiento": "libro diario",
    }
    return LABELS.get(obj)


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural


@register.filter
def get_class(obj):
    return obj.__class__.__name__


@register.filter
def is_operator(obj):
    try:
        obj.operator
        return True
    except ObjectDoesNotExist:
        return False

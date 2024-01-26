from django import template

register = template.Library()


@register.filter
def to_spanish(obj):
    LABELS = {
        "login": "acceso",
        "home": "inicio",
        "list": "lista",
        "create": "crear",
        "detail": "detalle",
        "update": "modificar",
        "accounting": "contabilidad",
        "asiento": "asiento manual",
        "cuenta": "cuenta",
        "taxtype": "impuesto",
        "configuration": "configuración",
        "operator": "operario",
        "task": "tarea",
        "priority": "prioridad",
        "is_done": "estado",
        "paymentmethod": "forma de pago",
        "expenses": "egresos",
        "supplier": "proveedor",
        "expensesinvoice": "factura de gastos",
        "expensespayment": "orden de pago",
        "invoice__isnull": "estado",
        "method": "forma de pago",
        "collector": "cobrador",
        "income": "ingresos",
        "customer": "cliente",
        "iva_situation": "situación frente IVA",
        "identification_type": "tipo de identificación",
        "budget": "presupuesto",
        "hiring": "contratación",
        "salesinvoice": "factura de venta",
        "incomepayment": "recibo de cobro",
        "inventory": "inventario",
        "servicetype": "tipo de servicio",
        "stock": "stock",
        "bathroom": "baño",
        "workshop": "obrador",
        "AVAILABLE": "disponible",
        "PROMISED": "prometido",
        "PLACED": "colocado",
        "MAINTENANCE": "en mantenimiento",
        "is_active": "estado",
        "is_clean": "limpieza",
        "status": "estado",
        "is_paid": "estado",
        "sale_condition": "condición de compra",
        "date": "fecha",
    }
    return LABELS[obj]


@register.filter
def to_spanish_plural(obj):
    LABELS = {
        "asiento": "Libro diario",
        "cuenta": "Cuentas contables",
        "taxtype": "Tipos de impuesto",
        "operator": "Operarios",
        "paymentmethod": "Formas de pago",
        "task": "Tareas",
        "supplier": "Proveedores",
        "expensesinvoice": "Facturas de gastos",
        "expensespayment": "Órdenes de pago",
        "customer": "Clientes",
        "budget": "Presupuestos",
        "hiring": "Contrataciones",
        "salesinvoice": "Facturas de venta",
        "incomepayment": "Recibos de cobro",
        "servicetype": "Tipos de servicio",
        "stock": "Stock",
    }
    return LABELS[obj]


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural


@register.filter
def get_class(obj):
    return obj.__class__.__name__.lower()


@register.filter
def can_delete(obj):
    models_list = [
        "tax_type",
        "task",
        "payment_method",
        "budget",
        "hiring",
        "servicetype",
    ]
    return obj in models_list


@register.filter
def can_update(obj):
    models_list = [
        "tax_type",
        "task",
        "payment_method",
        "supplier",
        "customer",
        "budget",
        "hiring",
        "salesinvoice",
        "incomepayment",
        "expensesinvoice",
        "expensespayment",
        "stock",
        "servicetype",
    ]
    return obj in models_list


@register.filter
def is_operator(user):
    return hasattr(user, "operator")

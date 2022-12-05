from django import template

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
        "taxtype": "tipo de impuesto",
        "cuenta": "cuenta",
        "income": "ingresos",
        "customer": "cliente",
        "situacion_iva": "situación frente IVA",
        "identification_type": "tipo de identificación",
        "budget": "presupuesto",
        "hiring": "contratación",
        "invoice": "factura",
        "inventory": "inventario",
        "category": "categoría",
        "producttype__category": "categoría",
        "producttype": "producto",
        "warehouse": "depósito",
        "stock": "stock",
    }
    return LABELS.get(obj)


@register.filter
def to_spanish_plural(obj):
    LABELS = {
        "taxtype": "tipos de impuesto",
        "cuenta": "cuentas contables",
        "customer": "clientes",
        "budget": "presupuestos",
        "hiring": "contrataciones",
        "invoice": "facturas",
        "category": "categorías",
        "producttype__category": "categorías",
        "producttype": "productos",
        "warehouse": "depósitos",
        "stock": "stocks",
    }
    return LABELS.get(obj)


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural


@register.filter
def get_class(obj):
    return obj.__class__.__name__

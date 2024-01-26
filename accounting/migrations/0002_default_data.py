from django.db import migrations


def create_default_data(apps, schema_editor):
    DATA = {
        "Activo": {
            "Activo corriente": {
                "Cajas": ["CAJA CHICA"],
                "Bancos": [],
                "Créditos impositivos": ["IVA CRÉDITO FISCAL"],
                "Anticipos a proveedores": ["GENERAL"],
                "Devoluciones a proveedores": ["GENERAL"],
                "Anticipos al personal": [],
                "Créditos por ventas": ["GENERAL"],
                "Bienes de cambio": ["MERCADERÍAS"],
            },
            "Activo no corriente": {
                "Bienes de uso": [],
            },
        },
        "Pasivo": {
            "Pasivo corriente": {
                "Proveedores": ["GENERAL"],
                "Anticipos de clientes": ["GENERAL"],
                "Devoluciones de clientes": ["GENERAL"],
                "Impuestos por pagar": ["IVA DÉBITO FISCAL"],
            },
            "Pasivo no corriente": {
                "Deudas financieras": ["OTRAS DEUDAS"],
            },
        },
        "Ingresos": {
            "Ingresos ordinarios": {
                "Ventas": ["VENTAS"],
            },
            "Ingresos extraordinarios": {
                "Resultados financieros y por tenencia": ["INTERESES GANADOS"],
            },
        },
        "Egresos": {
            "Costo de ventas": {
                "Costo de los servicios vendidos": ["COSTO DE LOS SERVICIOS VENDIDOS"]
            },
            "Gastos ordinarios": {
                "Gastos de administración": [
                    "GASTOS EN REMUNERACIONES Y CARGAS SOCIALES",
                    "ALQUILERES PAGADOS",
                    "SERVICIOS PAGADOS",
                    "PAPELERÍA Y ÚTILES",
                    "SEGUROS",
                    "GASTOS DE MANTENIMIENTO Y REPARACIONES",
                    "GASTOS VARIOS",
                ],
            },
            "Depreciaciones": {
                "Depreciación de bienes de uso": [],
            },
            "Gastos financieros": {
                "Intereses y gastos bancarios": [],
                "Diferencia de cambio": [],
            },
            "Impuestos": {
                "Impuesto a las ganancias": ["IMPUESTO A LAS GANANCIAS"],
                "Impuesto a los Ingresos Brutos": ["IMPUESTO A LOS INGRESOS BRUTOS"],
                "Impuesto a Industria y Comercio": ["IMPUESTO A INDUSTRIA Y COMERCIO"],
            },
        },
    }

    Rubro = apps.get_model("accounting", "Rubro")
    Subrubro = apps.get_model("accounting", "Subrubro")
    Cuenta = apps.get_model("accounting", "Cuenta")
    rubros_list, subrubros_list, cuentas_list = [], [], []

    for capitulo, rubros in DATA.items():
        for rubro, subrubros in rubros.items():
            rubro_instance = Rubro(capitulo=capitulo, name=rubro)
            rubros_list.append(rubro_instance)
            rubro_index = rubros_list.index(rubro_instance) + 1
            for subrubro, cuentas in subrubros.items():
                subrubro_instance = Subrubro(rubro_id=rubro_index, name=subrubro)
                subrubros_list.append(subrubro_instance)
                subrubro_index = subrubros_list.index(subrubro_instance) + 1
                if cuentas:
                    for cuenta in cuentas:
                        cuentas_list.append(
                            Cuenta(subrubro_id=subrubro_index, name=cuenta)
                        )

    Rubro.objects.bulk_create(rubros_list)
    Subrubro.objects.bulk_create(subrubros_list)
    Cuenta.objects.bulk_create(cuentas_list)


class Migration(migrations.Migration):
    dependencies = [
        ("accounting", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_default_data)]

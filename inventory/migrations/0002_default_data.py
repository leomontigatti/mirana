from django.db import migrations


def create_default_data(apps, schema_editor):
    SERVICE_TYPE = [
        "Alquiler de baño",
        "Alquiler de obrador",
        "Limpieza cada 2 días",
        "Limpieza cada 3 días",
    ]

    ServiceType = apps.get_model("inventory", "ServiceType")

    service_type_list = [
        ServiceType(description=description, can_be_updated=False)
        for description in SERVICE_TYPE
    ]

    ServiceType.objects.bulk_create(service_type_list)


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_default_data)]

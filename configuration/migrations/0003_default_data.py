# from decouple import config
# from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_data(apps, schema_editor):
    # User = apps.get_model("auth", "User")
    # Collector = apps.get_model("configuration", "Collector")
    # superuser_password = config("SUPERUSER_PASSWORD")
    # user_password = config("USER_PASSWORD")

    # superuser = User(
    #     username="superuser",
    #     password=make_password(superuser_password),
    #     is_staff=True,
    #     is_superuser=True,
    # )

    # estefania = User(
    #     username="estefania",
    #     password=make_password(user_password),
    #     is_staff=False,
    #     is_superuser=False,
    # )
    # estefania_collector = Collector(user_id=2, name="Estefanía")

    # mariano = User(
    #     username="mariano",
    #     password=make_password(user_password),
    #     is_staff=False,
    #     is_superuser=False,
    # )
    # mariano_collector = Collector(user_id=3, name="Mariano")

    # User.objects.bulk_create([superuser, estefania, mariano])
    # Collector.objects.bulk_create([estefania_collector, mariano_collector])

    PaymentMethod = apps.get_model("configuration", "PaymentMethod")
    PaymentMethod.objects.create(cuenta_id=1, name="Efectivo")


class Migration(migrations.Migration):
    dependencies = [
        ("configuration", "0002_initial"),
    ]

    operations = [migrations.RunPython(create_default_data)]

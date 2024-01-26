import csv

from django.core.management.base import BaseCommand, CommandError

from accounting.models import Cuenta, Rubro, Subrubro


class Command(BaseCommand):
    """
    Base command used for importing rubros, subrubros and cuentas in a CSV file.
    This file must contain the columns:
    'capitulo', 'rubro', 'subrubro' and 'cuenta'
    """

    help = (
        "Imports a .csv file with 'cuentas contables' and inserts them into database."
    )

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="CSV File name (Ex.: cuentas.csv).")

    def handle(self, *args, **options):
        filename = options["file"]
        if not filename:
            raise CommandError("No file was specified.")
        cuentas = []
        try:
            with open(filename, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file, delimiter=",")
                try:
                    for row in reader:
                        rubro, created_rubro = Rubro.objects.get_or_create(
                            capitulo=row["capitulo"], name=row["rubro"]
                        )
                        subrubro, created_subrubro = Subrubro.objects.get_or_create(
                            rubro=rubro, name=row["subrubro"]
                        )
                        if row["cuenta"]:
                            cuentas.append(
                                Cuenta(subrubro=subrubro, name=row["cuenta"])
                            )
                except KeyError:
                    # File structure is incorrect, its first column must be "capitulo".
                    self.stdout.write(
                        self.style.ERROR(
                            "File has incorrect format. It's missing a 'capitulo' column."
                        )
                    )
                    return
        except FileNotFoundError:
            # File path is incorrect.
            self.stdout.write(
                self.style.ERROR(
                    "File path is incorrect. Please check .csv file destination."
                )
            )
            return
        created = Cuenta.objects.bulk_create(cuentas, ignore_conflicts=True)
        count = len(created)
        if not count:
            self.stdout.write(
                self.style.WARNING("File was imported but no 'cuenta' was registered.")
            )
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported cuentas file and registered {count} cuenta{'s' if count != 1 else ''}."
            )
        )

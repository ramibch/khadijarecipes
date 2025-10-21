from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reset AUTOINCREMENT sequences in sqlite_sequence for all tables starting with 'recipes_'."

    def handle(self, *args, **options):
        if connection.vendor != "sqlite":
            self.stderr.write(
                self.style.ERROR("This command only works with SQLite databases.")
            )
            return

        with connection.cursor() as cursor:
            # Check if sqlite_sequence exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';"
            )
            if not cursor.fetchone():
                self.stdout.write(
                    self.style.WARNING(
                        "No sqlite_sequence table found (no AUTOINCREMENT fields in DB)."
                    )
                )
                return

            # Get all tables in sqlite_sequence starting with 'recipes_'
            cursor.execute(
                "SELECT name, seq FROM sqlite_sequence WHERE name LIKE 'recipes_%';"
            )
            tables = cursor.fetchall()

            if not tables:
                self.stdout.write(
                    self.style.WARNING("No 'recipes_' tables found in sqlite_sequence.")
                )
                return

            for name, seq in tables:
                cursor.execute(
                    "UPDATE sqlite_sequence SET seq = 0 WHERE name = %s;", [name]
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Reset sequence for table '{name}' (was {seq})")
                )

        self.stdout.write(
            self.style.SUCCESS("All 'recipes_' sequences have been reset.")
        )

import json
import os

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Load fixtures handling unique constraints and timestamp issues"

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture_files", nargs="+", type=str, help="Fixture files to load"
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing records instead of skipping them",
        )

    def handle(self, *args, **options):
        fixture_files = options["fixture_files"]
        update_existing = options["update"]

        for fixture_file in fixture_files:
            self.stdout.write(f"Processing fixture: {fixture_file}")

            if not os.path.exists(fixture_file):
                self.stderr.write(f"Fixture file not found: {fixture_file}")
                continue

            # Try normal loading first
            try:
                self.stdout.write("Attempting normal load...")
                call_command("loaddata", fixture_file, verbosity=1)
                self.stdout.write(self.style.SUCCESS("Normal load successful"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Normal load failed: {e}"))
                self.load_fixture_smart(fixture_file, update_existing)

    def load_fixture_smart(self, fixture_file, update_existing):
        """Load fixture with smart handling of unique constraints"""
        try:
            with open(fixture_file, "r", encoding="utf-8") as f:
                fixture_data = json.load(f)
        except Exception as e:
            self.stderr.write(f"Error reading fixture: {e}")
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        with transaction.atomic():
            for entry in fixture_data:
                try:
                    model = apps.get_model(entry["model"])
                    fields = entry["fields"]
                    desired_pk = entry.get("pk")

                    # Remove auto-generated fields
                    fields.pop("created_at", None)
                    fields.pop("updated_at", None)

                    # Check for existing record by primary key
                    existing_obj = None
                    if desired_pk:
                        existing_obj = model.objects.filter(pk=desired_pk).first()

                    # If no existing by PK, check by unique fields
                    if not existing_obj:
                        existing_obj = self.find_existing_by_unique_fields(
                            model, fields
                        )

                    if existing_obj:
                        if update_existing:
                            # Update existing record
                            for field, value in fields.items():
                                setattr(existing_obj, field, value)
                            existing_obj.save()
                            updated_count += 1
                            self.stdout.write(
                                f"↻ Updated {entry['model']} PK:{existing_obj.pk}"
                            )
                        else:
                            # Skip existing record
                            skipped_count += 1
                            self.stdout.write(
                                f"⤳ Skipped {entry['model']} PK:{existing_obj.pk} (exists)"
                            )
                    else:
                        # Create new record
                        obj = model(**fields)
                        if desired_pk:
                            obj.pk = desired_pk
                        obj.save()
                        created_count += 1
                        self.stdout.write(f"✓ Created {entry['model']} PK:{obj.pk}")

                except Exception as e:
                    error_count += 1
                    self.stderr.write(f"✗ Error {entry['model']}: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed: {created_count} created, {updated_count} updated, "
                f"{skipped_count} skipped, {error_count} errors"
            )
        )

    def find_existing_by_unique_fields(self, model, fields):
        """Find existing record by checking unique fields"""
        try:
            # For Unit model, check by name_de (which has unique constraint)
            if model._meta.label == "recipes.Unit":
                if "name_de" in fields:
                    return model.objects.filter(name_de=fields["name_de"]).first()

            # For Ingredient model, check by name_de
            elif model._meta.label == "recipes.Ingredient":
                if "name_de" in fields:
                    return model.objects.filter(name_de=fields["name_de"]).first()

            # For other models, you might need different logic
            # For now, return None to create new record
            return None

        except Exception:
            return None

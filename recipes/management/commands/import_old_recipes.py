import json
import re

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeStep, Unit


class Command(BaseCommand):
    help = "Import recipes from old JSON format to new structured models"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to the JSON file")
        parser.add_argument(
            "--dry-run", action="store_true", help="Dry run without saving"
        )

    def handle(self, *args, **options):
        json_file_path = options["json_file"]
        dry_run = options["dry_run"]

        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create common units
        units = self.create_units(dry_run)

        imported_count = 0
        skipped_count = 0

        for item in data:
            if item["model"] == "blog.blogpage":
                try:
                    if dry_run:
                        self.stdout.write(
                            f"Would import: {self.get_recipe_title(item)}"
                        )
                    else:
                        recipe = self.import_recipe(item, units)
                        if recipe:
                            imported_count += 1
                            self.stdout.write(f"✓ Imported: {recipe.title_de}")
                        else:
                            skipped_count += 1
                except Exception as e:
                    self.stderr.write(f"✗ Error importing: {str(e)}")
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {imported_count} recipes imported, {skipped_count} skipped"
            )
        )

    def get_recipe_title(self, item):
        """Extract recipe title from the item"""
        fields = item["fields"]

        # Try to get from subtitle first
        subtitle = fields.get("subtitle", "")
        if subtitle:
            return subtitle

        # Try to find a title in the body
        body = fields.get("body", "[]")
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
                for block in body_data:
                    if block["type"] == "paragraph_block":
                        value = block.get("value", "")
                        # Look for h2 tags
                        if "<h2" in value:
                            match = re.search(r"<h2[^>]*>(.*?)</h2>", value)
                            if match:
                                title = match.group(1).strip()
                                if title and title.lower() not in [
                                    "zutaten",
                                    "ingredients",
                                    "ingrédients",
                                    "zubereitung",
                                    "preparation",
                                    "préparation",
                                ]:
                                    return title
            except Exception as e:
                print(e)

        # Fallback
        return f"Recipe {item['pk']}"

    def create_units(self, dry_run=False):
        """Create common measurement units"""
        units_data = [
            ("gram", "g"),
            ("kilogram", "kg"),
            ("milliliter", "ml"),
            ("liter", "l"),
            ("teaspoon", "tsp"),
            ("tablespoon", "tbsp"),
            ("cup", "cup"),
            ("piece", "pc"),
            ("pinch", "pinch"),
            ("bunch", "bunch"),
            ("clove", "clove"),
        ]

        units = {}
        if not dry_run:
            for name, abbrev in units_data:
                unit, created = Unit.objects.get_or_create(
                    name_de=name, defaults={"abbreviation": abbrev}
                )
                units[name] = unit
        return units

    def parse_ingredients_from_html(self, html_content):
        """Extract ingredients from HTML content"""
        ingredients = []

        # Look for unordered lists
        ul_pattern = r"<ul>(.*?)</ul>"
        ul_matches = re.findall(ul_pattern, html_content, re.DOTALL | re.IGNORECASE)

        for ul_content in ul_matches:
            # Extract list items
            li_pattern = r"<li[^>]*>(.*?)</li>"
            li_matches = re.findall(li_pattern, ul_content, re.DOTALL | re.IGNORECASE)

            for li_content in li_matches:
                # Clean up HTML tags
                clean_text = re.sub(r"<[^>]+>", "", li_content).strip()
                # Remove affiliate links
                if (
                    clean_text
                    and "amzn.to" not in clean_text
                    and "http" not in clean_text
                ):
                    ingredients.append(clean_text)

        return ingredients

    def parse_ingredient_line(self, line):
        """Parse an ingredient line into quantity, unit, and name"""
        # Remove affiliate links
        line = re.sub(r"https?://[^\s]+", "", line)

        # Common patterns for ingredient parsing
        patterns = [
            r"(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|tsp|tbsp|cup|cups|piece|pieces|pinch|bunch)?\s*(.+)",
            r"(\d+)\s*(.+)",
        ]

        for pattern in patterns:
            match = re.match(pattern, line.strip(), re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    quantity, unit, name = match.groups()
                    return quantity.strip(), unit.strip() if unit else "", name.strip()
                elif len(match.groups()) == 2:
                    quantity, name = match.groups()
                    return quantity.strip(), "", name.strip()

        return None, None, line.strip()

    def extract_steps_from_html(self, html_content):
        """Extract preparation steps from HTML content"""
        steps = []

        # Look for paragraphs after preparation headings
        prep_pattern = r"<h2[^>]*>.*?(?:Preparation|Zubereitung|Préparation).*?</h2>(.*?)(?=<h2|$|</body>)"
        prep_match = re.search(prep_pattern, html_content, re.DOTALL | re.IGNORECASE)

        if prep_match:
            prep_content = prep_match.group(1)
            # Extract paragraphs as steps
            p_pattern = r"<p[^>]*>(.*?)</p>"
            p_matches = re.findall(p_pattern, prep_content, re.DOTALL | re.IGNORECASE)

            for p_content in p_matches:
                clean_text = re.sub(r"<[^>]+>", " ", p_content).strip()
                clean_text = re.sub(r"\s+", " ", clean_text)
                if clean_text and len(clean_text) > 10:
                    steps.append(clean_text)

        return steps

    def import_recipe(self, item, units):
        """Import a single recipe from the old format"""
        fields = item["fields"]

        # Extract title
        title = self.get_recipe_title(item)
        if not title or title.lower() in ["zutaten", "ingredients", "ingrédients"]:
            return None

        # Create recipe
        recipe = Recipe(
            title_de=title,
            introduction_de=fields.get("introduction", ""),
            date_published=fields.get("date_published"),
            is_published=bool(fields.get("date_published")),
        )

        # Generate slug
        recipe.slug_de = slugify(recipe.title_de)

        # Handle duplicate slugs
        counter = 1
        original_slug = recipe.slug_de
        while Recipe.objects.filter(slug_de=recipe.slug_de).exists():
            recipe.slug_de = f"{original_slug}-{counter}"
            counter += 1

        recipe.save()

        # Import ingredients and steps from body
        body = fields.get("body", "[]")
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
                self.import_from_body(recipe, body_data, units)
            except json.JSONDecodeError:
                pass

        return recipe

    def import_from_body(self, recipe, body_data, units):
        """Import ingredients and steps from body data"""
        ingredients_imported = 0
        steps_imported = 0

        for block in body_data:
            if block["type"] == "paragraph_block":
                value = block.get("value", "")

                # Import ingredients
                ingredients = self.parse_ingredients_from_html(value)
                for i, ingredient_line in enumerate(ingredients):
                    if self.import_ingredient(recipe, ingredient_line, i, units):
                        ingredients_imported += 1

                # Import steps
                steps = self.extract_steps_from_html(value)
                for step_number, step_text in enumerate(steps, 1):
                    if self.import_step(recipe, step_text, step_number):
                        steps_imported += 1

        if ingredients_imported > 0 or steps_imported > 0:
            self.stdout.write(
                f"  → {ingredients_imported} ingredients, {steps_imported} steps"
            )

    def import_ingredient(self, recipe, ingredient_line, order, units):
        """Import a single ingredient"""
        quantity, unit_text, name = self.parse_ingredient_line(ingredient_line)

        if not name or len(name) < 2:
            return False

        # Get or create ingredient
        ingredient, created = Ingredient.objects.get_or_create(name_de=name.title())

        # Create recipe ingredient
        recipe_ingredient = RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient,
            order=order,
        )

        if quantity:
            try:
                # Handle decimal separators
                quantity = quantity.replace(",", ".")
                recipe_ingredient.quantity = float(quantity)
            except (ValueError, TypeError):
                pass

        if unit_text:
            # Try to match with existing units
            unit_text_lower = unit_text.lower()
            for unit_name, unit_obj in units.items():
                if (
                    unit_name in unit_text_lower
                    or unit_obj.abbreviation in unit_text_lower
                ):
                    recipe_ingredient.unit = unit_obj
                    break
            else:
                recipe_ingredient.unit_text = unit_text

        recipe_ingredient.save()
        return True

    def import_step(self, recipe, step_text, step_number):
        """Import a single step"""
        if not step_text or len(step_text) < 5:
            return False

        # Check if this step number already exists
        if RecipeStep.objects.filter(recipe=recipe, step_number=step_number).exists():
            # Find next available step number
            existing_numbers = set(
                RecipeStep.objects.filter(recipe=recipe).values_list(
                    "step_number", flat=True
                )
            )
            step_number = max(existing_numbers) + 1 if existing_numbers else step_number

        RecipeStep.objects.create(
            recipe=recipe, step_number=step_number, instruction_de=step_text
        )
        return True

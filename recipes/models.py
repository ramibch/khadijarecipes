import json

from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Transpose

from config.db import CustomModel, PageModel


class Unit(CustomModel):
    """Model for measurement units"""

    abbreviation = models.CharField(max_length=10, blank=True)
    name_de = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)
    name_fr = models.CharField(max_length=50, null=True, blank=True)
    name_es = models.CharField(max_length=50, null=True, blank=True)
    name_it = models.CharField(max_length=50, null=True, blank=True)
    name_plural_de = models.CharField(max_length=100)
    name_plural_en = models.CharField(max_length=100, null=True, blank=True)
    name_plural_fr = models.CharField(max_length=100, null=True, blank=True)
    name_plural_es = models.CharField(max_length=100, null=True, blank=True)
    name_plural_it = models.CharField(max_length=100, null=True, blank=True)

    @property
    def name(self):
        return self.get_localized_value("name") or self.name_de

    @property
    def name_plural(self):
        return self.get_localized_value("name_plural") or self.name_plural_de

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name_de"]
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")


class Ingredient(CustomModel):
    """Model for ingredients that can be reused across recipes"""

    name_de = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    name_fr = models.CharField(max_length=100, null=True, blank=True)
    name_es = models.CharField(max_length=100, null=True, blank=True)
    name_it = models.CharField(max_length=100, null=True, blank=True)
    name_plural_de = models.CharField(max_length=100)
    name_plural_en = models.CharField(max_length=100, null=True, blank=True)
    name_plural_fr = models.CharField(max_length=100, null=True, blank=True)
    name_plural_es = models.CharField(max_length=100, null=True, blank=True)
    name_plural_it = models.CharField(max_length=100, null=True, blank=True)

    @property
    def name(self):
        return self.get_localized_value("name") or self.name_de

    @property
    def name_plural(self):
        return self.get_localized_value("name_plural") or self.name_plural_de

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name_de"]
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")


class RecipeDifficulty(models.TextChoices):
    EASY = "easy", _("Easy")
    MEDIUM = "medium", _("Medium")
    HARD = "hard", _("Hard")


class RecipeCategory(models.TextChoices):
    APPETIZER = "appetizer", _("Appetizer")
    MAIN = "main", _("Main Course")
    DESEART = "dessert", _("Dessert")
    SNACK = "snack", _("Snack")
    BEVERAGE = "beverage", _("Beverage")
    BREAD = "bread", _("Bread")


class Recipe(PageModel):
    """Main recipe model"""

    introduction_de = models.TextField()
    introduction_en = models.TextField(null=True, blank=True)
    introduction_fr = models.TextField(null=True, blank=True)
    introduction_es = models.TextField(null=True, blank=True)
    introduction_it = models.TextField(null=True, blank=True)

    # Metadata
    difficulty = models.CharField(
        max_length=10,
        choices=RecipeDifficulty,
        default=RecipeDifficulty.MEDIUM,
        verbose_name=_("Difficulty Level"),
    )
    category = models.CharField(
        max_length=20,
        choices=RecipeCategory,
        default=RecipeCategory.MAIN,
        verbose_name=_("Category"),
    )

    # Timing
    prep_time = models.PositiveIntegerField(
        help_text=_("Preparation time in minutes"),
        null=True,
        blank=True,
        verbose_name=_("Preparation Time"),
    )
    cook_time = models.PositiveIntegerField(
        help_text=_("Cooking time in minutes"),
        null=True,
        blank=True,
        verbose_name=_("Cooking Time"),
    )

    # Images
    main_image = models.ImageField(
        upload_to="recipes/main/",
        null=True,
        blank=True,
        verbose_name=_("Main Image"),
    )
    main_image_500x500 = ImageSpecField(
        source="main_image",
        processors=[Transpose(), ResizeToFill(500, 500)],
        format="WEBP",
        options={"quality": 90},
    )
    main_image_300x300 = ImageSpecField(
        source="main_image",
        processors=[Transpose(), ResizeToFill(300, 300)],
        format="WEBP",
        options={"quality": 90},
    )

    ingredients_image = models.ImageField(
        upload_to="recipes/ingredients/",
        null=True,
        blank=True,
        verbose_name=_("Ingredients Image"),
    )
    ingredients_image_500x500 = ImageSpecField(
        source="ingredients_image",
        processors=[Transpose(), ResizeToFill(500, 500)],
        format="WEBP",
        options={"quality": 90},
    )
    prep_image = models.ImageField(
        upload_to="recipes/preparation/",
        null=True,
        blank=True,
        verbose_name=_("Preparation Image"),
    )
    prep_image_500x500 = ImageSpecField(
        source="prep_image",
        processors=[Transpose(), ResizeToFill(500, 500)],
        format="WEBP",
        options={"quality": 90},
    )

    @property
    def introduction(self):
        return self.get_localized_value("introduction") or self.introduction_de

    @property
    def total_time(self):
        """Calculate total time including preparation and cooking"""
        total = 0
        if self.prep_time:
            total += self.prep_time
        if self.cook_time:
            total += self.cook_time
        return total if total > 0 else None

    def get_absolute_url(self):
        return reverse_lazy("recipe_detail", args=(self.slug,))

    def __str__(self):
        return self.title

    @property
    def json_schema(self):
        """Return structured data for Recipe (JSON-LD)."""
        ingredients_list = [str(ri) for ri in self.ingredients.all()]

        steps_list = [
            {
                "@type": "HowToStep",
                "position": step.step_number,
                "text": str(step.instruction),
            }
            for step in self.steps.all()
        ]

        schema = {
            "@context": "https://schema.org/",
            "@type": "Recipe",
            "name": str(self.title),
            "description": str(self.introduction)[:300] if self.introduction else "",
            "recipeCategory": str(self.get_category_display()),
            "recipeCuisine": str(self.get_category_display()),
            "prepTime": f"PT{self.prep_time}M" if self.prep_time else None,
            "cookTime": f"PT{self.cook_time}M" if self.cook_time else None,
            "totalTime": f"PT{self.total_time}M" if self.total_time else None,
            "recipeYield": "1 serving",
            "recipeIngredient": ingredients_list,
            "recipeInstructions": steps_list,
            "author": {
                "@type": "Person",
                "name": "Chef",  # or use dynamic brand_name if available
            },
            "keywords": f"{self.get_category_display()}, recipe, food",
            "datePublished": (
                self.created_at.strftime("%Y-%m-%d") if self.created_at else None
            ),
            "dateModified": (
                self.updated_at.strftime("%Y-%m-%d") if self.updated_at else None
            ),
        }

        # Add main image if present
        if self.main_image:
            schema["image"] = [self.main_image.url]

        # Remove None values for JSON-LD validity
        schema = {k: v for k, v in schema.items() if v is not None}

        return json.dumps(schema, ensure_ascii=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")


class RecipeIngredient(CustomModel):
    """Ingredients for a specific recipe"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name=_("Recipe"),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_("Ingredient"),
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Quantity"),
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Unit"),
    )

    def get_display_unit(self):
        """Return localized singular or plural unit name."""
        if not self.unit:
            return None
        if self.quantity and self.quantity != 1:
            return self.unit.name_plural
        return self.unit.name

    def get_display_ingredient(self):
        """Return localized singular or plural ingredient name."""
        if self.quantity and self.quantity != 1:
            return self.ingredient.name_plural
        return self.ingredient.name

    def __str__(self):
        """Human-readable representation like '2 cups flour' or '1 egg'."""
        parts = []

        # Quantity
        if self.quantity is not None:
            parts.append(str(self.quantity).replace(".00", ""))

        # Unit
        if self.unit:
            # Prefer abbreviation if present
            if self.unit.abbreviation:
                parts.append(self.unit.abbreviation)
            else:
                parts.append(self.get_display_unit())

        # Ingredient name (singular/plural)
        parts.append(self.get_display_ingredient())

        return " ".join(parts)

    class Meta:
        ordering = ["id"]
        unique_together = ["recipe", "ingredient"]
        verbose_name = _("Recipe Ingredient")
        verbose_name_plural = _("Recipe Ingredients")


class RecipeStep(CustomModel):
    """Step-by-step instructions for a recipe"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    step_number = models.PositiveIntegerField(verbose_name=_("Step Number"))
    instruction_de = models.TextField()
    instruction_en = models.TextField(blank=True)
    instruction_fr = models.TextField(blank=True)
    instruction_es = models.TextField(blank=True)
    instruction_it = models.TextField(blank=True)

    @property
    def instruction(self):
        return self.get_localized_value("instruction") or self.instruction_de

    def __str__(self):
        return f"Step {self.step_number}: {self.instruction[:50]}..."

    class Meta:
        ordering = ["step_number"]
        unique_together = ["recipe", "step_number"]
        verbose_name = _("Recipe Step")
        verbose_name_plural = _("Recipe Steps")

from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from config.db import CustomModel, PageModel


class Unit(CustomModel):
    """Model for measurement units"""

    name_de = models.CharField(max_length=50, verbose_name=_("Name (German)"))
    name_en = models.CharField(
        max_length=50, verbose_name=_("Name (English)"), null=True, blank=True
    )
    name_fr = models.CharField(
        max_length=50, verbose_name=_("Name (French)"), null=True, blank=True
    )
    name_es = models.CharField(
        max_length=50, verbose_name=_("Name (Spanish)"), null=True, blank=True
    )
    name_it = models.CharField(
        max_length=50, verbose_name=_("Name (Italian)"), null=True, blank=True
    )
    abbreviation = models.CharField(max_length=10, blank=True)

    @property
    def name(self):
        return self.get_localized_value("name") or self.name_de

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name_de"]
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")


class Ingredient(CustomModel):
    """Model for ingredients that can be reused across recipes"""

    name_de = models.CharField(max_length=100, verbose_name=_("Name (German)"))
    name_en = models.CharField(
        max_length=100, verbose_name=_("Name (English)"), null=True, blank=True
    )
    name_fr = models.CharField(
        max_length=100, verbose_name=_("Name (French)"), null=True, blank=True
    )
    name_es = models.CharField(
        max_length=100, verbose_name=_("Name (Spanish)"), null=True, blank=True
    )
    name_it = models.CharField(
        max_length=100, verbose_name=_("Name (Italian)"), null=True, blank=True
    )

    @property
    def name(self):
        return self.get_localized_value("name") or self.name_de

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name_de"]
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")


class Recipe(PageModel):
    """Main recipe model"""

    DIFFICULTY_LEVELS = [
        ("easy", _("Easy")),
        ("medium", _("Medium")),
        ("hard", _("Hard")),
    ]

    CATEGORIES = [
        ("appetizer", _("Appetizer")),
        ("main", _("Main Course")),
        ("dessert", _("Dessert")),
        ("snack", _("Snack")),
        ("beverage", _("Beverage")),
        ("bread", _("Bread")),
    ]

    # Introduction in multiple languages
    introduction_de = models.TextField(
        blank=True, verbose_name=_("Introduction (German)")
    )
    introduction_en = models.TextField(
        blank=True, verbose_name=_("Introduction (English)")
    )
    introduction_fr = models.TextField(
        blank=True, verbose_name=_("Introduction (French)")
    )
    introduction_es = models.TextField(
        blank=True, verbose_name=_("Introduction (Spanish)")
    )
    introduction_it = models.TextField(
        blank=True, verbose_name=_("Introduction (Italian)")
    )

    # Metadata
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_LEVELS,
        default="medium",
        verbose_name=_("Difficulty Level"),
    )
    category = models.CharField(
        max_length=20, choices=CATEGORIES, default="main", verbose_name=_("Category")
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

    # Servings
    servings = models.PositiveIntegerField(default=1, verbose_name=_("Servings"))

    # Images
    main_image = models.ImageField(
        upload_to="recipes/main/", null=True, blank=True, verbose_name=_("Main Image")
    )

    # Publication
    date_published = models.DateField(
        null=True, blank=True, verbose_name=_("Date Published")
    )
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published"))

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
        Ingredient, on_delete=models.CASCADE, verbose_name=_("Ingredient")
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Quantity"),
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Unit")
    )
    unit_text = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Custom unit if not in predefined units"),
        verbose_name=_("Custom Unit"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    def __str__(self):
        parts = []
        if self.quantity:
            parts.append(str(self.quantity))
        if self.unit:
            parts.append(self.unit.abbreviation or self.unit.name)
        elif self.unit_text:
            parts.append(self.unit_text)
        parts.append(self.ingredient.name)
        return " ".join(parts)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ["recipe", "ingredient"]
        verbose_name = _("Recipe Ingredient")
        verbose_name_plural = _("Recipe Ingredients")


class RecipeStep(CustomModel):
    """Step-by-step instructions for a recipe"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="steps", verbose_name=_("Recipe")
    )
    step_number = models.PositiveIntegerField(verbose_name=_("Step Number"))
    instruction_de = models.TextField(verbose_name=_("Instruction (German)"))
    instruction_en = models.TextField(
        blank=True, verbose_name=_("Instruction (English)")
    )
    instruction_fr = models.TextField(
        blank=True, verbose_name=_("Instruction (French)")
    )
    instruction_es = models.TextField(
        blank=True, verbose_name=_("Instruction (Spanish)")
    )
    instruction_it = models.TextField(
        blank=True, verbose_name=_("Instruction (Italian)")
    )

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

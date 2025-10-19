from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Ingredient, Recipe, RecipeIngredient, RecipeStep, Unit


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ["quantity", "unit", "ingredient"]
    verbose_name = _("Ingredient")
    verbose_name_plural = _("Ingredients")


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1
    fields = ["step_number", "instruction_de"]
    ordering = ["step_number"]
    verbose_name = _("Step")
    verbose_name_plural = _("Steps")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title_de", "category", "difficulty", "created_at"]
    list_filter = ["category", "difficulty", "created_at"]
    search_fields = ["title_de", "introduction_de"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [RecipeIngredientInline, RecipeStepInline]
    fields = (
        "title_de",
        "introduction_de",
        "main_image",
        "ingredients_image",
        "prep_image",
        "category",
        "difficulty",
        "prep_time",
        "cook_time",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name_de", "created_at"]
    search_fields = ["name_de"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (_("German"), {"fields": ("name_de", "name_plural_de")}),
        (
            _("Advanced Options - Other Languages"),
            {
                "classes": ("collapse",),
                "fields": (
                    "name_en",
                    "name_fr",
                    "name_es",
                    "name_it",
                    "name_plural_en",
                    "name_plural_fr",
                    "name_plural_es",
                    "name_plural_it",
                ),
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["name_de", "abbreviation", "created_at"]
    search_fields = ["name_de", "name_plural_de"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("German"),
            {
                "fields": (
                    "name_de",
                    "name_plural_de",
                    "abbreviation",
                )
            },
        ),
        (
            _("Advanced Options - Other Languages"),
            {
                "classes": ("collapse",),
                "fields": (
                    "name_en",
                    "name_fr",
                    "name_es",
                    "name_it",
                ),
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient", "quantity", "unit"]
    list_filter = ["recipe", "unit"]
    search_fields = ["recipe__title_de", "ingredient__name_de"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ["recipe", "step_number", "instruction_preview"]
    list_filter = ["recipe"]
    search_fields = ["recipe__title_de", "instruction_de"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "recipe",
                    "step_number",
                )
            },
        ),
        (_("Instruction (German)"), {"fields": ("instruction_de",)}),
        (
            _("Advanced Options - Other Languages"),
            {
                "classes": ("collapse",),
                "fields": (
                    "instruction_en",
                    "instruction_fr",
                    "instruction_es",
                    "instruction_it",
                ),
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description=_("Instruction Preview"))
    def instruction_preview(self, obj):
        return (
            obj.instruction_de[:50] + "..."
            if len(obj.instruction_de) > 50
            else obj.instruction_de
        )

from django.contrib import admin

from products.models import Product, ProductImage

# Register your models here.


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text_de")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title",)
    fields = (
        "title_de",
        "description_de",
        "product_type",
        "price_500g",
        "price_1kg",
        "price_per_unit",
    )
    inlines = (ProductImageInline,)

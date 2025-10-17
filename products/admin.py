from django.contrib import admin

from products.models import Product, ProductImage

# Register your models here.


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_img_de")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title",)
    fields = (
        "title_de",
        "description_de",
        "total_fat",
        "saturated_fat",
        "total_carbo",
        "sugar",
        "protein",
        "salt",
    )
    inlines = (ProductImageInline,)

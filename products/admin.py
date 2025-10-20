from django.contrib import admin



from .models import Product, ProductImage


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 1



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    inlines = [ProductImageInline]
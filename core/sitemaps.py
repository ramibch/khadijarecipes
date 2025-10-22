from django.contrib.sitemaps import Sitemap

from products.models import Product
from recipes.models import Recipe


class RecipeSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.7

    def items(self):
        return Recipe.objects.all()

    def lastmod(self, obj: Recipe):
        obj.updated_at


class ProductSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj: Product):
        obj.updated_at

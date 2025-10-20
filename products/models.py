from django.db import models

from django.utils.translation import get_language
from typing import Any



class Product(models.Model):
    # title
    title_de = models.CharField(max_length=256)
    title_en = models.CharField(max_length=256, null=True, blank=True)
    title_fr = models.CharField(max_length=256, null=True, blank=True)
    title_es = models.CharField(max_length=256, null=True, blank=True)
    title_it = models.CharField(max_length=256, null=True, blank=True)
    
    # slug
    slug_de = models.SlugField(max_length=256)
    slug_en = models.SlugField(max_length=256, null=True, blank=True)
    slug_fr = models.SlugField(max_length=256, null=True, blank=True)
    slug_es = models.SlugField(max_length=256, null=True, blank=True)
    slug_it = models.SlugField(max_length=256, null=True, blank=True)

    # description
    description_de = models.TextField()
    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)
    description_es = models.TextField(null=True, blank=True)
    description_it = models.TextField(null=True, blank=True)
    

    def get_value(self, attr) -> Any | None:
        lang = get_language()
        value = getattr(self, f"{attr}_{lang}", None)
        return value

    @property
    def title(self):
        return self.get_value("title") or self.title_de

    @property
    def slug(self):
        return self.get_value("slug") or self.slug_de

    @property
    def description(self):
        return self.get_value("description") or self.description_de

    def __str__(self):
        return self.title 


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")
    alt_text_de = models.CharField(max_length=256)
    alt_text_en = models.CharField(max_length=256, null=True, blank=True)
    alt_text_fr = models.CharField(max_length=256, null=True, blank=True)
    alt_text_es = models.CharField(max_length=256, null=True, blank=True)
    alt_text_it = models.CharField(max_length=256, null=True, blank=True)    

    def get_value(self, attr) -> Any | None:
        lang = get_language()
        value = getattr(self, f"{attr}_{lang}", None)
        return value

    @property
    def alt_text(self):
        return self.get_value("alt_text") or self.alt_text_de
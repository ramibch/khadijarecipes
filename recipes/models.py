from typing import Any

from django.db import models
from django.utils.translation import get_language


class Recipe(models.Model):
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

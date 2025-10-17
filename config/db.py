from typing import Any

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import get_language


class CustomModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def admin_url(self) -> str:
        ns = f"admin:{self._meta.app_label}_{self._meta.model_name}_change"
        return reverse(ns, args=(self.pk,))

    @property
    def full_admin_url(self) -> str:
        return settings.WEBSITE_URL + self.admin_url

    def get_localized_value(self, attr: str) -> Any | None:
        lang = get_language()
        value = getattr(self, f"{attr}_{lang}", None)
        return value


class PageModel(CustomModel):
    class Meta(CustomModel.Meta):
        abstract = True

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

    @property
    def title(self):
        return self.get_localized_value("title") or self.title_de

    @property
    def slug(self):
        return self.get_localized_value("slug") or self.slug_de

    @property
    def url(self):
        if hasattr(self, "get_absolute_url"):
            return self.get_absolute_url()
        raise NotImplementedError

    def save(self, *args, **kwargs):
        for lang in settings.LANGUAGE_CODES:
            if not hasattr(self, f"title_{lang}") or not hasattr(self, f"slug_{lang}"):
                continue
            title_value = getattr(self, f"title_{lang}", None)
            if title_value is None:
                continue
            setattr(self, f"slug_{lang}", slugify(title_value))
        super().save(*args, **kwargs)

import urllib

from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from config.db import CustomModel, PageModel


class ProductType(models.TextChoices):
    MIXED_PLATTERS = "mixed_pastries", _("Mixed platters")
    SWEET_PLATTERS = "sweet_pastries", _("Sweet platters")
    HONEY_PLATTERS = "honey_pastries", _("Honey platters")
    DOUGH_PRODUCTS = "dough_products", _("Dough products")
    COOKIES = "cookies", _("Cookies")
    OTHER = "other", _("Other products")


class Product(PageModel):
    description_de = models.TextField()
    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)
    description_es = models.TextField(null=True, blank=True)
    description_it = models.TextField(null=True, blank=True)
    product_type = models.CharField(max_length=32, choices=ProductType)
    calories = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
    )
    total_fat = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
    )
    saturated_fat = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
    )
    total_carbo = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
    )
    sugar = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
    )
    protein = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
    )
    salt = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
    )

    price_500g = models.DecimalField(
        verbose_name=_("Price 500g"),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
    )
    price_1kg = models.DecimalField(
        verbose_name=_("Price 1kg"),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
    )
    price_per_unit = models.DecimalField(
        verbose_name=_("Price per Unit"),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

    @property
    def nutrition_info_available(self):
        return bool(self.total_fat and self.total_carbo and self.protein)

    def save(self, *args, **kwargs):
        if self.nutrition_info_available:
            self.calories = 9 * self.total_fat + 4 * (self.total_carbo + self.protein)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy("product_detail", args=(self.slug,))

    @property
    def description(self):
        return self.get_localized_value("description") or self.description_de

    @property
    def whatsapp_order_url(self):
        text = _("Hi") + " Khadija\n\n"
        text += _("I am interested in this product") + "\n\n"
        text += self.title
        return f"{settings.WHATSAPP_URL}?text={urllib.parse.quote_plus(text)}"


class ProductImage(CustomModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images/")

    image_100x100 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(100, 100)],
        format="WEBP",
        options={"quality": 60},
    )

    image_500x500 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(500, 500)],
        format="WEBP",
        options={"quality": 90},
    )

    image_300x300 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(300, 300)],
        format="WEBP",
        options={"quality": 90},
    )

    alt_text_de = models.CharField(max_length=256)
    alt_text_en = models.CharField(max_length=256, null=True, blank=True)
    alt_text_fr = models.CharField(max_length=256, null=True, blank=True)
    alt_text_es = models.CharField(max_length=256, null=True, blank=True)
    alt_text_it = models.CharField(max_length=256, null=True, blank=True)

    @property
    def alt_text(self):
        return self.get_localized_value("alt") or self.alt_de

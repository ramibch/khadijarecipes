import urllib
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from PIL import Image

from config.db import CustomModel, PageModel


class ProductType(models.TextChoices):
    MIXED_PLATTERS = "mixed_pastries", _("Mixed platters")
    SWEET_PLATTERS = "sweet_pastries", _("Sweet platters")
    HONEY_PLATTERS = "honey_pastries", _("Honey platters")
    COOKIES = "cookies", _("Cookies")


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
    image_800 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    image_600 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    image_400 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    image_200 = models.ImageField(upload_to="product-images/", null=True, blank=True)
    alt_de = models.CharField(max_length=256)
    alt_en = models.CharField(max_length=256, null=True, blank=True)
    alt_fr = models.CharField(max_length=256, null=True, blank=True)
    alt_es = models.CharField(max_length=256, null=True, blank=True)
    alt_it = models.CharField(max_length=256, null=True, blank=True)

    def description(self):
        return self.get_localized_value("alt") or self.alt_de

    def save(self, *args, **kwargs):
        # Save initially so we have self.image stored
        if not self.pk or not self.image:
            super().save(*args, **kwargs)

        if self.image:
            # Open image safely (works on S3 and local)
            self.image.open()
            img = Image.open(self.image)
            img = img.convert("RGB")

            sizes = [800, 600, 400, 200]

            for width in sizes:
                field = getattr(self, f"image_{width}")
                if field and field.name:
                    continue

                aspect_ratio = img.height / img.width
                height = int(width * aspect_ratio)
                resized = img.resize((width, height), Image.LANCZOS)

                buffer = BytesIO()
                resized.save(buffer, format="WEBP", optimize=True, quality=85)
                buffer.seek(0)

                base_name = self.image.name.rsplit(".", 1)[0]
                filename = f"{base_name}_{width}.webp"

                getattr(self, f"image_{width}").save(
                    filename, ContentFile(buffer.read()), save=False
                )

            # Important: close file handle
            self.image.close()

        super().save(*args, **kwargs)

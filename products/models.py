# Create your models here.
from django.db import models
from django.urls import reverse_lazy

from config.db import CustomModel, PageModel


class Product(PageModel):
    description_de = models.TextField()
    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)
    description_es = models.TextField(null=True, blank=True)
    description_it = models.TextField(null=True, blank=True)
    calories = models.DecimalField(max_digits=4, decimal_places=1)
    total_fat = models.DecimalField(max_digits=3, decimal_places=1)
    saturated_fat = models.DecimalField(max_digits=3, decimal_places=1)
    total_carbo = models.DecimalField(max_digits=3, decimal_places=1)
    sugar = models.DecimalField(max_digits=3, decimal_places=1)
    protein = models.DecimalField(max_digits=3, decimal_places=1)
    salt = models.DecimalField(max_digits=3, decimal_places=2)

    def save(self, *args, **kwargs):
        self.calories = 9 * self.total_fat + 4 * (self.total_carbo + self.protein)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy("product_detail", args=(self.slug))

    def description(self):
        return self.get_localized_value("description") or self.description_de


class ProductImage(CustomModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images/")
    alt_img_de = models.CharField(max_length=256)
    alt_img_en = models.CharField(max_length=256, null=True, blank=True)
    alt_img_fr = models.CharField(max_length=256, null=True, blank=True)
    alt_img_es = models.CharField(max_length=256, null=True, blank=True)
    alt_img_it = models.CharField(max_length=256, null=True, blank=True)

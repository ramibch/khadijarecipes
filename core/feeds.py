from django.contrib.syndication.views import Feed
from django.utils import timezone
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _

from products.models import Product
from recipes.models import Recipe

activate("de")


class ProductPinFeed(Feed):
    title = _("List of products")
    link = "/"
    description = _("Last products published in my website")
    item_enclosure_mime_type = "image/png"

    def items(self):
        past = timezone.now() - timezone.timedelta(days=30)
        return Product.objects.filter(
            created_at__gte=past,
            productimage__isnull=False,
        ).distinct()

    def item_title(self, item: Product):
        return item.title

    def item_description(self, item: Product):
        return item.description

    def item_lastupdated(self, item: Product):
        return item.updated_at

    def item_enclosure_url(self, item: Product):
        return item.productimage_set.first().image.url

    def item_enclosure_length(self, item: Product):
        return item.productimage_set.first().image.size


class RecipePinFeed(Feed):
    title = _("List of recipes")
    link = "/"
    description = _("Last recipes published in my website")
    item_enclosure_mime_type = "image/png"

    def items(self):
        past = timezone.now() - timezone.timedelta(days=30)
        return (
            Recipe.objects.filter(created_at__gte=past)
            .exclude(main_image="")
            .distinct()
        )

    def item_title(self, item: Recipe):
        return item.title

    def item_description(self, item: Recipe):
        return item.introduction

    def item_lastupdated(self, item: Recipe):
        return item.updated_at

    def item_enclosure_url(self, item: Recipe):
        return item.main_image.url

    def item_enclosure_length(self, item: Recipe):
        return item.main_image.size

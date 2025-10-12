from django.contrib.sitemaps import Sitemap


class RecipeSitempa(Sitemap):
    changefreq = "yearly"
    priority = 0.7

    def items(self):
        return []

    def lastmod(self, obj):
        pass


def get_sitemaps(*args, **kwargs):
    return {
        "recipes": RecipeSitempa(),
    }

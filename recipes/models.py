from django.urls import reverse_lazy

from config.db import PageModel


class Recipe(PageModel):
    def get_absolute_url(self):
        return reverse_lazy("recipe_detail", args=(self.slug))

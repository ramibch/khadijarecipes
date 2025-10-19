from functools import reduce
from operator import or_

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Recipe


class RecipeListView(ListView):
    template_name = "recipes/recipe_list.html"
    model = Recipe
    context_object_name = "recipes"

    def get_queryset(self):
        return super().get_queryset().exclude(main_image="")


class RecipeDetailView(DetailView):
    template_name = "recipes/recipe_detail.html"
    model = Recipe
    context_object_name = "recipe"

    def get_object(self, queryset=None):
        slug = self.kwargs["slug"]
        slug_d = {f"slug_{lang}": slug for lang in settings.LANGUAGE_CODES}
        expr = reduce(or_, (Q(**d) for d in [dict([i]) for i in slug_d.items()]))
        try:
            self.object = Recipe.objects.get(expr)
            return self.object
        except Recipe.DoesNotExist as err:
            raise Http404 from err

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.object.title
        context["page_description"] = self.object.introduction[:300]
        return context

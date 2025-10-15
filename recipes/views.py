from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Recipe


class RecipeListView(ListView):
    template_name = "recipes/recipe_list.html"
    model = Recipe


class RecipeDetailView(DetailView):
    template_name = "recipes/recipe_detail.html"
    model = Recipe

from django.urls import path

from .views import RecipeDetailView, RecipeListView

urlpatterns = [
    path("", RecipeListView.as_view(), name="recipe_list"),
    path("<slug:slug>", RecipeDetailView.as_view(), name="recipe_detail"),
]

from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .sitemaps import ProductSitemap, RecipeSitemap
from .views import (
    HomeView,
    PrivacyView,
    RecipeDetailRedirectView,
    RecipeListRedirectView,
    RobotTxtView,
    TermsView,
    favicon_view,
    product_feed_pins,
    recipe_feed_pins,
)

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"recipes": RecipeSitemap(), "products": ProductSitemap()}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Favicon
    path("favicon.ico", favicon_view, name="favicon"),
    # robots.txt
    path("robots.txt", RobotTxtView.as_view(), name="robots"),
    # "static" pages
    path("~/p", PrivacyView.as_view(), name="privacy"),
    path("~/t", TermsView.as_view(), name="terms"),
    # Home
    path("", HomeView.as_view(), name="home"),
    # Pins
    path("pins/products/<str:lang>", product_feed_pins),
    path("pins/recipes/<str:lang>", recipe_feed_pins),
    # Redirects (previous site)
    path("<str:lang>/blog/", RecipeListRedirectView.as_view()),
    path("<str:lang>/blog/<slug:slug>/", RecipeDetailRedirectView.as_view()),
]

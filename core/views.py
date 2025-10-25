from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views.generic import RedirectView, TemplateView

from core.models import Faq
from products.models import Product

from .feeds import ProductPinFeed, RecipePinFeed


class RecipeListRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("recipe_list")


class RecipeDetailRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("recipe_detail", kwargs={"slug": self.kwargs["slug"]})


class HomeView(TemplateView):
    http_method_names = ["get"]
    template_name = "home.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = _("Tasty recipes make from Bern")
        cxt["products"] = Product.objects.all()
        cxt["faqs"] = Faq.objects.filter(is_active=True)
        return cxt


class PrivacyView(TemplateView):
    http_method_names = ["get"]
    template_name = "privacy.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = _("Privacy Policy")
        return cxt


class TermsView(TemplateView):
    http_method_names = ["get"]
    template_name = "terms.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = _("Terms and Conditions")
        return cxt


class RobotTxtView(TemplateView):
    http_method_names = ["get"]
    content_type = "text/plain"
    template_name = "robots.txt"


@require_GET
@cache_control(max_age=60 * 60 * 24 * 30, public=True, immutable=False)
def favicon_view(request) -> HttpResponse:
    emoji = "🍳"
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        + f'<text y=".9em" font-size="90">{emoji}</text>'
        + "</svg>"
    )
    return HttpResponse(svg_content, content_type="image/svg+xml; charset=utf-8")


def error_404(request, exception):
    cxt = {"page_title": _("Page Not found")}
    return render(request, "error.html", cxt, status=404)


def error_403(request, exception):
    cxt = {"page_title": _("Request blocked")}
    return render(request, "error.html", cxt, status=403)


def error_500(request):
    cxt = {"page_title": _("Server Error")}
    return render(request, "error.html", cxt, status=500)


def product_feed_pins(request: HttpRequest, lang: str):
    with translation.override(lang):
        return ProductPinFeed()(request)


def recipe_feed_pins(request: HttpRequest, lang: str):
    with translation.override(lang):
        return RecipePinFeed()(request)

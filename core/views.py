from typing import Any

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView


class HomeView(TemplateView):
    http_method_names = ["get"]
    template_name = "core/home.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = _("Tasty recipes make from Bern")
        return cxt


class PrivacyView(TemplateView):
    http_method_names = ["get"]
    template_name = "core/privacy.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = _("Privacy Policy")
        return cxt


class TermsView(TemplateView):
    http_method_names = ["get"]
    template_name = "core/terms.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = _("Terms and Conditions")
        return cxt


class RobotTxtView(TemplateView):
    http_method_names = ["get"]
    content_type = "text/plain"
    template_name = "core/robots.txt"


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
    return render(request, "core/error.html", cxt, status=404)


def error_403(request, exception):
    cxt = {"page_title": _("Request blocked")}
    return render(request, "core/error.html", cxt, status=403)


def error_500(request):
    cxt = {"page_title": _("Server Error")}
    return render(request, "core/error.html", cxt, status=500)

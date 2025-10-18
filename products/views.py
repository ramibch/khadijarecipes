from functools import reduce
from operator import or_

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.views.generic.detail import DetailView

from core.models import Faq
from products.models import Product


class ProductDetailView(DetailView):
    template_name = "product_detail.html"
    model = Product
    context_object_name = "product"

    def get_object(self, queryset=...):
        slug = self.kwargs["slug"]
        slug_d = {f"slug_{lang}": slug for lang in settings.LANGUAGE_CODES}
        expr = reduce(or_, (Q(**d) for d in [dict([i]) for i in slug_d.items()]))
        try:
            self.object = Product.objects.get(expr)
            return self.object
        except Product.DoesNotExist as err:
            raise Http404 from err

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt["page_title"] = self.object.title
        cxt["page_description"] = self.object.description[:300]
        cxt["faqs"] = Faq.objects.filter(is_active=True)
        return cxt

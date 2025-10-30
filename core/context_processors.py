import json

from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import gettext as _


def brand(request):
    emoji = "🍳"
    name = "Khadija Recipes"
    description = _(
        "homemade Moroccan specialties and creative recipes from Bern. "
        "Discover traditional sweets or try new recipes at home."
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": request.build_absolute_uri(),
        "name": name,
        "description": description,
        "inLanguage": request.LANGUAGE_CODE,
        "publisher": {"@type": "Person", "name": "Khadija El Azzouzi"},
    }
    return {
        "request": request,
        "brand_name": name,
        "brand_emoji": emoji,
        "page_description": description,  # will be overriden on views (hopefully)
        "website_schema": json.dumps(schema, ensure_ascii=True),
    }


def links(request):
    lang = get_language()
    return {
        "request": request,
        "website_url": settings.WEBSITE_URL,
        "whatsapp_url": settings.WHATSAPP_URL,
        "telegram_url": settings.TELEGRAM_URL,
        "instagram_url": settings.INSTAGRAM_URL,
        "temp_blog_url": f"https://khadijarecipes.com/{lang}/blog/",
    }

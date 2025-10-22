from django.conf import settings
from django.utils.translation import get_language


def brand(request):
    return {
        "request": request,
        "brand_name": "Khadija Recipes",
        "brand_name_short": "Khadija",
        "brand_emoji": "🍳",
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

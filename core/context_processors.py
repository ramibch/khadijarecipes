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
        "whatsapp_url": "https://wa.me/+41772363205",
        "telegram_url": "https://t.me/khadijarecipes",
        "instagram_url": "https://www.instagram.com/khadijarecipes/",
        "temp_blog_url": f"https://khadijarecipes.com/{lang}/blog/",
    }

from django.contrib import admin

from core.models import Faq


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    fields = ("question_de", "answer_de")
    list_display = ("question", "answer", "created_at")

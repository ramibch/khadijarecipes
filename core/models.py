from django.db import models

from config.db import CustomModel


class Faq(CustomModel):
    question_de = models.CharField(max_length=256)
    question_en = models.CharField(max_length=256, null=True, blank=True)
    question_fr = models.CharField(max_length=256, null=True, blank=True)
    question_es = models.CharField(max_length=256, null=True, blank=True)
    question_it = models.CharField(max_length=256, null=True, blank=True)
    answer_de = models.TextField()
    answer_en = models.TextField(null=True, blank=True)
    answer_fr = models.TextField(null=True, blank=True)
    answer_es = models.TextField(null=True, blank=True)
    answer_it = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def question(self):
        return self.get_localized_value("question") or self.question_de

    @property
    def answer(self):
        return self.get_localized_value("answer") or self.answer_de

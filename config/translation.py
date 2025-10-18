from typing import Any

import deepl
from deepl.api_data import Formality
from django.conf import settings


def rename_deepl_source(lang: str) -> str:
    """
    Rename the source language according to DeepL API expectations

    https://developers.deepl.com/docs/resources/supported-languages#source-languages

    """
    return lang.upper()


def rename_deepl_target(lang: str) -> str:
    """
    Rename the target language according to DeepL API expectations

    https://developers.deepl.com/docs/resources/supported-languages#target-languages

    """

    adjustments = {"en": "en-gb", "pt": "pt-pt", "zh": "zh-hans"}
    try:
        out = adjustments[lang]
    except KeyError:
        out = lang
    return out.upper()


def translate_text(
    from_lang: str,
    to_lang: str,
    text: str,
    output_if_error: str | None = None,
) -> str | Any:
    """
    Translate text with DeepL API
    """
    try:
        result = deepl.Translator(settings.DEEPL_AUTH_KEY).translate_text(
            text=text,
            source_lang=rename_deepl_source(from_lang),
            target_lang=rename_deepl_target(to_lang),
            formality=Formality.PREFER_LESS,
        )
        return result.text

    except Exception as e:
        if output_if_error:
            return output_if_error
        raise e

import os

import polib
from django.conf import settings
from django.core.management.base import BaseCommand

from config.translation import translate_text


class Command(BaseCommand):
    help = "Translate untranslated messages in .po files using DeepL"

    def handle(self, *args, **options):
        langs = getattr(settings, "LANGUAGE_CODES_WITHOUT_DEFAULT", [])
        if not langs:
            self.stderr.write(
                self.style.WARNING(
                    "No languages found in LANGUAGE_CODES_WITHOUT_DEFAULT"
                )
            )
            return

        default_lang = getattr(settings, "LANGUAGE_CODE", "en").split("-")[0]

        for lang in langs:
            if lang.startswith(default_lang):
                # Skip default language
                continue

            po_path = os.path.join(
                settings.BASE_DIR, "locale", lang, "LC_MESSAGES", "django.po"
            )

            if not os.path.exists(po_path):
                self.stderr.write(self.style.WARNING(f"File not found: {po_path}"))
                continue

            po = polib.pofile(po_path)
            updated = False

            for entry in po.untranslated_entries() + po.fuzzy_entries():
                if not entry.msgid.strip():
                    continue

                # Singular
                if not entry.msgid_plural:
                    if "%(" in entry.msgid or "{" in entry.msgid:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping entry with variables: {entry.msgid}"
                            )
                        )
                        continue
                    translated = translate_text(
                        from_lang=default_lang,
                        to_lang=lang,
                        text=entry.msgid,
                        output_if_error=None,
                    )
                    if translated:
                        entry.msgstr = str(translated)
                        entry.fuzzy = False
                        updated = True
                        self.stdout.write(f"[{lang}] {entry.msgid} → {entry.msgstr}")

                # Plurals
                else:
                    for idx, msgid in enumerate([entry.msgid, entry.msgid_plural]):
                        if "%(" in msgid or "{" in msgid:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Skipping entry with variables: {msgid}"
                                )
                            )
                            continue

                        translated = translate_text(
                            from_lang=default_lang,
                            to_lang=lang,
                            text=msgid,
                            output_if_error=None,
                        )
                        if translated:
                            entry.msgstr_plural[idx] = str(translated)
                            entry.fuzzy = False
                            updated = True
                            self.stdout.write(
                                f"[{lang}] (plural {idx}) {msgid} → {translated}"
                            )

            if updated:
                po.save()
                self.stdout.write(self.style.SUCCESS(f"Updated {po_path}"))

            else:
                self.stdout.write(f"No changes in {po_path}")

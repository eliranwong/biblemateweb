# Translations

UI strings are in `translations/eng.py`, `tc.py` and `sc.py`. Use:

```python
from biblemateweb import get_translation
label = get_translation("Settings")
```

The language comes from `app.storage.user["ui_language"]` (`eng`, `tc`, `sc`). Missing keys fall back to the key text itself (the English string).

## Add a language

1. Add a translation module (a dict like `translation_tc`) and import it in `__init__.py`, then extend `get_translation()` to select it.
2. Add the option to the language selector in `main.py` (`/settings`).
3. Provide Bible book names for the language (`BibleBooks.abbrev[...]`).
4. Add long-form messages (e.g. `welcome_chat_mode`) for AI pages.

User view: [Languages & Fonts](../basics/languages_and_fonts.md).

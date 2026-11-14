# 語言翻譯

UI 字串位於 `translations/eng.py`、`tc.py` 與 `sc.py`。使用方式：

```python
from biblemateweb import get_translation
label = get_translation("Settings")
```

語言設定來自 `app.storage.user["ui_language"]`（`eng`、`tc`、`sc`）。若缺少鍵值，則回退至鍵名文字本身（英文原文字串）。

## 新增語言

1. 新增一個翻譯模組（類似 `translation_tc` 的字典）並在 `__init__.py` 中匯入，然後擴充 `get_translation()` 以選擇它。
2. 在 `main.py`（`/settings`）的語言選擇器中新增該選項。
3. 為該語言提供聖經書卷名稱（`BibleBooks.abbrev[...]`）。
4. 為 AI 頁面新增長篇訊息（例如 `welcome_chat_mode`）。

使用者視角：[語言與字型](../basics/languages_and_fonts.md)。

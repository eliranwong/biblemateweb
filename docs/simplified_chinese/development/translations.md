# 语言翻译

UI 字符串位于 `translations/eng.py`、`tc.py` 与 `sc.py`。使用方式：

```python
from biblemateweb import get_translation
label = get_translation("Settings")
```

语言设定来自 `app.storage.user["ui_language"]`（`eng`、`tc`、`sc`）。若缺少键值，则回退到键名文本本身（英文原始字符串）。

## 添加语言

1. 添加一个翻译模块（类似 `translation_tc` 的字典）并在 `__init__.py` 中导入，然后扩展 `get_translation()` 以选择它。
2. 在 `main.py`（`/settings`）的语言选择器中添加该选项。
3. 为该语言提供圣经书卷名称（`BibleBooks.abbrev[...]`）。
4. 为 AI 页面添加长篇消息（例如 `welcome_chat_mode`）。

用户视角：[语言与字体](../basics/languages_and_fonts.md)。

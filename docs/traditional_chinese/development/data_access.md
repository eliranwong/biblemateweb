# 資料存取

- 聖經、聖經註釋與原文詞典皆為 SQLite 檔案，透過 **APSW** 在上下文管理器中讀取。
- `getBiblePath(code)` 將聖經代碼對應至檔案；`getBibleChapter`、`getBibleChapterVerses`、`getBibleBookList`、`getBibleChapterList`、`getBibleVerseList` 位於 `fx/bible.py`。
- `get_bible_content(user_input, bible, sql_query, refs, search_mode, ...)` 支援經文檢索與搜索。`search_mode`：`1` 字面、`2` 模式（使用註冊至 APSW 的自訂 `regexp()`）、`3` 語義（向量儲存於 `~/biblemate/data/vectors/bible.db`）。
- 結果上限受限於 `config.verses_limit`。
- 資源字典位於 `config`：`config.bibles`、`config.bibles_custom`、`config.commentaries`、`config.lexicons`、`config.audio`。
- 工具提示：`fx/tooltips.py`（`get_tooltip_data`、詞彙、形態學分析與聖經筆記資料）。
- 筆記：`fx/cloud_index_manager.py`（筆記的 Google Drive 索引）。

```python
from biblemateweb.fx.bible import getBiblePath, get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

parser = BibleVerseParser(False)
verses = get_bible_content(user_input="John 3:16", bible="NET", parser=parser)
```

資源佈局：[數據與資源](../server_setup/data_and_resources.md)。

# 数据访问

- 圣经、圣经注释与原文词典均为 SQLite 文件，通过 **APSW** 在上下文管理器中读取。
- `getBiblePath(code)` 将圣经代码映射到文件；`getBibleChapter`、`getBibleChapterVerses`、`getBibleBookList`、`getBibleChapterList`、`getBibleVerseList` 位于 `fx/bible.py`。
- `get_bible_content(user_input, bible, sql_query, refs, search_mode, ...)` 支持经文检索与搜索。`search_mode`：`1` 字面、`2` 模式（使用注册到 APSW 的自定义 `regexp()`）、`3` 语义（向量存储于 `~/biblemate/data/vectors/bible.db`）。
- 结果上限受限于 `config.verses_limit`。
- 资源字典位于 `config`：`config.bibles`、`config.bibles_custom`、`config.commentaries`、`config.lexicons`、`config.audio`。
- 工具提示：`fx/tooltips.py`（`get_tooltip_data`、词汇、形态学分析与圣经笔记数据）。
- 笔记：`fx/cloud_index_manager.py`（笔记的 Google Drive 索引）。

```python
from biblemateweb.fx.bible import getBiblePath, get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

parser = BibleVerseParser(False)
verses = get_bible_content(user_input="John 3:16", bible="NET", parser=parser)
```

资源布局：[数据与资源](../server_setup/data_and_resources.md)。

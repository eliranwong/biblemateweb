# Data Access

- Bibles, commentaries and lexicons are SQLite files read with **APSW** inside context managers.
- `getBiblePath(code)` maps a Bible code to a file; `getBibleChapter`, `getBibleChapterVerses`, `getBibleBookList`, `getBibleChapterList`, `getBibleVerseList` live in `fx/bible.py`.
- `get_bible_content(user_input, bible, sql_query, refs, search_mode, ...)` powers verse retrieval and searching. `search_mode`: `1` literal, `2` regex (custom `regexp()` registered with APSW), `3` semantic (vectors in `~/biblemate/data/vectors/bible.db`).
- Results are capped by `config.verses_limit`.
- Resource dictionaries are on `config`: `config.bibles`, `config.bibles_custom`, `config.commentaries`, `config.lexicons`, `config.audio`.
- Tooltips: `fx/tooltips.py` (`get_tooltip_data`, lexical, morphology and Bible-note data).
- Notes: `fx/cloud_index_manager.py` (Google Drive index of notes).

```python
from biblemateweb.fx.bible import getBiblePath, get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

parser = BibleVerseParser(False)
verses = get_bible_content(user_input="John 3:16", bible="NET", parser=parser)
```

Resource layout: [Data & Resources](../server_setup/data_and_resources.md).

# 工具（选择工具）

当开启 `工具` 复选框时，BibleMate 会为您的请求挑选最合适的圣经研读工具，而非仅回复纯 AI 文本。这能提高准确度，因为经文与各项资源均直接取自应用程序的内置数据。

| | |
|---|---|
| 键值 | `auto_tool_selection` |
| 默认 | 关闭 |

## 运作方式

1. **选择工具** 面板会显示建议的工具。
2. 若开启[审查](chat_review.md)，可从列表中挑选（点击 `更多...` 显示所有工具）；否则将自动采用第一个建议的工具。
3. 对于 AI 工具，**工具指示** 步骤会将您的需求转化为精确的运行指示（在审查模式下可进行编辑）。
4. 工具随即运行并呈现结果。

## 自行指定工具

在您的消息开头输入 `@tool_name `，例如 `@write_bible_sermon John 3:16`，即可直接调用该工具。

## 可用工具

**数据工具（非 AI 生成）：** `search_the_bible`、`compare_bible_translations`、`retrieve_bible_cross_references`、`retrieve_bible_verses`、`retrieve_hebrew_or_greek_bible_verses`、`retrieve_interlinear_hebrew_or_greek_bible_verses`、`retrieve_chinese_bible_verses`、`retrieve_verse_morphology`、`retrieve_bible_chapter`、`read_bible_commentary`、`read_chinese_bible_commentary`。

**专家角色：** `ask_theologian`、`ask_pastor`、`ask_bible_scholar`、`anyalyze_psalms`、`write_pastor_prayer`、`quote_bible_verses`、`refine_bible_translation`、`write_bible_perspectives`。

**研经与写作工具：** `explain_bible_meaning`、`interpret_old_testament_verse`、`interpret_new_testament_verse`、`write_bible_sermon`、`write_bible_devotion`、`write_bible_questions`、`write_bible_outline`、`write_bible_insights`、`write_bible_applications`、`write_bible_chapter_summary`、`write_bible_book_introduction`、`write_bible_theology`、`write_bible_canonical_context`、`write_bible_thought_progression`、`write_bible_related_summary`、`write_bible_character_study`、`write_bible_location_study`、`expound_bible_topic`、`quote_bible_promises`、`identify_bible_keywords`。

**主题与重点：** `study_bible_themes`、`study_old_testament_themes`、`study_new_testament_themes`、`write_old_testament_highlights`、`write_new_testament_highlights`、`write_old_testament_historical_context`、`write_new_testament_historical_context`。

**祷告与翻译：** `write_bible_prayer`、`write_short_bible_prayer`、`translate_hebrew_bible_verse`、`translate_greek_bible_verse`。

`get_direct_text_response` 为默认值：即一般 AI 纯文本回答。

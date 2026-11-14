# 工具（選用工具）

當開啟 `工具` 核取方塊時，BibleMate 會為您的請求挑選最合適的聖經研讀工具，而非僅回覆純 AI 文字。這能提高準確度，因為經文與各項資源均直接取自應用程式的內建數據。

| | |
|---|---|
| 鍵值 | `auto_tool_selection` |
| 預設 | 關閉 |

## 運作方式

1. **選用工具** 面板會顯示建議的工具。
2. 若開啟[審查](chat_review.md)，可從清單中挑選（點擊 `更多...` 顯示所有工具）；否則將自動採用第一個建議的工具。
3. 對於 AI 工具，**工具指示** 步驟會將您的需求轉化為精確的執行指示（在審查模式下可進行編輯）。
4. 工具隨即執行並呈現結果。

## 自行指定工具

在您的訊息開頭輸入 `@tool_name `，例如 `@write_bible_sermon John 3:16`，即可直接調用該工具。

## 可用工具

**數據工具（非 AI 生成）：** `search_the_bible`、`compare_bible_translations`、`retrieve_bible_cross_references`、`retrieve_bible_verses`、`retrieve_hebrew_or_greek_bible_verses`、`retrieve_interlinear_hebrew_or_greek_bible_verses`、`retrieve_chinese_bible_verses`、`retrieve_verse_morphology`、`retrieve_bible_chapter`、`read_bible_commentary`、`read_chinese_bible_commentary`。

**專家角色：** `ask_theologian`、`ask_pastor`、`ask_bible_scholar`、`anyalyze_psalms`、`write_pastor_prayer`、`quote_bible_verses`、`refine_bible_translation`、`write_bible_perspectives`。

**研經與寫作工具：** `explain_bible_meaning`、`interpret_old_testament_verse`、`interpret_new_testament_verse`、`write_bible_sermon`、`write_bible_devotion`、`write_bible_questions`、`write_bible_outline`、`write_bible_insights`、`write_bible_applications`、`write_bible_chapter_summary`、`write_bible_book_introduction`、`write_bible_theology`、`write_bible_canonical_context`、`write_bible_thought_progression`、`write_bible_related_summary`、`write_bible_character_study`、`write_bible_location_study`、`expound_bible_topic`、`quote_bible_promises`、`identify_bible_keywords`。

**主題與重點：** `study_bible_themes`、`study_old_testament_themes`、`study_new_testament_themes`、`write_old_testament_highlights`、`write_new_testament_highlights`、`write_old_testament_historical_context`、`write_new_testament_historical_context`。

**禱告與翻譯：** `write_bible_prayer`、`write_short_bible_prayer`、`translate_hebrew_bible_verse`、`translate_greek_bible_verse`。

`get_direct_text_response` 為預設值：即一般 AI 純文字回答。

# Tools (Tool Selection)

When the `Tools` checkbox is on, BibleMate chooses a Bible study tool suited to your request instead of replying with plain AI text. This improves accuracy because verses and resources come from the app's data.

| | |
|---|---|
| Key | `auto_tool_selection` |
| Default | Off |

## How it works

1. A **Tool Selection** panel shows the suggested tool(s).
2. With [Review](chat_review.md) on, choose from a list (`More...` shows all tools); otherwise the first suggestion is used.
3. For AI tools, a **Tool Instruction** step turns your request into a precise instruction (editable under Review).
4. The tool runs and the result is shown.

## Choose a tool yourself

Start your message with `@tool_name `, e.g. `@write_bible_sermon John 3:16`. The tool is used directly.

## Available tools

**Data tools (no AI generation):** `search_the_bible`, `compare_bible_translations`, `retrieve_bible_cross_references`, `retrieve_bible_verses`, `retrieve_hebrew_or_greek_bible_verses`, `retrieve_interlinear_hebrew_or_greek_bible_verses`, `retrieve_chinese_bible_verses`, `retrieve_verse_morphology`, `retrieve_bible_chapter`, `read_bible_commentary`, `read_chinese_bible_commentary`.

**Specialist personas:** `ask_theologian`, `ask_pastor`, `ask_bible_scholar`, `anyalyze_psalms`, `write_pastor_prayer`, `quote_bible_verses`, `refine_bible_translation`, `write_bible_perspectives`.

**Study and writing tools:** `explain_bible_meaning`, `interpret_old_testament_verse`, `interpret_new_testament_verse`, `write_bible_sermon`, `write_bible_devotion`, `write_bible_questions`, `write_bible_outline`, `write_bible_insights`, `write_bible_applications`, `write_bible_chapter_summary`, `write_bible_book_introduction`, `write_bible_theology`, `write_bible_canonical_context`, `write_bible_thought_progression`, `write_bible_related_summary`, `write_bible_character_study`, `write_bible_location_study`, `expound_bible_topic`, `quote_bible_promises`, `identify_bible_keywords`.

**Themes and highlights:** `study_bible_themes`, `study_old_testament_themes`, `study_new_testament_themes`, `write_old_testament_highlights`, `write_new_testament_highlights`, `write_old_testament_historical_context`, `write_new_testament_historical_context`.

**Prayer and translation:** `write_bible_prayer`, `write_short_bible_prayer`, `translate_hebrew_bible_verse`, `translate_greek_bible_verse`.

`get_direct_text_response` is the default: a plain AI answer.

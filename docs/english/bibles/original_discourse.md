# Original Discourse Bible (ODB)

The original text annotated with discourse structure, to follow how sentences and sections connect.

## Open

- **Bibles** menu → Original Discourse Bible (area: Bible), or **Parallel Bibles** menu (area: Tool).
- [Quick Search](../basics/quick_search.md): type `ODB`, or `ODB:::John 3:16` style references.

## Features

- Same [selectors](../integrations/bible_selectors.md), [three-dot menu](../integrations/three_dot_menu.md) (💡 icons for Book/Chapter/Verse Tools) and [verse popup](../integrations/verse_menu.md) as other Bibles.
- Original words are interactive: hover over (or tap) any Hebrew or Greek word to open a [popup window](../integrations/word_tooltips.md) showing its **manuscript form** (with transliteration, pronunciation, and an inline **manuscript-form audio player**), **lemma form** (with an inline **lemma-form audio player**), **morphology**, **interlinear gloss**, and **translation**. Click the manuscript word or lemma inside the popup to open [Lexicons](../search/search_lexicons.md).
- Verse translations are dynamically loaded from available `.bible` modules (`~/biblemate/data/bibles/` and `~/biblemate/data_custom/bibles/` when a valid [custom token](../user_preferences/custom_token.md) is active). Configure OT and NT translations in [Preferences](../user_preferences/README.md) (`ODB OT Translation` default `NET`, `ODB NT Translation` default `NET`). Tagged translation words support bidirectional hover highlighting with the original text and open word tooltips on hover.
- Hebrew and Greek fonts are bundled for correct display.
- Works with [Sync](../layout/sync.md) and synchronised scrolling.

Data file: `~/biblemate/data/original/ODB.bible` ([Data & Resources](../server_setup/data_and_resources.md)). See also [Word Morphology](../tools/tool_morphology.md).

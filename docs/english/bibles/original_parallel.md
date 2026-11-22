# Original Parallel Bible (OPB)

The original-language text presented in parallel with translation, to compare source and rendering.

## Open

- **Bibles** menu → Original Parallel Bible (area: Bible), or **Parallel Bibles** menu (area: Tool).
- [Quick Search](../basics/quick_search.md): type `OPB`, or `OPB:::John 3:16` style references.

## Features

- Same [selectors](../integrations/bible_selectors.md), [three-dot menu](../integrations/three_dot_menu.md) (💡 icons for Book/Chapter/Verse Tools) and [verse popup](../integrations/verse_menu.md) as other Bibles.
- Original words are interactive: hover over (or tap) any Hebrew or Greek word to open a [popup window](../integrations/word_tooltips.md) showing its **manuscript form** (with transliteration, pronunciation, and an inline **manuscript-form audio player**), **lemma form** (with an inline **lemma-form audio player**), **morphology**, **interlinear gloss**, and **translation**. Click the manuscript word or lemma inside the popup to open [Lexicons](../search/search_lexicons.md).
- Parallel clause translations (`<trans1>`, `<trans2>`) are dynamically loaded from `~/biblemate/data/clauses/` (and `~/biblemate/data_custom/clauses/` when a valid [custom token](../user_preferences/custom_token.md) is active). Configure OT and NT clause translations separately in [Preferences](../user_preferences/README.md) (`OPB OT Translation 1` default `KJV`, `OPB OT Translation 2` default `NET`, `OPB NT Translation 1` default `KJV`, `OPB NT Translation 2` default `NET`). Tagged translation words support bidirectional hover highlighting with the original text and open word tooltips on hover.
- Hebrew and Greek fonts are bundled for correct display.
- Works with [Sync](../layout/sync.md) and synchronised scrolling.

Data files: `~/biblemate/data/original/OPB.bible` and `~/biblemate/data/clauses/*.clause` ([Data & Resources](../server_setup/data_and_resources.md)). See also [Word Morphology](../tools/tool_morphology.md).

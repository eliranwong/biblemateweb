# Latest Changes (Last 3 Days: 2026-11-22 – 2026-11-24)

Concise summary of features added or updated in the last three days, with their English documentation paths for testing.

## 2026-11-24

1. **Default Tool on Startup & Reset**
   - **Chapter Indexes** is now the default tool on startup and after **Reset All Preferences**.
   - Docs: `docs/english/tools/tool_chapter_indexes.md`, `docs/english/basics/menu_tools.md`

2. **Chapter Indexes Improvements**
   - **Chapter Translation Vocabulary**: Moved to the top and expanded by default for translations (auto-hidden for original-language/interlinear Bibles such as `ORB`, `OLB`, `OPB`, `OIB`, `ODB`, `OHGB`, `OHGBi`, `LXX`, `LXX1`, `LXX1i`, `LXX2`, `LXX2i`). Uses `data_custom/tagged_translations.sqlite` when custom access is enabled and file exists (otherwise `data/tagged_translations.sqlite`), falling back to `NET` (`eng`), `CUV` (`tc`), or `CUVs` (`sc`), with **Hide common words**, verse/lemma tooltips, and click-to-search in **Verses**.
   - **Chapter Vocabulary & Rare Words**: Moved from Morphology into Chapter Indexes (expanded by default for original-language Bibles).
   - **Clickable People & Locations Chips**: **Bible People** and **Bible Locations** render as deduplicated clickable chips; **Bible Topics**, **Bible Dictionaries**, and **Bible Encyclopedia** entries are grouped by module (`HIT`, `NAV`, `TCR`, etc.) and deduplicated.
   - **Chapter Tools Quick Launch**: Bottom buttons to open **Chapter Summary**, **Chapter Map**, **Bible Podcast**, **Bible Audio**, **Verse Indexes**, **Book Indexes**, and **Notes** in the next tab.
   - Docs: `docs/english/tools/tool_chapter_indexes.md`, `docs/english/tools/tool_morphology.md`

3. **Book Indexes (New Tool)**
   - Whole-book study dashboard with book-only selector, **Book Translation Vocabulary**, **Book Vocabulary & Rare Words**, **People Relationship Graph**, **Book Map**, **Bible People**, **Bible Locations**, **Bible Topics**, **Export Study Sheet**, and **Book Tools** quick-launch buttons.
   - Docs: `docs/english/tools/tool_book_indexes.md`, `docs/english/basics/menu_tools.md`

4. **Verse Indexes Improvements**
   - Clickable chips for **Bible People** and **Bible Locations**, plus bottom **Verse Tools** quick-launch buttons (**Cross-references**, **Treasury**, **AI Commentary**, **Commentaries**, **Morphology**, **Comparison**, **Bible Audio**, **Chapter Indexes**, and **Notes**).
   - Docs: `docs/english/tools/tool_indexes.md`

5. **Search Bible Verses Improvements**
   - **Export Verses & Export Table**: Exports visible/filtered verses (preferring `VersesPlain` when available, otherwise `Verses`), plus **Export Table** for grouped Excel (`.xlsx`) comparison tables.
   - **Highlight Differences**: Toggle word-level diff highlighting when viewing multiple translations for the same verse(s).
   - **Distribution Analysis**: Added **OT | NT** totals and on-demand book loading when clicking books beyond `verses_limit` (unloaded books appear in lighter blue).
   - Docs: `docs/english/search/search_bible_verses.md`

6. **Customizable Verse Comparison & Compare Chapter**
   - Added **Verse Comparison** (`Default` / `Custom` with multi-select versions) under `Preferences` → `Frequently Used Resources`.
   - Added **Compare Chapter** to the chapter context menu.
   - Docs: `docs/english/user_preferences/verse_comparison.md`, `docs/english/integrations/chapter_menu.md`

7. **Cross-References, Treasury & Commentaries**
   - **Cross-References**: Added **OT | NT** totals in Distribution Analysis and **Export Cross-References** (filtered results, `VersesPlain` support).
   - **Treasury**: Added **Open References in Verses** and **Export Treasury**.
   - **Commentaries**: Added quick-switch commentary chips (**AI Commentary**, `CBSC`, `BKC`, `JFB`, `MHC`) and **Copy** / **Export Commentary**.
   - Docs: `docs/english/tools/tool_xrefs.md`, `docs/english/tools/tool_treasury.md`, `docs/english/tools/tool_commentary.md`

8. **Bookmarks, Color-Coded Highlights & Reading History**
   - Added **Bookmark Chapter**, **Add to Notepad**, **Bookmark Verse**, and **Highlight** (`Key Verse`, `Promise`, `Doctrine`, `Prayer` with light & dark mode palettes) in the chapter/verse menus, plus a 3-tab **Bookmarks & History** dialog under `Tools` → `Bookmarks`.
   - Docs: `docs/english/integrations/chapter_menu.md`, `docs/english/integrations/verse_menu.md`, `docs/english/basics/menu_tools.md`

9. **Bible Reading Plan (New Tool)**
   - 365-day **Bible Reading Plan** (`Tools` → `Bible Reading Plan`) with localized references in English, Traditional Chinese, and Simplified Chinese, **Read** / **Read All in Verses**, streak & progress tracking, and a **365-Day Overview** grid.
   - Docs: `docs/english/tools/tool_reading_plan.md`, `docs/english/basics/menu_tools.md`

10. **Bible Maps Pin Tooltips & Sanitized Popups**
    - Added hover tooltips displaying location names on pins and sanitized map popups.
    - Docs: `docs/english/search/search_bible_maps.md`

11. **Multilingual Search Pages & API**
    - Added multilingual UI support and translations across search pages (`Bible Characters`, `Locations`, `Maps`, `Parallels`, `Promises`, `Topics`, `Dictionaries`, `Encyclopedias`, `Lexicons`) and API responses.
    - Docs: `docs/english/search/README.md`, `docs/english/api/routes.md`

---

## 2026-11-23

12. **Interactive Relationship Graphs & Chapter Map**
    - Added interactive force-directed **People Relationship Graph** (in **Bible Characters** and **Chapter Indexes**) and **Chapter Map** (Leaflet map with location pins).
    - Docs: `docs/english/search/search_bible_relationships.md`, `docs/english/search/search_bible_characters.md`, `docs/english/tools/tool_chapter_indexes.md`

13. **Pagination & Distribution Analysis Charts**
    - Added pagination (`Load more`) and uncapped **Distribution Analysis** book/chapter bar charts (click-to-filter + morphology breakdown) in **Search Bible Verses** and **Cross-References**.
    - Docs: `docs/english/search/search_bible_verses.md`, `docs/english/tools/tool_xrefs.md`

14. **Hover Tooltip Toggle**
    - Added a toggle option for hover tooltips (`hover_tooltip`) in Settings.
    - Docs: `docs/english/basics/toggle_options.md`

15. **Mutual Word & Clause Highlighting & Interlinear Lexicon Events**
    - Added mouseover/mouseout mutual word and clause highlighting across parallel original-language panes and interlinear lexicon event handling.
    - Docs: `docs/english/bibles/original_interlinear.md`, `docs/english/bibles/original_parallel.md`, `docs/english/bibles/original_linguistic.md`

---

## 2026-11-22

16. **ODB & OPB Translation Preferences**
    - Added user preferences and dynamic loading for **OPB** (`opb_ot_trans1`, `opb_ot_trans2`, `opb_nt_trans1`, `opb_nt_trans2`) and **ODB** (`odb_ot_trans`, `odb_nt_trans`) modules under `Preferences` → `Frequently Used Resources`.
    - Docs: `docs/english/bibles/original_parallel.md`, `docs/english/bibles/original_discourse.md`, `docs/english/user_preferences/opb_ot_trans1.md`, `docs/english/user_preferences/odb_ot_trans.md`

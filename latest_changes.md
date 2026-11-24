# Latest Changes

Summary of features added or updated today (2026-11-24), with their English documentation paths for testing:

1. **Default Tool on Startup & Reset**
   - **Chapter Indexes** is now the default tool on startup and after **Reset All Preferences**.
   - Docs: `docs/english/tools/tool_chapter_indexes.md`, `docs/english/basics/menu_tools.md`

2. **Chapter Indexes Improvements**
   - **Chapter Translation Vocabulary**: Moved to the top and expanded by default for translations (auto-hidden for original-language/interlinear Bibles such as `ORB`, `OLB`, `OPB`, `OIB`, `ODB`, `OHGB`, `OHGBi`, `LXX`, `LXX1`, `LXX1i`, `LXX2`, `LXX2i`). Matches the active Bible against `tagged_translations.sqlite` (`data_custom/tagged_translations.sqlite` when custom access is enabled and file exists; otherwise `data/tagged_translations.sqlite`), falling back to `NET` (`eng`), `CUV` (`tc`), or `CUVs` (`sc`), with **Hide common words**, verse/lemma tooltips, and click-to-search in **Verses**.
   - **Chapter Vocabulary & Rare Words**: Moved from Morphology into Chapter Indexes (expanded by default when an original-language Bible is active).
   - **Grouped & Deduplicated Indexes**: **Bible Topics**, **Bible Dictionaries**, and **Bible Encyclopedia** entries are grouped by module (`HIT`, `NAV`, `TCR`, etc.) and deduplicated as clickable chips.
   - **Chapter Tools Quick Launch**: Bottom buttons to open **Chapter Summary**, **Chapter Map**, **Bible Podcast**, **Bible Audio**, **Verse Indexes**, **Book Indexes**, and **Notes** in the next tab.
   - Docs: `docs/english/tools/tool_chapter_indexes.md`, `docs/english/tools/tool_morphology.md`

3. **Book Indexes (New Tool)**
   - Whole-book study dashboard with book-only selector, **Book Translation Vocabulary**, **Book Vocabulary & Rare Words**, **People Relationship Graph**, **Book Map**, **Bible People**, **Bible Locations**, **Bible Topics**, **Export Study Sheet**, and **Book Tools** quick-launch buttons.
   - Docs: `docs/english/tools/tool_book_indexes.md`, `docs/english/basics/menu_tools.md`

4. **Verse Indexes Quick Launch**
   - Added **Verse Tools** buttons at the bottom (**Cross-references**, **Treasury**, **AI Commentary**, **Commentaries**, **Morphology**, **Comparison**, **Bible Audio**, **Chapter Indexes**, and **Notes**) opening in the next tab.
   - Docs: `docs/english/tools/tool_indexes.md`

5. **Search Bible Verses Improvements**
   - **Export Verses & Export Table**: Exports visible/filtered verses (preferring `VersesPlain` when available, otherwise `Verses`), plus **Export Table** for grouped Markdown comparison tables when multiple translations are shown.
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
   - Added a 365-day **Bible Reading Plan** (`Tools` → `Bible Reading Plan`) with localized references in English, Traditional Chinese, and Simplified Chinese, **Read** / **Read All in Verses**, streak & progress tracking, and a **365-Day Overview** grid.
   - Docs: `docs/english/tools/tool_reading_plan.md`, `docs/english/basics/menu_tools.md`

10. **Bible Maps Pin Tooltips**
    - Added hover tooltips displaying location names on pins in **Bible Maps**.
    - Docs: `docs/english/search/search_bible_maps.md`

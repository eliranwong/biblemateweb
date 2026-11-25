# Compare Chapter

The **Compare Chapter** tool displays a Bible chapter side by side across multiple translations in a multi-column comparison table.

## How to Open

- **Chapter Tools menu**: Right-click a chapter title (or open the three-dot menu → `Chapter Tools`) and select `👀 Compare Chapter`.
- **Quick Search**: `comparechapter` (or `comparechapter:::KJV,NET,CUV` to pre-select versions).

## Features

- **Chapter Navigation**: Select any book and chapter with `Go`, or step through chapters using `◀️ Prev Chapter` and `Next Chapter ▶️`.
- **Multi-Version Selection**: Add, remove, or clear Bible versions at any time using the chip selector. When opened from a specific Bible version, that version is placed in the first column ahead of your configured comparison versions (see [Chapter Comparison Preferences](../user_preferences/chapter_comparison.md)).
- **Verse-by-Verse Toggle**:
  - **Off (default)**: Displays one row with one column per version, drawing from the `Bible` table (or falling back to `Verses` when a module has no `Bible` table).
  - **On**: Displays one row per verse across the union of verse numbers in `Verses`. If a version omits a verse, its cell is left empty while other versions still appear.
  - Your toggle choice is saved in `compare_chapter_verse_by_verse` for future sessions.
- **Diff Toggle** *(when Verse-by-Verse is on)*: Highlights word-level differences in columns 2+ relative to the first column (`compare_chapter_diff`).
- **Mutual Highlighting & Links**: Hovering over tagged words (`heb`, `grk`, `en`, `zh`) highlights corresponding words across columns, and Strong's numbers, study notes, cross-references, and verse highlights remain interactive.
- **DOCX Export**: Click `📥 DOCX` to export the current chapter comparison table as a Word (`.docx`) document.

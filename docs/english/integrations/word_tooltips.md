# Word Tooltips & Lexicon Links

Words in original-language Bibles and annotated texts open an interactive popup window when you hover over (or tap) them.

## How the Popup Works

- **Trigger:** When **Tooltip** is **On** (default) in the [Settings menu](../layout/settings_menu.md), hovering over a marked word opens the popup after a brief delay (`100 ms`). When **Tooltip** is **Off**, hover triggers are disabled and the popup opens only when you **click** a word (clicking the same word again or clicking outside dismisses it).
- **Stay open for audio & links:** Moving your cursor into the popup keeps it open so you can play the audio or click links inside it; it closes `300 ms` after your cursor leaves both the word and the popup.
- **Smart positioning:** Automatically places itself above, below, to the right, or to the left of the word based on available screen space, and repositions on scroll or window resize.
- **On-demand & cached:** Data is fetched from `GET /api/tooltip/{word}` and cached in the browser for instant repeat lookups.

## Three Types of Popups

### 1. Original-Language Word Popup (Hebrew & Greek)

In the [Original-Language Bibles](../bibles/README.md) (`ORB`, `OIB`, `OPB`, `ODB`, `OLB`), every Hebrew/Aramaic (Old Testament) and Greek (New Testament) word has a rich morphology and audio popup:

| Element | Description |
|---|---|
| **Manuscript form** | The exact inflected word as it appears in the text. **Click it** to search **Verses** for occurrences matching both its `E...`/`G...` lexical entry and all of its morphology tags. |
| **Transliteration & Pronunciation** | Shown next to the manuscript form (`word \| transliteration \| pronunciation`). |
| **Manuscript form audio** | An inline audio player (`<audio controls>`) for the pronunciation of the **manuscript (inflected) form** of the word. |
| **Lemma form** | The dictionary / root form of the word. **Click it** to search **Verses** for all occurrences matching its `E...`/`G...` lexical entry across all morphology forms. |
| **Lemma form audio** | A second inline audio player for the pronunciation of the **lemma (dictionary) form** of the word. |
| **Morphology** | Grammatical analysis tags (e.g., part of speech, tense, voice, mood, case, gender, number, person, stem). |
| **Interlinear gloss** | Word-for-word interlinear rendering. |
| **Translation** | Contextual translation of the word. |
| **Lexical & Lexicon Links** | Displayed at the bottom of the popup: `LexicalEntry` links (`E...`, and `H...`/`G...` if not duplicated in `eStrongContextSpecific`), `eStrongContextSpecific` links (when present), and direct mapping links to **BDAG**, **LSJ**, **HALOT**, **CHALOT**, and **BDBE** when those lexicons are available to the user. **Click any link** to open that entry in [Lexicons](../search/search_lexicons.md). |

#### Word-Level Audio Details

Both the manuscript form audio and the lemma form audio play directly inside the popup without leaving the page:

- **Old Testament (Hebrew / Aramaic — BHS5):** served from `/bhs5_audio/{book}_{chapter}/BHS5_{book}_{chapter}_{verse}_{wordID}.mp3` (manuscript form) and `lex_BHS5_{book}_{chapter}_{verse}_{wordID}.mp3` (lemma form).
- **New Testament (Greek — OGNT):** served from `/ognt_audio/{book}_{chapter}/OGNT_{book}_{chapter}_{verse}_{wordID}.mp3` (manuscript form) and `lex_OGNT_{book}_{chapter}_{verse}_{wordID}.mp3` (lemma form).

> [!NOTE]
> Word-level audio requires the `BHS5` and `OGNT` audio files in `~/biblemate/data/audio/bibles/` (see [Data & Resources](../server_setup/data_and_resources.md)).

### 2. Lexical Popup (Strong's Numbers)

In translation Bibles with Strong's tagging, hovering over a Strong's number (`H...` or `G...`) shows:

- A clickable header (`[Lexicon] Strong's ID`) that opens the full entry in [Lexicons](../search/search_lexicons.md).
- The lexicon definition from your configured [Hebrew Lexicon](../user_preferences/hebrew_lexicon.md) or [Greek Lexicon](../user_preferences/greek_lexicon.md).
- Clickable cross-references and lexicon links inside the definition.

### 3. Bible Note Popup

Hovering over a translation note marker shows the note text with clickable Bible verse references.

## Click-Through to Morphology Search & Lexicons

- **Morphology Search:** In an original-language word popup, clicking the **manuscript word** opens [Verses](../search/search_bible_verses.md) with a combined `E...`/`G...` lexical entry + morphology tag query (matching that exact inflected form), while clicking the **lemma** searches [Verses](../search/search_bible_verses.md) for all morphology forms of that lexical entry (`<entry>|%`).
- **Lexicons:** Clicking any `LexicalEntry`, `eStrongContextSpecific`, or Strong's link opens [Lexicons](../search/search_lexicons.md) in the Tool Area using your preferred Hebrew, Greek, or Morphology lexicon. Clicking a **BDAG**, **LSJ**, **HALOT**, **CHALOT**, or **BDBE** mapping link opens that specific lexicon directly on the target entry.

> [!TIP]
> **Why Tagged Bibles Shine in BibleMate Web:** Using Strong's- or morphology-tagged Bible translations lets you **parallel-highlight corresponding words** both across different translations and between translations and the original Hebrew/Greek text (`ORB`, `OIB`, `OPB`, `ODB`, `OLB`) when reading side by side in [Parallel Bibles](../layout/parallel_bibles.md), while also letting you **look up Hebrew and Greek lexicons directly** from the word tooltip.

## Mutual Word & Clause Highlighting

In both **tagged translation Bibles** and the [Original-Language Bibles](original_language_bibles.md) (`ORB`, `OIB`, `OPB`, `ODB`, `OLB`), hovering over a tagged word highlights related elements across all open Bible panes (for example, when comparing two tagged translations, a translation alongside `OIB`/`OPB`, or `OPB` and `OLB` side by side in [Parallel Bibles](../layout/parallel_bibles.md)):

1. **Clause highlight (`.c<cl>`):** Highlights all words belonging to the same grammatical clause (`PAPAYAWHIP` in light mode; `#d48f28` in dark mode).
2. **Mutual lexical highlight (`.G<sn>`):** Highlights every occurrence of the same lexical / Strong's entry across all open panes (`#E7EDFF` in light mode; `#5d85fc` in dark mode).
3. **Focal word highlight (`#w<id>`):** Highlights the hovered word (`#C9CFFF` in light mode; `#5a64b0` in dark mode).

Moving the cursor away clears all three highlight layers. Because clause and lexical highlighting query the entire document (`document.querySelectorAll`), hovering a word in one pane immediately highlights corresponding words and clauses in the parallel pane.

## Programmatic Access

Tooltip data is served by `GET /api/tooltip/{word}` — see [REST API](rest_api.md).

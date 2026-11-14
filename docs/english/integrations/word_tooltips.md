# Word Tooltips & Lexicon Links

Words in original-language Bibles and annotated texts open an interactive popup window when you hover over (or tap) them.

## How the Popup Works

- **Trigger:** Hovering over a marked word opens the popup after a brief delay (`100 ms`).
- **Stay open for audio & links:** Moving your cursor into the popup keeps it open so you can play the audio or click links inside it; it closes `300 ms` after your cursor leaves both the word and the popup.
- **Smart positioning:** Automatically places itself above, below, to the right, or to the left of the word based on available screen space, and repositions on scroll or window resize.
- **On-demand & cached:** Data is fetched from `GET /api/tooltip/{word}` and cached in the browser for instant repeat lookups.

## Three Types of Popups

### 1. Original-Language Word Popup (Hebrew & Greek)

In the [Original-Language Bibles](../bibles/README.md) (`ORB`, `OIB`, `OPB`, `ODB`, `OLB`), every Hebrew/Aramaic (Old Testament) and Greek (New Testament) word has a rich morphology and audio popup:

| Element | Description |
|---|---|
| **Manuscript form** | The exact inflected word as it appears in the text. **Click it** to open its lexicon entry in the Tool Area. |
| **Transliteration & Pronunciation** | Shown next to the manuscript form (`word \| transliteration \| pronunciation`). |
| **Manuscript form audio** | An inline audio player (`<audio controls>`) for the pronunciation of the **manuscript (inflected) form** of the word. |
| **Lemma form** | The dictionary / root form of the word. **Click it** to open the lemma's lexicon entry in the Tool Area. |
| **Lemma form audio** | A second inline audio player for the pronunciation of the **lemma (dictionary) form** of the word. |
| **Morphology** | Grammatical analysis tags (e.g., part of speech, tense, voice, mood, case, gender, number, person, stem). |
| **Interlinear gloss** | Word-for-word interlinear rendering. |
| **Translation** | Contextual translation of the word. |

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

## Click-Through to Lexicons

Clicking a Hebrew/Greek manuscript word, lemma, or Strong's link opens [Lexicons](../search/search_lexicons.md) in the Tool Area with that entry as the query, using your preferred Hebrew or Greek lexicon.

## Programmatic Access

Tooltip data is served by `GET /api/tooltip/{word}` — see [REST API](rest_api.md).

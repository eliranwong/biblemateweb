# Data & Resources

Resources live outside the package, in `~/biblemate/`.

| Path | Contents |
|---|---|
| `~/biblemate/biblemateweb.config` | Server [configuration](configuration.md) |
| `~/biblemate/data/bibles/` | Bible texts (`.bible`, SQLite) |
| `~/biblemate/data/original/` | Original-language Bibles (ORB, OIB, OPB, ODB, OLB) |
| `~/biblemate/data/clauses/` | Clause translation modules for OPB (`.clause`, SQLite) |
| `~/biblemate/data/commentaries/` | Commentaries (`.commentary`) |
| `~/biblemate/data/lexicons/` | Lexicons (`.lexicon`) |
| `~/biblemate/data/audio/bibles/` | Bible chapter audio, plus word-level `BHS5/default` and `OGNT/default` audio (manuscript & `lex_` lemma MP3s) |
| `~/biblemate/data/morphology.sqlite` | Hebrew and Greek word morphology, transliteration, pronunciation, glosses and translations |
| `~/biblemate/data/vectors/bible.db` | Embeddings for semantic search |
| `~/biblemate/data_custom/` | [Custom resources](../integrations/custom_resources.md) (Bibles, books, clauses) – need the custom token |

Download or update with `biblematedata`. Resource lists in the app (Bibles menu, Preferences, [API `.resources`](../api/api_query.md)) are built from what is found in these folders.

Static reference data bundled with the package (events, locations, timelines, names, lexical data) is under `package/biblemateweb/data`.

Fonts for Hebrew and Greek (Ezra SIL, KoineGreek) are bundled for correct display.

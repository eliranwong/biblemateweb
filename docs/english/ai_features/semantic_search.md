# Semantic Search

Search by meaning. An embedding model compares your words with stored vectors and returns the closest matches, even when the wording is different. It uses Ollama (`paraphrase-multilingual`), not the Chat, Partner or Agent backends.

## Verse search

**Search** menu → `Verses`, then choose **Semantic** (beside Literal and Regex).

Type a phrase or idea, such as `God's forgiveness` or `trusting in difficult times`, and press Enter. Results are the closest verses, up to **Similar Verses** (default 20, range 5–100) under `Preferences` → `Semantic Searches`.

You can limit the books and the Bible versions on that page. Quick Search uses the same mode for free text when Semantic is selected.

API: `semantic:::{bibles_books}*:::{search_string}` — for example `semantic:::love of God` or `semantic:::KJV:::Jesus love`. See [API Query](../api/api_query.md).

Vectors: `~/biblemate/data/vectors/bible.db`.

Verse-search guide: [Bible Verse Search](../search/search_bible_verses.md).

## Other searches

These look up an exact entry first. If none matches, they search by meaning and return the closest entries, up to **Similar Entries** (default 5, range 3–30):

| Search | Vector data |
|---|---|
| Topics, Characters, Locations, Names | `~/biblemate/data/vectors/exlb.db` |
| Parallels, Promises | `~/biblemate/data/vectors/collection.db` |
| Dictionaries | `~/biblemate/data/vectors/dictionary.db` |
| Encyclopedias | `~/biblemate/data/vectors/encyclopedia.db` |

Maps, relationships and lexicons do not use this fallback.

## Setup

Ollama must be running with the embedding model, and the vector databases must be present. [Semantic Search Setup](../server_setup/semantic_search_setup.md).

Literal and regex verse search still work without it.

Preferences: [Similar Verses](../user_preferences/top_similar_verses.md), [Similar Entries](../user_preferences/top_similar_entries.md), [Search Mode](../user_preferences/search_mode.md).

# BibleMateDesktop — Comprehensive Architecture & Implementation Plan (Option A: Go + Wails)

> **Target Repository**: Separate standalone repository (`BibleMateDesktop` / `biblematedesktop`)
> **Architecture**: **Go (Wails v2/v3)** Backend + **Vue 3 + Quasar + TypeScript** Frontend
> **Data Source**: Direct, zero-migration reuse of `~/biblemate/data/` and `~/biblemate/data_custom/` SQLite databases, vector DBs, and audio/media assets
> **Target Binaries**: **Windows** (`amd64`, `arm64`), **macOS** (`universal` — Apple Silicon `arm64` + Intel `amd64`), and **Linux** (`amd64`, `arm64` `.AppImage`, `.deb`, `.rpm`)

---

## 1. Executive Summary & Goals

**BibleMateDesktop** will be a high-performance, native desktop application built in **Go** with **Wails** and **Vue 3 + Quasar**. It will preserve **100% feature parity** with `biblemateweb` while delivering significant desktop-first enhancements in speed, offline reliability, multi-window ergonomics, and single-binary distribution:

1. **Zero Database Migration**: Directly reads all existing SQLite databases and files in `~/biblemate/data/` and `~/biblemate/data_custom/` without altering a single byte.
2. **Sub-2ms UI Latency**: Eliminates Python/NiceGUI WebSocket round-trips. Frontend components invoke Go methods directly via Wails IPC bindings in memory.
3. **Why Vue 3 + Quasar Frontend**: Because NiceGUI is built on Vue 3 and Quasar under the hood, choosing Vue 3 + Quasar allows near-1:1 porting of all existing layouts, Quasar props, CSS (`css/original.py`, `css/tooltip.py`), and custom JavaScript (`js/bible.py`, `js/original.py`, `js/tooltip.py`, `js/sync_scrolling.py`).
4. **Desktop-Exclusive Enhancements**:
   - **Multi-Window & Undocking**: Detach any Tool tab, AI Chat, or Bible comparison pane into a secondary window for multi-monitor setups.
   - **Local-First Notes + Cloud Sync**: Save verse/chapter/book notes and Notepad entries directly as local Markdown/JSON files in `~/biblemate/notes/` (Obsidian-compatible) while retaining optional Google Drive AppData sync.
   - **Global OS Hotkeys & System Tray**: Quick verse lookup popup from anywhere in the OS (e.g., `Ctrl+Shift+B` / `Cmd+Shift+B`).
   - **Zero-Dependency Native Export**: Built-in pure-Go `.txt`, `.md`, `.docx`, `.xlsx`, and `.pdf` exporters (no external `pandoc` binary required).

---

## 2. Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Desktop Shell & IPC** | **Wails v2** (ready for v3) | Uses native OS WebView (WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux). Produces ~12–18 MB single binaries vs. 200MB+ Electron/PyInstaller bundles. |
| **Backend Language** | **Go 1.23+** | Blazing fast concurrency, instant startup, static typing, effortless cross-compilation. |
| **SQLite Engine** | `modernc.org/sqlite` (or `mattn/go-sqlite3`) | Custom SQL scalar function registration (`REGEXP`), concurrent read pools (`PRAGMA journal_mode=WAL; PRAGMA query_only=ON;` for read-only resource DBs). |
| **Vector Search Engine** | Native Go Float32 Cosine Similarity + Matrix Cache | Directly parses `entry_vector` JSON / BLOBs from `~/biblemate/data/vectors/*.db` using Go SIMD/goroutines (replaces `numpy.vstack` with 5–10x lower memory overhead). |
| **Frontend Framework** | **Vue 3 (Composition API) + Vite + TypeScript** | Matches NiceGUI's underlying reactive model while providing full client-side speed. |
| **UI Component Library** | **Quasar Framework v2** + **Tailwind CSS** | 1:1 visual parity with NiceGUI's `q-splitter`, `q-tabs`, `q-scroll-area`, `q-select`, `q-dialog`, `q-expansion-item`, and Material Icons. |
| **Document Export** | `excelize/v2` (XLSX), pure-Go Markdown-to-DOCX | Replaces `openpyxl` and `pypandoc` without requiring external binaries. |
| **AI & MCP Engine** | Native Go Multi-Provider LLM Client + Optional `agentmake` / CLI Subprocess Bridge | Native Go streaming for OpenAI, Anthropic, Gemini, Ollama, Groq, xAI, DeepSeek, Mistral, Cohere, VertexAI, Azure + full support for Agentic Workspace CLI backends (`agy`, `claude`, `codex`, `grok`). |

---

## 3. Complete Repository Structure (`biblematedesktop`)

```text
biblematedesktop/
├── main.go                          # Wails application entry point, custom asset/media middleware, tray, menus
├── app.go                           # Core App struct bound to Wails frontend
├── wails.json                       # Wails project configuration & build metadata
├── go.mod
├── go.sum
├── build/                           # OS packaging assets
│   ├── appicon.png                  # High-res 1024x1024 icon
│   ├── windows/                     # Windows .ico, manifest, NSIS installer script
│   ├── darwin/                      # macOS Info.plist, entitlements.plist, DMG layout
│   └── linux/                       # Linux .desktop file, AppImage/deb/rpm configs
├── internal/
│   ├── config/
│   │   ├── config.go                # Reads/writes ~/biblemate/biblematedesktop.json & legacy biblemateweb.config
│   │   ├── defaults.go              # USER_DEFAULT_SETTINGS & HIGHLIGHT_PALETTE
│   │   └── resources.go             # Auto-discovery of ~/biblemate/data & ~/biblemate/data_custom
│   ├── db/
│   │   ├── pool.go                  # Thread-safe SQLite connection manager + custom REGEXP scalar function
│   │   ├── bibles.go                # .bible queries (Bible, Verses, VersesPlain, Details, Notes tables)
│   │   ├── original.go              # ORB, OIB, OPB, ODB, OLB & clauses/*.clause + tagged_translations.sqlite
│   │   ├── morphology.go            # morphology.sqlite queries, word/lexeme parsing, context-specific lexicons
│   │   ├── commentaries.go          # commentaries/*.commentary queries
│   │   ├── lexicons.go              # lexicons/*.lexicon queries & Strong's mapping
│   │   ├── xrefs.go                 # cross-reference.sqlite (xrefs & TSKE treasury)
│   │   ├── collections.go           # collections3.sqlite (Promises, Parallels, Topics)
│   │   ├── indexes.go               # indexes2.sqlite & images.sqlite
│   │   ├── datafiles.go             # data/*.data (biblePeople, book_analysis, chapter_summary, dictionary, encyclopedia, exlb3)
│   │   ├── books.go                 # books/*.book reference books & Timelines
│   │   └── vectors.go               # Vector search over vectors/*.db (bible, collection, dictionary, encyclopedia, exlbl/n/p/t)
│   ├── parser/
│   │   ├── books.go                 # 66 Bible books names, abbreviations (EN, TC, SC), chapter/verse counts
│   │   ├── verse_parser.go          # Go port of BibleVerseParser (extractAllReferences, extractExhaustiveReferences, bcvToVerseReference, parseText)
│   │   └── html_tags.go             # Tooltip tag injection (<heb>, <grk>, <ref>, <vid>, add_bible_word_tooltips, apply_verse_highlights_html)
│   ├── api/
│   │   ├── query_engine.go          # Triple-colon `{keyword}:::{options}:::{query}` parser & router (API_TOOLS)
│   │   └── http_server.go           # Optional local HTTP/REST & MCP server on port 33355 for CLI/external tools
│   ├── ai/
│   │   ├── providers.go             # Unified streaming client (OpenAI, Anthropic, Gemini, Ollama, Groq, xAI, DeepSeek, etc.)
│   │   ├── embeddings.go            # Query embedding generation for semantic vector search
│   │   ├── chat.go                  # Chat Mode (with optional Prompt Engineering & @tool invocation)
│   │   ├── partner.go               # Partner Mode orchestration
│   │   ├── agent.go                 # Autonomous Agent Mode with tool selection loop
│   │   ├── workspace.go             # Agentic Workspace integration (Antigravity, Claude Code, Codex, Grok Build, Gemini API)
│   │   └── mcp_tools/
│   │       ├── tools.go             # 110+ Bible study tool definitions, schemas, and elements
│   │       └── prompts/             # Embedded system_tool_selection_{full,lite,mini,mini_web}.md
│   ├── notes/
│   │   ├── local_store.go           # Local filesystem notes manager (~/biblemate/notes/ & SQLite index)
│   │   └── gdrive_sync.go           # Google OAuth2 loopback flow + Google Drive AppData sync (bible_index.json & B_C_V.json)
│   ├── export/
│   │   ├── txt.go                   # Plain text & Markdown export with watermark
│   │   ├── docx.go                  # Native Go Markdown/HTML to DOCX exporter
│   │   └── xlsx.go                  # Native Go Excel table builder (excelize)
│   ├── staticdata/
│   │   ├── bible_events.go          # Chronology events data
│   │   ├── bible_locations.go       # Coordinates & location metadata (EN, TC, SC)
│   │   ├── bible_names.go           # Bible names metadata
│   │   ├── bible_timelines.go       # Timeline periods & image mappings
│   │   ├── lexical_data.go          # Strong's number to lexeme/gloss lookup map
│   │   └── readings.go              # Reading plans data
│   └── i18n/
│       └── translations.go          # English (eng), Traditional Chinese (tc), Simplified Chinese (sc) dictionaries
└── frontend/                        # Vue 3 + Quasar + TypeScript application
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.ts
        ├── App.vue
        ├── assets/
        │   ├── fonts/               # Embedded KoineGreek.ttf, sileot.ttf, sileotsr.ttf (Ezra SIL)
        │   └── css/                 # original.css, tooltip.css, theme variables
        ├── stores/
        │   ├── settingsStore.ts     # Persistent user settings synced with Go config
        │   ├── workspaceStore.ts    # Area 1 & Area 2 tabs, split panes, layout mode (1/2/3), history, bookmarks
        │   └── highlightStore.ts    # Verse highlight colors (yellow, green, blue, pink)
        ├── composables/
        │   ├── useSyncScroll.ts     # Port of js/sync_scrolling.py
        │   ├── useTooltip.ts        # Port of js/tooltip.py (instant Wails IPC lookup + audio playback)
        │   ├── useOriginalHighlight.ts # Port of js/original.py (interactive clause/word hover highlighting)
        │   └── useBibleEvents.ts    # Global event bus for bcv(), lex(), wd(), morph(), cr(), bn(), luV()
        ├── components/
        │   ├── layout/
        │   │   ├── AppHeader.vue
        │   │   ├── LeftDrawer.vue
        │   │   ├── DualAreaSplitter.vue
        │   │   ├── ClosableTabBar.vue
        │   │   └── FloatingActionButtons.vue # Draggable layout swap & quick Bible selector buttons
        │   ├── common/
        │   │   ├── BibleSelector.vue         # Dynamic Version / Book / Chapter / Verse dropdowns
        │   │   ├── VerseContextMenu.vue      # Book, Chapter, and Verse study context menus
        │   │   ├── TooltipPopup.vue          # Smart viewport-aware tooltip with BHS5/OGNT word audio
        │   │   ├── ReviewDialog.vue
        │   │   ├── SelectionDialog.vue
        │   │   └── BibleSelectionDialog.vue
        │   ├── bibles/                       # Area 1 & Area 2 Bible Readers
        │   │   ├── BibleTranslation.vue
        │   │   ├── OriginalReader.vue        # ORB
        │   │   ├── OriginalInterlinear.vue   # OIB
        │   │   ├── OriginalParallel.vue      # OPB
        │   │   ├── OriginalDiscourse.vue     # ODB (with dynamic <trans> injection)
        │   │   └── OriginalLinguistic.vue    # OLB
        │   ├── tools/                        # Study Tools
        │   │   ├── CommentaryTool.vue
        │   │   ├── MorphologyTool.vue
        │   │   ├── CrossReferencesTool.vue
        │   │   ├── TreasuryTool.vue
        │   │   ├── CompareChapterTool.vue    # Side-by-side & verse-by-verse diff modes
        │   │   ├── MultiTool.vue             # Configurable multi-column preset grid
        │   │   ├── AudioBibleTool.vue
        │   │   ├── PodcastTool.vue
        │   │   ├── ChronologyTool.vue
        │   │   ├── TimelinesTool.vue
        │   │   ├── ReadingPlanTool.vue
        │   │   ├── ReferenceBooksTool.vue
        │   │   ├── IndexesTool.vue           # Resource, Book, and Chapter Indexes
        │   │   ├── SummaryAnalysisTool.vue   # Book Analysis & Chapter Summary
        │   │   ├── PromisesMenuTool.vue
        │   │   ├── ParallelsMenuTool.vue
        │   │   ├── NotesTool.vue             # Verse/Chapter/Book notes (Local + Google Drive)
        │   │   └── NotepadTool.vue
        │   ├── search/                       # Search & Reference Modules
        │   │   ├── VerseSearch.vue           # Literal, Regex, Semantic, and Combined Search + Book/Chapter count charts
        │   │   ├── LexiconSearch.vue
        │   │   ├── DictionarySearch.vue
        │   │   ├── EncyclopediaSearch.vue
        │   │   ├── TopicSearch.vue
        │   │   ├── CharacterSearch.vue
        │   │   ├── LocationSearch.vue
        │   │   ├── NameSearch.vue
        │   │   ├── MapSearch.vue             # Interactive Leaflet/Map view
        │   │   ├── RelationshipSearch.vue    # Interactive Character Relationship Graph
        │   │   ├── PromiseSearch.vue
        │   │   └── ParallelSearch.vue
        │   ├── teachings/
        │   │   └── ParousiaView.vue          # English & Chinese Parousia teaching modules
        │   └── ai/
        │       ├── AiChatView.vue
        │       ├── AiPartnerView.vue
        │       ├── AiAgentView.vue
        │       └── AgenticWorkspaceView.vue
```

---

## 4. Shared Database & Asset Architecture (`~/biblemate/data/`)

`BibleMateDesktop` will use the exact same directory layout as `biblemateweb` (`~/biblemate/data` and `~/biblemate/data_custom`), plus allow users to configure a custom data folder path in Settings (e.g., an external SSD or shared folder).

### 4.1 Complete Database Map
| Data Category | File Pattern in `~/biblemate/data/` (and `data_custom/`) | Tables / Access Logic to Implement in Go |
| :--- | :--- | :--- |
| **Bible Translations** | `bibles/*.bible` (excluding `MOB\|MIB\|MAB\|MTB\|MPB`) | `Details` (`Title`), `Bible` (`Book, Chapter, Scripture`), `Verses` (`Book, Chapter, Verse, Scripture`), `VersesPlain` (fast stripped-tag search), `Notes` (`Book, Chapter, Verse, ID, Note`) |
| **Original Bibles** | `original/{ORB,OIB,OPB,ODB,OLB}.bible`, `bibles/{OHGB,OHGBi}.bible` | Chapter HTML retrieval, dynamic `<trans>` replacement in `ODB.bible` using `clauses/*.clause` (`ASV`, `BSB`, `CUV`, `CUVs`, `KJV`, `LEB`, `NET`, `ULT`, `UST`, `WEB`) |
| **Morphology & Tagged** | `morphology.sqlite`, `tagged_translations.sqlite` | `morphology` table (`WordID, ClauseID, Book, Chapter, Verse, Word, LexicalEntry, MorphologyCode, Morphology, Lexeme, Transliteration, Pronunciation, Interlinear, Translation, Gloss` + `*ContextSpecific` columns: `eStrong`, `BDAG`, `LSJ`, `HALOT`, `CHALOT`, `BDBE`) |
| **Commentaries** | `commentaries/c*.commentary` | `Details` (`Title`), `Commentary` (`Book, Chapter, Scripture`) + verse-level anchor extraction |
| **Lexicons** | `lexicons/*.lexicon` | `Lexicon` (`Topic, Definition`) |
| **Cross-References & TSKE** | `cross-reference.sqlite` | `ScrollMapper` / `CrossReference` & `TSKE` tables by `Book, Chapter, Verse` |
| **Collections** | `collections3.sqlite` | `PROMISES`, `PARALLELS`, and topical collections |
| **Resource Indexes & Images** | `indexes2.sqlite`, `images.sqlite` | Book/chapter/verse resource indexes and embedded biblical map/illustration blobs |
| **Study Data Files** | `data/*.data` (`biblePeople`, `book_analysis[_sc/_tc]`, `chapter_summary[_sc/_tc]`, `dictionary`, `encyclopedia`, `exlb3`) | SQLite tables for characters, relationships, book analysis, chapter summaries, dictionaries (`AMT`, `BBD`, `BMC`, `BUC`, `CBA`, `DRE`, `EAS`, `FAU`, `FOS`, `HBN`, `MOR`, `PMD`, `SBD`, `USS`, `VNT`), encyclopedias (`DAC`, `DCG`, `HAS`, `ISB`, `KIT`, `MSC`), and locations/people/topics |
| **Reference Books** | `books/*.book`, `books/Timelines/*` | Chapter/Topic list & content retrieval (`Chapters` / `Pages` tables); excludes `Bible_Promises.book` and `Harmonies_and_Parallels.book` from generic book menu |
| **Semantic Vector DBs** | `vectors/{bible,collection,dictionary,encyclopedia,exlbl,exlbn,exlbp,exlbt,exlbt_sc,exlbt_tc}.db` | Cosine similarity search over `entry_vector` embeddings with optional Book/OT/NT filter |
| **Audio & Podcasts** | `audio/bibles/{Version}/default/`, `audio/bibles/{BHS5,OGNT}/default/`, `podcast/` | Local media streaming via Wails custom asset handler (`/media/bhs5_audio/...`, `/media/ognt_audio/...`, `/media/audio/...`, `/media/podcast/...`) |

### 4.2 High-Performance Go SQLite Layer
- **Connection Pooling**: Open SQLite databases with `mode=ro&_journal_mode=WAL&_busy_timeout=5000` for all reference resources so multiple goroutines can run searches concurrently across 10+ Bible versions in parallel.
- **Custom `REGEXP` Scalar Function**: Register Go's `regexp.Regexp` (with LRU cache for compiled regexes and case-sensitivity toggle) as the SQLite `REGEXP` function on every connection.
- **Automatic `VersesPlain` Optimization**: Just like `fx/bible.py`, automatically detect if `VersesPlain` exists in a `.bible` file, run `LIKE` / `REGEXP` against `VersesPlain` first, and fetch the rich HTML from `Verses` for matching `(Book, Chapter, Verse)` tuples.

---

## 5. Phased Implementation Plan

When you ask me to execute this plan, I will follow these 8 structured phases in order:

### Phase 1: Repository Scaffolding & Wails Core Foundation
1. Initialize the new repository (`biblematedesktop`) with **Wails v2 (`wails init -n BibleMateDesktop -t vue-ts`)** and configure **Quasar v2 + Tailwind CSS**.
2. Implement `internal/config`:
   - Load `~/biblemate/biblemateweb.config` for backward compatibility and store desktop settings in `~/biblemate/biblematedesktop.json`.
   - Implement `internal/config/resources.go` to scan `~/biblemate/data` and `~/biblemate/data_custom` (Bibles, Clauses, Commentaries, Lexicons, Books, Audio, Podcasts).
   - Provide a first-launch setup wizard if `~/biblemate/data` is empty (capable of downloading/extracting `biblematedata` directly inside the desktop app without needing Python/pip).
3. Configure Wails custom HTTP AssetServer middleware to serve:
   - Bundled fonts (`KoineGreek.ttf`, `sileot.ttf`, `sileotsr.ttf`)
   - Local audio files (`/bhs5_audio/`, `/ognt_audio/`, `/audio/`, `/podcast/`)
   - Timeline images (`/timelines/`) and `images.sqlite` blobs.
4. Port `translations/eng.py`, `translations/tc.py`, and `translations/sc.py` into `internal/i18n` and expose reactive i18n to Vue.

### Phase 2: Go Bible Engine, Verse Parser & SQLite Data Layer
1. Port `BibleBooks` and `BibleVerseParser` from Python (`agentmake.plugins.uba.lib`) to pure Go (`internal/parser/verse_parser.go`):
   - Support English, Traditional Chinese, and Simplified Chinese book names and abbreviations.
   - Implement `ExtractAllReferences`, `ExtractExhaustiveReferences`, `BcvToVerseReference`, and `ParseText` (auto-tagging plain text verse references into clickable `<ref onclick="bcv(b,c,v)">`).
2. Port `internal/staticdata` (`lexical_data`, `bible_events`, `bible_locations` EN/TC/SC, `bible_names`, `bible_timelines`, `cr_books`, `readings`).
3. Implement `internal/db/bibles.go` & `internal/parser/html_tags.go`:
   - `GetBibleChapter`, `GetBibleChapterVerses`, `GetBibleBookList`, `GetBibleChapterList`, `GetBibleVerseList`.
   - `GetBibleContent` supporting Reference lookup, Literal (`LIKE`), Regex (`REGEXP`), and Semantic Vector Search (`vectors/bible.db`), including `book_counts` and `chapter_counts` aggregation.
   - `AddBibleWordTooltips` (converting `<heb>`, `<grk>`, `<en>`, `<zh>`, `bn(...)`, `lex(...)` into `.tooltip-word` elements with `data-word` attributes and RTL wrapping).
   - `ApplyVerseHighlightsHTML` (applying `yellow`, `green`, `blue`, `pink` light/dark theme palettes).
4. Implement `internal/db/tooltips.go`:
   - `GetTooltipData(word)` handling `bn,...` (Bible study notes from `.bible` `Notes` table), `wh[0-9]+` / `w[0-9]+` (`morphology.sqlite` with BHS5/OGNT word & lexeme audio and context-specific lexicon links `BDAG`, `LSJ`, `HALOT`, `CHALOT`, `BDBE`), and `H[0-9]+` / `G[0-9]+` (user's preferred Hebrew/Greek lexicon).

### Phase 3: Dual-Area Workspace Shell & Core Frontend UX
1. Build the main desktop workspace (`DualAreaSplitter.vue`, `ClosableTabBar.vue`, `LeftDrawer.vue`):
   - **Area 1 (Bible Area)** & **Area 2 (Tool Area)** with dynamic closable tabs (`tab1_1..N`, `tab2_1..N`) persisted automatically.
   - Responsive splitter (horizontal split in landscape, vertical split in portrait) and Layout Modes: `1` (Bible only), `2` (Split Both), `3` (Tools only).
   - Draggable floating buttons (`FloatingActionButtons.vue`) for quick layout swapping and quick Bible selector dialog, persisting coordinates.
2. Port client-side interactive behaviors into Vue composables:
   - `useTooltip.ts`: Viewport-aware tooltip positioning with directional arrows, audio playback, hover toggle, and instant Wails IPC lookup (`window.go.main.App.GetTooltipData(word)`).
   - `useSyncScroll.ts`: Debounced bi-directional `<vid id="v{b}.{c}.{v}">` synchronized scrolling between Area 1 and Area 2.
   - `useOriginalHighlight.ts`: Clause and lexical hover highlighting for original language modules.
   - `useBibleEvents.ts`: Global bridge handling `emitEvent('bcv' | 'wd' | 'morph' | 'lex' | 'cr' | 'luV1' | 'luV2' | 'note', args)` from rendered HTML.
3. Build `BibleSelectionDialog.vue` and `BibleSelector.vue` (cascading Version → Book → Chapter → Verse selectors with instant keyboard navigation).

### Phase 4: All 6 Bible Reading Modes (Area 1 & Area 2)
1. **Bible Translation (`BibleTranslation.vue`)**: Standard & tagged translations (`NET`, `KJV`, `CUV`, `OHGBi`, etc.), study note popovers, verse highlighting, bookmarking, reading history, and verse/chapter/book context menus.
2. **Original Reader (`OriginalReader.vue` — `ORB`)**: Hebrew OT & Greek NT reader with word morphology tooltips and audio.
3. **Original Interlinear (`OriginalInterlinear.vue` — `OIB`)**: Multi-layer interlinear display (`OHGBi` / `OIB.bible`).
4. **Original Parallel (`OriginalParallel.vue` — `OPB`)**: Original language alongside configurable OT/NT translations (`opb_ot_trans1/2`, `opb_nt_trans1/2`).
5. **Original Discourse (`OriginalDiscourse.vue` — `ODB`)**: Clause-structured discourse analysis with dynamic `<trans>` injection from `clauses/*.clause` (`odb_ot_trans`, `odb_nt_trans`).
6. **Original Linguistic (`OriginalLinguistic.vue` — `OLB`)**: Linguistic/syntactic breakdown reader.

### Phase 5: Complete Study Tools & Search Modules
1. **Verse & Chapter Comparison**:
   - `CompareChapterTool.vue`: Full chapter comparison across multiple versions, verse-by-verse mode, and word-level diff highlighting (`compare_chapter_diff`).
   - `MultiTool.vue`: Configurable multi-column grid displaying multiple tools (Commentary, Morphology, Xrefs, Treasury, Lexicons) simultaneously for the active chapter/verse with custom presets.
2. **Commentaries, Morphology, Cross-References & Treasury**:
   - `CommentaryTool.vue` (`commentaries/*.commentary` with chapter/verse filter).
   - `MorphologyTool.vue` (`morphology.sqlite` clause/word breakdown + Excel `.xlsx` / `.txt` / `.docx` export).
   - `CrossReferencesTool.vue` & `TreasuryTool.vue` (`cross-reference.sqlite` TSKE & xrefs).
3. **Search Suite (with Semantic Vector Search)**:
   - `VerseSearch.vue`: Literal, Regex, and Semantic (`vectors/bible.db`) search across single or multiple Bibles, Book/OT/NT filters, result highlighting, and interactive Book/Chapter hit distribution charts.
   - `LexiconSearch.vue` (`lexicons/*.lexicon` + `tagged_translations.sqlite` reverse search).
   - `DictionarySearch.vue` (`data/dictionary.data` + `vectors/dictionary.db`).
   - `EncyclopediaSearch.vue` (`data/encyclopedia.data` + `vectors/encyclopedia.db`).
   - `TopicSearch.vue` (`collections3.sqlite` + `data/exlb3.data` + `vectors/exlbt*.db`).
   - `CharacterSearch.vue` & `RelationshipSearch.vue` (`data/biblePeople.data` + `vectors/exlbp.db` + interactive family/relationship graph).
   - `LocationSearch.vue` & `MapSearch.vue` (`data/exlb3.data` + `vectors/exlbl.db` + interactive map pins & distance calculator).
   - `NameSearch.vue` (`vectors/exlbn.db`).
   - `PromiseSearch.vue` & `ParallelSearch.vue` (`collections3.sqlite` + `vectors/collection.db`).
4. **Indexes, Summaries, Books, Chronology, Audio & Teachings**:
   - `IndexesTool.vue`, `ChapterIndexes`, `BookIndexes` (`indexes2.sqlite`, `images.sqlite`).
   - `SummaryAnalysisTool.vue` (`book_analysis*.data`, `chapter_summary*.data`).
   - `ReferenceBooksTool.vue` (`books/*.book`).
   - `ChronologyTool.vue`, `TimelinesTool.vue`, `ReadingPlanTool.vue` (with completion tracking).
   - `AudioBibleTool.vue` & `PodcastTool.vue` (with chapter looping and playlist controls).
   - `ParousiaView.vue` (`parousia.py` and `parousia_zh.py` teaching modules).
5. **Notes & Notepad (Desktop Upgraded)**:
   - `NotesTool.vue` & `NotepadTool.vue`: Store notes locally in `~/biblemate/notes/` (instant offline access) + full two-way sync with Google Drive `appDataFolder` (`bible_index.json` and `{b}_{c}_{v}.json`) via native desktop OAuth2 loopback callback.

### Phase 6: Unified API Query Engine & AI / MCP Integration
1. **Triple-Colon Query Engine (`internal/api/query_engine.go`)**:
   - Implement all `API_TOOLS` keywords (`morphology:::`, `chapter:::`, `comparechapter:::`, `verses:::`, `bible:::`, `search:::`, `literal:::`, `regex:::`, `semantic:::`, `treasury:::`, `tske:::`, `commentary:::`, `chronology:::`, `xrefs:::`, `crossreference:::`, `promises:::`, `parallels:::`, `topics:::`, `locations:::`, `characters:::`, `names:::`, `dictionaries:::`, `encyclopedias:::`, `lexicons:::`).
   - Expose both via direct Wails bindings and an optional toggleable local HTTP API server (`http://localhost:33355/api/...`) so existing `biblemateapi` CLI scripts continue to work seamlessly.
2. **Three AI Modes + Agentic Workspace**:
   - **Chat Mode (`AiChatView.vue`)**: Streaming Markdown responses, `@tool_name` direct invocation across all 110+ tools in `mcp_tools/tools.py`, optional Prompt Engineering expansion (`improve_prompt_2`) with review dialog, edit response in-place, and full conversation download (`.txt` / `.docx`).
   - **Partner Mode (`AiPartnerView.vue`)**: Multi-step collaborative Bible study workflow with tool execution & context injection.
   - **Agent Mode (`AiAgentView.vue`)**: Autonomous multi-step agent loop with automatic tool selection (`system_tool_selection_full.md` / `lite.md` / `mini.md`).
   - **Agentic Workspace (`AgenticWorkspaceView.vue`)**: Support signed-in CLI backends (`Antigravity`, `Claude Code`, `Codex`, `Grok Build`, `Gemini API`) in `~/biblemate/`.
   - **Multi-Provider LLM Support**: Native Go clients for OpenAI, Anthropic, Google Gemini / VertexAI, Ollama (local models), Llama.cpp, Groq, xAI (Grok), DeepSeek, Mistral, Cohere, Azure, and GitHub Models—plus optional delegation to `agentmake` if installed on the system.

### Phase 7: Desktop-Exclusive Enhancements
1. **Multi-Window Support**: Allow any tab in Area 1 or Area 2 to be popped out into a separate native OS window (synchronized with the main window's verse navigation).
2. **Native File Dialogs & Exporters**: Use native OS Save/Open file dialogs (`wails.Runtime.SaveFileDialog`) for `.txt`, `.md`, `.docx`, and `.xlsx` exports instead of browser downloads.
3. **System Tray & Global Shortcut**: Optional system tray icon and global hotkey (`Cmd/Ctrl+Shift+B`) to summon a quick verse lookup / AI bar over any application.
4. **Deep-Link & URL Parameter Parity**: Support `biblemate://?bb=43&bc=3&bv=16&bbt=NET&tool=commentary` custom protocol links on Windows, macOS, and Linux, matching all URL parameters from `biblemateweb` (`bb`, `bc`, `bv`, `bbt`, `tool`, `l`, `pc`, `sc`, `nc`, `fs`, `d`).

### Phase 8: Cross-Platform Packaging & CI/CD (Windows, macOS, Linux)

Yes — building for **Windows, macOS, and Linux** is straightforward with Wails and GitHub Actions!

#### 8.1 Target Binary Matrix
| OS | Architectures | Output Formats | WebView Dependency |
| :--- | :--- | :--- | :--- |
| **Windows** | `amd64` (x64), `arm64` | Standalone `.exe` + **NSIS Installer** (`BibleMateDesktop-Setup.exe`) | Uses Windows 10/11 built-in Microsoft Edge **WebView2** (installer auto-bootstraps if missing) |
| **macOS** | **Universal Binary** (`arm64` Apple Silicon + `amd64` Intel) | `.app` bundle packaged inside a Drag-and-Drop **`.dmg`** | Uses macOS built-in **WKWebView** (zero extra dependencies) |
| **Linux** | `amd64` (x64), `arm64` | Portable **`.AppImage`**, Debian/Ubuntu **`.deb`**, Fedora/RHEL **`.rpm`**, `.tar.gz` | Uses standard system **WebKitGTK** (`libwebkit2gtk-4.1` / `4.0`) |

#### 8.2 Local & Automated Build Commands
Using Pure-Go SQLite (`modernc.org/sqlite`), cross-compiling Go code requires no complex C toolchain for the database layer, and Wails provides built-in packaging flags:

```bash
# 1. macOS Universal Binary (.app + .dmg)
wails build -platform darwin/universal -clean -upx

# 2. Windows Installer & Portable Executable (.exe + NSIS installer)
wails build -platform windows/amd64 -nsis -clean
wails build -platform windows/arm64 -nsis -clean

# 3. Linux Binaries (amd64 & arm64)
wails build -platform linux/amd64 -clean
wails build -platform linux/arm64 -clean
```

#### 8.3 Automated GitHub Actions Release Workflow (`.github/workflows/release.yml`)
We will include a ready-to-use GitHub Actions workflow that runs on tag push (`v*.*.*`) using a matrix of `macos-latest`, `windows-latest`, and `ubuntu-22.04` runners to automatically compile, package, sign (when certificates are provided), and attach all 5 binaries (`.exe` installer, `.dmg`, `.AppImage`, `.deb`, `.tar.gz`) to GitHub Releases.

---

## 6. Verification & Acceptance Checklist

Before marking the future implementation complete, every item below will be verified:
- [ ] All `.bible`, `.clause`, `.commentary`, `.lexicon`, `.book`, `.sqlite`, `.data`, and `vectors/*.db` files in `~/biblemate/data/` load without error.
- [ ] Custom data token (`config.custom_token`) properly unlocks `~/biblemate/data_custom/` modules.
- [ ] All 6 Bible reading modes (`Translation`, `ORB`, `OIB`, `OPB`, `ODB`, `OLB`) render with Ezra SIL (`sileot.ttf`) and KoineGreek (`KoineGreek.ttf`) fonts, RTL Hebrew alignment, interactive hover tooltips, and BHS5/OGNT word/lexeme audio playback.
- [ ] Bi-directional synchronized scrolling between Area 1 and Area 2 works smoothly across chapters.
- [ ] Literal, Regex, and Semantic Vector searches return identical results to `biblemateweb` with < 50ms query times.
- [ ] All 24+ `API_TOOLS` triple-colon queries (`{keyword}:::{options}:::{query}`) return identical Markdown output to `biblemateweb`.
- [ ] Chat Mode, Partner Mode, Agent Mode, and Agentic Workspace stream responses and execute all 110+ MCP Bible study tools.
- [ ] Native `.txt`, `.docx`, and `.xlsx` exports work offline without external `pandoc` dependencies.
- [ ] Local notes (`~/biblemate/notes/`) and Google Drive OAuth2 sync (`bible_index.json`) both read and write verse/chapter/book notes accurately.
- [ ] Production binaries build cleanly for **Windows**, **macOS**, and **Linux**.

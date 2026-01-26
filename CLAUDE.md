# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BibleMate AI Web is a Python web application that provides a unified web interface for Bible study, combining features from BibleMate AI and UniqueBible. It uses NiceGUI framework for the web UI and includes HTTP/API servers.

This repository focuses on the web UI, HTTP and API servers. For CLI version, MCP Server, Agent Mode partner components, and Bible data, see https://github.com/eliranwong/biblemate

## Development Commands

### Setup and Installation

```bash
# Install the package in development mode
pip install --upgrade biblemateweb

# One-time data setup
biblematedata

# Run HTTP & API servers
biblemateweb

# Access the web UI
open http://localhost:33355
```

### API Client

```bash
# Run API client with help
biblemateapi -h
```

### Testing

The `tests/` directory contains various test scripts and prototypes. There is no unified test runner - tests are individual Python scripts demonstrating features.

## Architecture

### Application Structure

**Entry Points:**
- `package/biblemateweb/main.py`: Main application entry point that starts the NiceGUI server
- `package/biblemateweb/__init__.py`: Core initialization, config management, and shared utilities
- `package/biblemateweb/api_client.py`: Command-line API client

**Page Architecture:**
- `pages/home.py`: Core `BibleMateWeb` class that manages the entire UI layout with two main areas (Bible area and Tool area)
- `pages/ai/`: AI integration modules (chat.py, agent.py, partner.py, stream.py)
- `pages/bibles/`: Bible reading modes (original_reader, original_interlinear, bible_translation, etc.)
- `pages/tools/`: Bible study tools (commentary, audio, chronology, indexes, notes, etc.)
- `pages/search/`: Search functionality (bible_verses, topics, locations, characters, etc.)
- `pages/teachings/`: Teaching content (parousia.py, parousia_zh.py)

**Support Modules:**
- `fx/`: Business logic and utilities (bible.py handles Bible data access, tooltips.py for Hebrew/Greek tooltips)
- `api/`: API endpoint handlers (api.py implements the query parser and content retrieval)
- `dialogs/`: Reusable UI dialogs (review_dialog, selection_dialog, filename_dialog)
- `mcp_tools/`: MCP (Model Context Protocol) tool definitions for AI integration
- `js/`: JavaScript injection modules for client-side functionality
- `css/`: CSS styling modules
- `data/`: Static Bible data (events, locations, timelines, names, lexical data)
- `translations/`: UI translations (eng.py, tc.py, sc.py)

### Data Management

**Bible Resources:**
- Bible texts stored as SQLite databases (`.bible` files) in `~/biblemate/data/bibles/`
- Commentaries (`.commentary` files) in `~/biblemate/data/commentaries/`
- Lexicons (`.lexicon` files) in `~/biblemate/data/lexicons/`
- Audio files in `~/biblemate/data/audio/bibles/`
- Custom user resources in `~/biblemate/data_custom/`

**Database Access Pattern:**
- Uses APSW (Another Python SQLite Wrapper) for thread-safe database access
- `getBiblePath()` resolves Bible module abbreviations to file paths
- `getBibleChapterVerses()` fetches verses from SQLite databases
- Vector embeddings for semantic search stored in `~/biblemate/data/vectors/bible.db`

### Configuration System

**Config Files:**
- `~/biblemate/biblemateweb.config`: Server-side configuration (avatar, port, storage_secret, custom_token, Google OAuth, agent/partner mode settings)
- Config loaded at startup via `load_config()` in `__init__.py`
- User preferences stored in NiceGUI's `app.storage.user` (client-side persistent storage)

**Key Config Items:**
- `config.storage_secret`: Required for deployment (generate with `openssl rand -hex 32`)
- `config.custom_token`: Token for accessing custom data sources
- `config.disable_agent_mode` / `config.limit_agent_mode_once_daily`: Control public access to Agent Mode
- `config.port`: HTTP server port (default: 33355)
- `config.verses_limit`: Maximum verses returned in searches (default: 2000)

### API Query System

The API uses a keyword-based query syntax with triple-colon delimiters (`:::`):

```
{keyword}:::{options}:::{query}
```

**Supported Keywords:**
- `morphology:::`: Word morphology in verses
- `chapter:::`: Retrieve Bible chapters
- `comparechapter:::`: Compare chapters across Bibles
- `verses:::`: Retrieve specific verses
- `literal:::`, `regex:::`, `semantic:::`: Bible verse searches
- `commentary:::`, `treasury:::`, `xrefs:::`: Study tools
- `topics:::`, `characters:::`, `locations:::`: Reference materials
- `lexicons:::`, `dictionaries:::`, `encyclopedias:::`: Language resources

See `docs/api_query.md` for complete syntax documentation.

### AI Integration

**Three AI Modes:**
1. **Chat Mode** (`pages/ai/chat.py`): Standard conversational AI with Bible study tools
2. **Partner Mode** (`pages/ai/partner.py`): Enhanced collaboration mode with more context
3. **Agent Mode** (`pages/ai/agent.py`): Autonomous agent with tool selection capabilities

**MCP Tools:**
- Tool definitions in `mcp_tools/tools.py` and `mcp_tools/tools_schema.py`
- Tool elements mapped in `mcp_tools/elements.py`
- System prompts in `mcp_tools/system_tool_selection_*.md`

**Streaming:**
- AI responses streamed using `stream_response()` in `pages/ai/stream.py`
- Uses asyncio for non-blocking UI updates
- Supports tool calling via function schemas

### Tab System

The UI uses a dual-area tab system:
- **Area 1 (Bible area)**: Primary Bible reading tabs
- **Area 2 (Tool area)**: Study tools and AI chat tabs

Tabs are dynamically created and managed by the `BibleMateWeb` class. Each tab stores its state (book, chapter, verse, query) in `app.storage.user`.

### Authentication

Google OAuth integration for Drive-based notes sync:
- OAuth configuration in `main.py` using Authlib
- Routes: `/login` (initiates OAuth), `/auth` (callback)
- Tokens stored in `app.storage.user['google_token']`
- Notes synced to Google Drive AppData folder

## Important Technical Patterns

### URL Parameter Handling

The home page accepts extensive URL parameters for deep linking:
- `bb`, `bc`, `bv`: Bible book, chapter, verse
- `bbt`: Bible text/version
- `tool`: Load specific tool (bible, audio, chronology, search, chat, etc.)
- `l`: Layout mode (1=Bible only, 2=Both, 3=Tools only)
- `pc`, `sc`, `nc`: Primary, secondary, negative colors
- `fs`: Font size percentage
- `d`: Dark mode
- `k`: Keep parameters in history

### Hebrew/Greek Tooltips

Original language tooltips implemented via:
- Custom HTML tags: `<heb>`, `<grk>`, `<kgrk>`, `<wlex>`
- JavaScript event handlers in `js/tooltip.py`
- Tooltip data fetched via `/api/tooltip/{word}` endpoint
- CSS styling in `css/tooltip.py`

### Synchronized Scrolling

Bible area and tool area can synchronize scrolling using custom JavaScript (see `js/sync_scrolling.py`).

### Content Download

Users can download content as TXT or DOCX:
- TXT: Direct text encoding
- DOCX: Uses pypandoc to convert Markdown to Word format
- Watermark automatically added: `get_watermark()`

## Key Dependencies

- **nicegui**: Web UI framework (v3.2.0+)
- **agentmake**: AI agent framework (v1.2.13+)
- **biblemate**: Core Bible study engine (v0.2.63+)
- **biblematedata**: Bible data package (v0.0.2+)
- **apsw**: SQLite wrapper
- **authlib**: OAuth authentication
- **pypandoc**: Document conversion (requires `pandoc` binary)
- **google-api-python-client**: Google Drive integration
- **markdown2**: Markdown to HTML conversion
- **qrcode**, **pillow**: QR code generation

## Python Version

Requires Python 3.10-3.12 (due to fastmcp/agentmake constraints).

## Common Patterns

### Loading Bible Content

```python
from biblemateweb.fx.bible import getBiblePath, get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

parser = BibleVerseParser(False)
verses = get_bible_content(user_input="John 3:16", bible="NET", parser=parser)
```

### Accessing Configuration

```python
from biblemateweb import config

# Server config
config.port
config.custom_token
config.disable_agent_mode

# Available resources
config.bibles  # Dictionary of Bible modules
config.commentaries
config.lexicons
config.audio
```

### Using Translations

```python
from biblemateweb import get_translation

label = get_translation("Settings")  # Returns translated string based on app.storage.user["ui_language"]
```

### Creating Dialogs

```python
from biblemateweb.dialogs.review_dialog import ReviewDialog

edited_text = await ReviewDialog().open_with_text(original_text, label="Edit")
```

## Notes

- The application uses NiceGUI's `app.storage.user` for persistent user settings and `app.storage.client` for session-specific data
- Bible resources are lazily loaded from `~/biblemate/data/` directory
- Custom fonts (Ezra SIL, KoineGreek) loaded for Hebrew/Greek display
- All database connections use context managers for proper cleanup
- Regex search uses custom `regexp()` function registered with APSW
- The codebase includes many prototype files in `tests/` directory for experimentation

# BibleMate AI Web

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-green)](LICENSE)
[![Website](https://img.shields.io/badge/demo-biblemate.gospelchurch.uk-orange)](https://biblemate.gospelchurch.uk)

**AI-powered Bible study web application with advanced search, original language tools, and autonomous agent capabilities.**

BibleMate AI Web provides a unified web interface combining the best features of [BibleMate AI](https://github.com/eliranwong/biblemate) and [UniqueBible](https://github.com/eliranwong/UniqueBible). This repository contains the Web UI, HTTP Server, and API Server components.

> **Note:** For CLI Version, MCP Server, Agent Mode backend, Partner Mode, and Bible Data, see [BibleMate AI](https://github.com/eliranwong/biblemate)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Demo](#demo)
- [API Usage](#api-usage)
- [Configuration](#configuration)
  - [Server Configuration](#server-configuration)
  - [Agent Mode Settings](#agent-mode-settings)
  - [Google Drive Notes Sync](#google-drive-notes-sync)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Video Tutorials](#video-tutorials)
- [Platform Support](#platform-support)
- [Contributing](#contributing)

## Features

### Bible Study Tools
- **Multiple Bible Versions**: 100+ translations including original Hebrew (BHS5) and Greek (OGNT)
- **Original Language Support**: Interlinear view, morphology analysis, Strong's numbers
- **Hebrew & Greek Tooltips**: Instant lexical information on hover
- **Cross-References**: Treasury of Scripture Knowledge (TSK) integration
- **Commentaries**: 30+ classic Bible commentaries
- **Topical Studies**: Nave's, Thompson Chain, Torrey's topical Bibles
- **Bible Dictionaries & Encyclopedias**: Easton's, Smith's, ISBE, and more

### Advanced Search
- **Literal Search**: Fast text matching across Bible versions
- **Regex Search**: Powerful pattern-based searches
- **Semantic Search**: AI-powered meaning-based verse discovery
- **Parallel Passages**: Find related scripture across gospels and books
- **Bible Promises**: Search curated promise collections
- **Character & Location Studies**: Explore biblical people and places

### AI Integration
- **Chat Mode**: Conversational AI assistant for Bible study questions
- **Partner Mode**: Enhanced collaboration with extended context
- **Agent Mode**: Autonomous AI agent with tool selection and multi-step reasoning
- **Multi-backend Support**: OpenAI, Anthropic, Google AI, Azure, Cohere, DeepSeek, Mistral, xAI

### User Experience
- **Synchronized Scrolling**: Cross-reference comparison with linked scrolling
- **Audio Bible**: Listen to Bible chapters (multiple versions)
- **Personal Notes**: Google Drive integration for synced study notes
- **Customizable UI**: Dark mode, colors, fonts, layout options
- **Export**: Download content as TXT or DOCX (requires pandoc)
- **Deep Linking**: Share specific verses, chapters, and tool states via URL

### Developer Features
- **REST API**: Programmatic access to Bible data and tools
- **API Client**: Command-line tool for API queries
- **Extensible Architecture**: Plugin-based tool system
- **MCP Tools**: Model Context Protocol integration for AI agents

## Quick Start

### Installation

```bash
# Install BibleMate AI Web
pip install --upgrade biblemateweb

# One-time data setup (downloads Bible databases)
biblematedata

# Start the server
biblemateweb
```

The web UI will be available at **http://localhost:33355**

### First Run

1. **Configure Storage Secret**: For production deployment, generate a secure secret key:
   ```bash
   openssl rand -hex 32
   ```
   Add it to `~/biblemate/biblemateweb.config`:
   ```python
   config.storage_secret="your-generated-secret-here"
   ```

2. **Set AI Backend** (optional): Visit http://localhost:33355/settings to configure:
   - AI Backend (OpenAI, Anthropic, Google AI, etc.)
   - API Keys
   - Model preferences

3. **Customize Server** (optional): Edit `~/biblemate/biblemateweb.config`:
   - `config.port=33355` - Change server port
   - `config.avatar=""` - Set custom avatar URL
   - See [Configuration](#configuration) for more options

## Demo

Try BibleMate AI Web without installation: **[biblemate.gospelchurch.uk](https://biblemate.gospelchurch.uk)**


## API Usage

BibleMate AI Web provides a REST API for programmatic access to Bible data and study tools.

### Command-Line API Client

```bash
# Get help
biblemateapi -h

# Example queries
biblemateapi "verses:::John 3:16"
biblemateapi "chapter:::KJV:::Genesis 1"
biblemateapi "semantic:::love of God"
```

### API Endpoint

```
GET /api/data?query={query}&language={eng|tc|sc}&token={custom_token}
```

**Example:**
```bash
curl "http://localhost:33355/api/data?query=verses:::John%203:16&language=eng"
```

### Query Syntax

The API uses a keyword-based syntax with triple-colon delimiters:

```
{keyword}:::{options}:::{query}
```

**Supported Keywords:**
- `verses:::` - Retrieve Bible verses
- `chapter:::` - Get full chapters
- `semantic:::` - AI-powered semantic search
- `literal:::` - Literal text search
- `regex:::` - Regular expression search
- `commentary:::` - Bible commentary
- `lexicons:::` - Hebrew/Greek lexicons
- `topics:::` - Topical studies
- And more...

**Resources:**
- [API Query Documentation](docs/api_query.md) - Complete syntax reference
- [API Client Examples](tests/api_client.py) - Python usage examples

## Configuration

### Server Configuration

Edit `~/biblemate/biblemateweb.config` (create if it doesn't exist):

```python
config.hot_reload=False
config.avatar=""                    # Custom avatar URL
config.ai_backend=""                # Default AI backend
config.embedding_model="paraphrase-multilingual"
config.custom_token=""              # Token for custom data access
config.google_client_id=""          # Google OAuth (for Drive notes)
config.google_client_secret=""
config.auth_uri=""                  # OAuth redirect URI override
config.storage_secret="REPLACE_ME_WITH_A_REAL_SECRET"
config.port=33355
config.verses_limit=2000            # Max verses in search results
config.disable_agent_mode=False
config.disable_partner_mode=False
config.limit_agent_mode_once_daily=False
config.limit_partner_mode_once_daily=False
```

**Restart the server after configuration changes:**
```bash
# Kill the current process, then:
biblemateweb
```

### User Preferences

Individual users can customize their experience at: **http://localhost:33355/settings**

Settings include:
- UI Language (English, Traditional Chinese, Simplified Chinese)
- Dark Mode
- Font Size
- Primary Bible Version
- AI Backend & API Keys
- Semantic Search Parameters

### Agent Mode Settings

Agent Mode enables autonomous AI agents with tool selection capabilities. It consumes more tokens than standard chat mode.

**Restrict Public Access** (recommended for public deployments):

```python
# Disable agent mode for public users
config.disable_agent_mode=True

# Or limit to once daily per user
config.limit_agent_mode_once_daily=True
```

**Note:** Users can still access Agent Mode by:
1. Entering their own API keys in Settings
2. Using a custom token (if `config.custom_token` is set)

Daily limits require [Google Account authentication](#google-drive-notes-sync) to track usage per user. BibleMate AI does not store user data on servers - all settings are stored in the user's browser or Google Drive.

### Google Drive Notes Sync

Enable personal Bible study notes synchronized across devices via Google Drive.

**Setup:**

1. **Create Google Cloud Project** and enable Google Drive API
2. **Configure OAuth Credentials** (see [detailed setup guide](docs/google_drive_notes_setup.md))
3. **Add to config:**
   ```python
   config.google_client_id="your-client-id.apps.googleusercontent.com"
   config.google_client_secret="your-client-secret"
   config.auth_uri=""  # Optional: override redirect URI
   ```
4. **Restart server** and users can sign in via the UI

Notes are stored in users' Google Drive AppData folder (hidden, app-specific storage).

**Resources:**
- [Google Drive Notes Setup Guide](docs/google_drive_notes_setup.md)
- [Demo](https://biblemate.gospelchurch.uk)

### Document Export (DOCX)

To enable Word document export, install `pandoc`:

**Debian/Ubuntu:**
```bash
sudo apt install pandoc
```

**macOS:**
```bash
brew install pandoc
```

**Windows:**
Download from [pandoc.org](https://pandoc.org/installing.html)

Users can then download Bible content and AI chat conversations as `.docx` files.

## Deployment

### Production Deployment

**Required: Storage Secret Key**

Generate a secure secret for session encryption:

```bash
openssl rand -hex 32
```

Add to `~/biblemate/biblemateweb.config`:
```python
config.storage_secret="your-generated-secret-key"
```

### Server Hosting

BibleMate AI Web is built on NiceGUI, which supports various deployment options:

- **Standalone Server**: Run `biblemateweb` with process manager (systemd, supervisor)
- **Reverse Proxy**: Nginx, Apache, Caddy
- **Cloud Platforms**: Compatible with cloud hosting services

**Resources:**
- [NiceGUI Deployment Guide](https://nicegui.io/documentation/section_configuration_deployment#server_hosting)
- Recommended: Use reverse proxy with HTTPS for production

### Security Considerations

For public deployments:
- ✅ Set secure `config.storage_secret`
- ✅ Enable HTTPS via reverse proxy
- ✅ Consider restricting Agent/Partner modes to manage AI costs
- ✅ Set `config.verses_limit` to prevent excessive queries
- ✅ Configure OAuth carefully (restrict redirect URIs)

## Documentation

Full documentation is available in the [docs](docs/) directory.

- [API Query Syntax](docs/api_query.md) - Complete API reference
- [Google Drive Setup](docs/google_drive_notes_setup.md) - OAuth configuration
- [Custom Tokens](docs/custom_token.md) - Access control
- [API Key Setup](docs/api_key_setup.md) - AI backend configuration
- [Study Tools](docs/search/tool/) - Study Tools
- [Search Tools](docs/search/search/) - Search Tools
- [CLAUDE.md](CLAUDE.md) - Developer architecture guide

## Video Tutorials

- [UI Overview](https://youtu.be/UL8b1O97560) - Introduction to the interface
- [Hebrew & Greek Tooltips](https://youtu.be/qCMku8-UZ3I) - Original language features
- [Cross-Highlighting & Synchronized Scrolling](https://youtu.be/TDyT1ioesmY) - Comparison tools
- [Bible Audio](https://youtu.be/GL98FaJlYUQ) - Audio Bible features
- [User Customization](https://youtu.be/QMJ2oo1qkjY) - Personalization options

## Platform Support

- **Web UI**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **Server**: Linux, macOS, Windows (Python 3.10-3.12)
- **API Access**: Platform-independent REST API

## Contributing

Contributions welcome! This project is part of the larger BibleMate AI ecosystem.

**Related Repositories:**
- [BibleMate AI](https://github.com/eliranwong/biblemate) - CLI, MCP Server, Agent backend
- [UniqueBible](https://github.com/eliranwong/UniqueBible) - Desktop Bible study app

**Support:**
- [Issues](https://github.com/eliranwong/biblemateweb/issues) - Bug reports and feature requests
- [Wiki](https://github.com/eliranwong/biblemateweb/wiki) - Extended documentation
- [Funding](https://www.paypal.me/MarvelBible) - Support development

---

**License:** GPLv3+ | **Author:** [Eliran Wong](https://github.com/eliranwong) | **Website:** [biblemate.ai](https://biblemate.ai)


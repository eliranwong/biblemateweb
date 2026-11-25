# Studio Mode (BibleMate Agentic Workspace Integration)

**Studio Mode** brings together the best of two worlds in a single interface:

- **BibleMate Web**: Fast multi-version Bible reading, original-language interlinear & morphology, commentaries, encyclopedias, maps, timelines, and the Multi-Tool Workspace.
- **BibleMate Agentic Workspace**: Autonomous AI agents with specialist personas, exegesis skills, slash commands, saved study notes (`notes/`, `bibles/`, `images/`), and Markdown/DOCX export—running on the **same single server** as BibleMate Web without launching a second server process.

---

## Prerequisites & Access Control

1. **Custom Data Access**: Studio Mode is only enabled when `custom_data` is accessible (either `config.custom_token` is not set, or your session has a valid `custom_token` in **Settings** / `?t=...`).
2. **Workspace Directory**: Install `biblemate-agentic-workspace` into `~/biblemate` (or set the `BIBLEMATE_WORKSPACE_DIR` environment variable to a custom path).
3. **At Least One AI Backend**: Install and sign in to at least one of the supported CLI tools (no separate API key required for CLI backends) or configure `GEMINI_API_KEY`:
   - **Antigravity CLI (`agy`)** *(default when present)* — uses your signed-in Google subscription (`web_app_agy.py`).
   - **Claude Code CLI (`claude`)** — uses your signed-in Claude Code session (`web_app_claude.py`).
   - **Codex CLI (`codex`)** — uses your signed-in OpenAI Codex session via `codex login` (`web_app_codex.py`).
   - **Grok Build CLI (`grok`)** — uses your signed-in Grok session via `grok login` (`web_app_grok.py`).
   - **Gemini API (`gemini_api`)** — uses the `google-antigravity` Python SDK with the `GEMINI_API_KEY` environment variable (`web_app_gemini_api_key.py`).

---

## Setup Instructions

Download and unzip [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip) into `~/biblemate`, or run the command for your platform below:

### macOS

```bash
mkdir -p ~/biblemate && cd ~/biblemate
curl -L -O https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip && tar -xf manual_setup.zip && rm manual_setup.zip && mkdir -p biblemate notes images export bibles
```

### Linux

```bash
mkdir -p ~/biblemate && cd ~/biblemate
curl -L -O https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip && unzip -o manual_setup.zip && rm manual_setup.zip && mkdir -p biblemate notes images export bibles
```

### Windows

Download [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip), extract its contents into `%USERPROFILE%\biblemate` (for example `C:\Users\<your-username>\biblemate`), and create the `biblemate`, `notes`, `images`, `export`, and `bibles` subdirectories inside it.

### Install an AI Backend

Install and authenticate **at least one** of the following before using Studio Mode:

- **Antigravity CLI (`agy`)**: Install Antigravity CLI and sign in with your Google account.
- **Claude Code CLI (`claude`)**: Install Claude Code and complete sign-in.
- **Codex CLI (`codex`)**: Install Codex CLI and run `codex login`.
- **Grok Build CLI (`grok`)**: Install Grok Build and run `grok login`.
- **Gemini API (`gemini_api`)**: Install `google-antigravity` (`pip install -U google-antigravity`) and export `GEMINI_API_KEY="your-gemini-api-key"` in the shell running `biblemateweb`.

Once the workspace files are in `~/biblemate`, restart `biblemateweb`—it automatically detects the installed `web_app_*.py` backends.

---

## How to Use

### 1. Standalone Tool Tab

1. Open the **AI** menu (`auto_awesome` icon in the top bar, or **AI** in the mobile left drawer).
2. Click **Studio Mode** at the bottom of the AI menu.
3. A full-height **STUDIO** tab opens in the Tool Area:
   - **Backend Selector**: Switch between any detected backends (`agy` is selected by default when available; your choice is remembered per user).
   - **Bible Reference & Theme Sync**: Automatically inherits your current Bible reference from Area 1 and matches your light/dark mode and accent colors.
   - **Reload / Open in New Tab**: Use the refresh icon to reload the workspace, or the external-link icon to open `/agentic-workspace` full-screen in its own browser tab.

### 2. Inside Multi-Tool Workspace

You can run **Studio Mode** (and all other AI modes) side by side with traditional Bible study tools inside a single tab:

1. Open **Tools** → **Multi-Tool Workspace**.
2. Click **`+ Add Tool`** (or use any pane's tool switcher dropdown).
3. Choose from the AI resource options:
   - `AI: Chat Mode`
   - `AI: Partner Mode`
   - `AI: Agent Mode`
   - `AI: Studio Mode` *(shown when `~/biblemate` and `custom_data` are available)*

This lets you keep commentaries, cross-references, lexicons, or maps open in adjacent panes while collaborating with an autonomous AI agent in **AI: Studio Mode**.

---

Related: [AI Features](README.md) · [Multi-Tool Workspace](../tools/tool_multi_tool.md) · [AI Menu](../basics/menu_ai.md)

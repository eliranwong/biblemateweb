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

### Automatic Setup (Recommended)

Running `biblematedata` installs **BibleMate Agentic Workspace** into `~/biblemate` automatically alongside the Bible databases.

If you only want to install the workspace (for example, when Bible databases are already set up), run:

```bash
biblematedata --workspace-only
```

### Manual Setup (`manual_setup.zip`)

Alternatively, download and unzip [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip) into `~/biblemate`, or run the command for your platform below:

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
- **Claude Code CLI (`claude`)**: Install Claude Code and complete sign-in (or configure it with **Ollama** as shown below).
- **Codex CLI (`codex`)**: Install Codex CLI and run `codex login`.
- **Grok Build CLI (`grok`)**: Install Grok Build and run `grok login`.
- **Gemini API (`gemini_api`)**: Install `google-antigravity` (`pip install -U google-antigravity`) and export `GEMINI_API_KEY="your-gemini-api-key"` in the shell running `biblemateweb`.

Once the workspace files are in `~/biblemate`, restart `biblemateweb`—it automatically detects the installed `web_app_*.py` backends.

### Using Claude Code with Ollama (`~/.claude/settings.json`)

You can run the **Claude Code (`claude`)** backend against an Ollama server (supporting local or cloud models such as `glm-5.3-flash:cloud`) via Ollama's Anthropic-compatible API.

#### 1. Local / General Use (Recommended)

Rather than relying on shell `export` statements (which may not be inherited when `biblemateweb` is started from a service, desktop launcher, or different terminal), edit **`~/.claude/settings.json`** directly:

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "ollama",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_BASE_URL": "http://localhost:11434",
    "ANTHROPIC_MODEL": "glm-5.3-flash:cloud",
    "CLAUDE_CODE_MAX_CONTEXT_TOKENS": "256000",
    "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "skipDangerousModePermissionPrompt": true,
  "skipWorkflowUsageWarning": true
}
```

- Setting `"ANTHROPIC_API_KEY": ""` and `"ANTHROPIC_AUTH_TOKEN": "ollama"` ensures Claude Code authenticates against Ollama instead of requiring an Anthropic Console API key or `/login`.
- `"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"` disables telemetry, auto-updater checks, and non-essential background calls when routing through Ollama.

#### 2. Docker (`http://host.docker.internal:11434` or `http://ollama:11434`)

When running `biblemateweb` inside a Docker container, set `ANTHROPIC_BASE_URL` to **`http://host.docker.internal:11434`** to point to Ollama running on the host outside the container (or use **`http://ollama:11434`** if using the Docker Compose `ollama` service):

- In `docker-compose.yml` (see [`docker/uniquebible-server/docker-compose.yml`](../../../docker/uniquebible-server/docker-compose.yml) and [`docker/AGY_DOCKER_SETUP.md`](../../../docker/AGY_DOCKER_SETUP.md)):
  ```yaml
  extra_hosts:
    - "host.docker.internal:host-gateway"
  environment:
    ANTHROPIC_AUTH_TOKEN: ollama
    ANTHROPIC_API_KEY: ""
    # Points to Ollama running on the host (use http://ollama:11434 if using the Compose ollama service)
    ANTHROPIC_BASE_URL: http://host.docker.internal:11434
    ANTHROPIC_MODEL: glm-5.3-flash:cloud
    CLAUDE_CODE_MAX_CONTEXT_TOKENS: 256000
    CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS: 0
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1"
  ```
- If you bind-mount `~/.claude` into the Docker container and define `"env"` inside `~/.claude/settings.json`, set `"ANTHROPIC_BASE_URL": "http://host.docker.internal:11434"` (or `"http://ollama:11434"` for the Compose `ollama` service) in `~/.claude/settings.json`, or omit `ANTHROPIC_BASE_URL` from `settings.json` so the container uses `ANTHROPIC_BASE_URL` from `docker-compose.yml`.

### Using Codex CLI with Azure OpenAI Models (`~/.codex/config.toml`)

If you prefer using **Codex CLI (`codex`)** with Azure OpenAI models instead of a ChatGPT/Codex subscription (`codex login`), configure **`~/.codex/config.toml`** as follows:

```toml
model = "gpt-6.1-sol"
model_provider = "azure"
model_reasoning_effort = "high"
sandbox_mode = "danger-full-access"
approval_policy = "never"
web_search = "live"

[model_providers.azure]
name = "Azure OpenAI"
base_url = "https://<project_name>.openai.azure.com/openai/v1"
experimental_bearer_token = "<token>"
#env_key = "AZURE_OPENAI_API_KEY"
wire_api = "responses"

[sandbox_workspace_write]
network_access = true

[projects."/tmp/codex-research"]
trust_level = "trusted"

[projects."/tmp/macro-codex"]
trust_level = "trusted"

[projects."/tmp/intl-scan"]
trust_level = "trusted"

[projects."/tmp"]
trust_level = "trusted"

[tui]
screen_reader_detection_done = true

[notice.model_migrations]
"gpt-5.3-codex" = "gpt-5.4"
"gpt-5.5" = "gpt-6-sol"
```

- Replace `<project_name>` with your Azure OpenAI resource/project name, and set `experimental_bearer_token = "<token>"` (or uncomment `env_key = "AZURE_OPENAI_API_KEY"` and export `AZURE_OPENAI_API_KEY` in your environment).
- In Docker (`uniquebible-server`), `~/.codex` is bind-mounted into the container, so this configuration works for both local and Docker deployments.

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

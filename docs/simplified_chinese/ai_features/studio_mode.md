# 工作室模式（集成 BibleMate Agentic Workspace）

**工作室模式（Studio Mode）**将两者的优势完美结合在同一个界面中：

- **BibleMate Web**：快速的多译本圣经阅读、原文逐字对照与形态学分析、注释书、百科全书、地图、时间轴与多工具工作区。
- **BibleMate Agentic Workspace**：具备专业角色设定（Personas）、释经技能（Skills）、斜杠命令、笔记与经文文件管理（`notes/`、`bibles/`、`images/`）以及 Markdown / DOCX 导出的自主型 AI 代理——**与 BibleMate Web 共用同一个服务器**，无需额外启动第二个服务器。

---

## 前置条件与访问控制

1. **自定义数据访问权限**：仅当 `custom_data` 可访问时才会显示并启用工作室模式（未设置 `config.custom_token`，或在**设置**／网址参数 `?t=...` 中提供匹配的 `custom_token`）。
2. **工作区目录**：将 `biblemate-agentic-workspace` 安装至 `~/biblemate`（或设置环境变量 `BIBLEMATE_WORKSPACE_DIR` 指向自定义路径）。
3. **至少一个 AI 后端**：安装并登录至少一个支持的 CLI 工具（CLI 后端无需额外 API 密钥），或设置 `GEMINI_API_KEY`：
   - **Antigravity CLI (`agy`)** *（存在时默认选用）*——使用已登录的 Google 订阅账号（`web_app_agy.py`）。
   - **Claude Code CLI (`claude`)**——使用已登录的 Claude Code 会话（`web_app_claude.py`）。
   - **Codex CLI (`codex`)**——使用已通过 `codex login` 登录的 OpenAI Codex（`web_app_codex.py`）。
   - **Grok Build CLI (`grok`)**——使用已通过 `grok login` 登录的 Grok 会话（`web_app_grok.py`）。
   - **Gemini API (`gemini_api`)**——使用 `google-antigravity` Python SDK 搭配环境变量 `GEMINI_API_KEY`（`web_app_gemini_api_key.py`）。

---

## 安装与配置步骤

### 自动安装（推荐）

运行 `biblematedata` 时，系统会自动将 **BibleMate Agentic Workspace** 与圣经数据库一并安装至 `~/biblemate`。

如果您只需安装工作区（例如已配置好圣经数据库），可以运行：

```bash
biblematedata --workspace-only
```

### 手动安装（`manual_setup.zip`）

您也可以手动下载并解压 [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip) 至 `~/biblemate`，或按操作系统运行以下命令：

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

下载 [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip)，解压至 `%USERPROFILE%\biblemate`（例如 `C:\Users\<您的用户名>\biblemate`），并在其中创建 `biblemate`、`notes`、`images`、`export` 与 `bibles` 子文件夹。

### 安装 AI 后端

在使用工作室模式前，请先安装并认证**至少一个**以下后端：

- **Antigravity CLI (`agy`)**：安装 Antigravity CLI 并登录您的 Google 账号。
- **Claude Code CLI (`claude`)**：安装 Claude Code 并完成登录（或如下方所示搭配 **Ollama** 配置使用）。
- **Codex CLI (`codex`)**：安装 Codex CLI 并运行 `codex login`。
- **Grok Build CLI (`grok`)**：安装 Grok Build 并运行 `grok login`。
- **Gemini API (`gemini_api`)**：安装 `google-antigravity`（`pip install -U google-antigravity`），并在启动 `biblemateweb` 的终端中导出环境变量 `GEMINI_API_KEY="your-gemini-api-key"`。

完成上述文件配置后，重启 `biblemateweb`，系统会自动检测已安装的 `web_app_*.py` 后端。

### 搭配 Ollama 使用 Claude Code（`~/.claude/settings.json`）

您可以通过 Ollama 兼容 Anthropic 的 API，让 **Claude Code (`claude`)** 后端连接至 Ollama 服务器（支持本地或云端模型，例如 `glm-5.3-flash:cloud`）。

#### 1. 本地／常规使用（推荐做法）

建议直接编辑 **`~/.claude/settings.json`**，而非仅依赖终端的 `export` 环境变量（避免从系统服务、桌面快捷方式或不同终端启动 `biblemateweb` 时未继承环境变量）：

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

- 设置 `"ANTHROPIC_API_KEY": ""` 与 `"ANTHROPIC_AUTH_TOKEN": "ollama"` 可确保 Claude Code 直接连接至 Ollama，而不会要求 Anthropic Console API 密钥或 `/login`。
- `"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"` 可禁用遥测、自动更新检查与非必要的后台请求。

#### 2. Docker 环境（`http://host.docker.internal:11434` 或 `http://ollama:11434`）

当 `biblemateweb` 在 Docker 容器内运行时，若要指向容器外宿主机（Host）上运行的 Ollama，请将 `ANTHROPIC_BASE_URL` 设为 **`http://host.docker.internal:11434`**（若使用 Docker Compose 内的 `ollama` 服务，请改用 **`http://ollama:11434`**）：

- 在 `docker-compose.yml` 中（详见 [`docker/uniquebible-server/docker-compose.yml`](../../../docker/uniquebible-server/docker-compose.yml) 与 [`docker/AGY_DOCKER_SETUP.md`](../../../docker/AGY_DOCKER_SETUP.md)）：
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
- 若将宿主机的 `~/.claude` 挂载进 Docker 容器且在 `~/.claude/settings.json` 中定义了 `"env"`，请将其中的 `ANTHROPIC_BASE_URL` 设为 `"http://host.docker.internal:11434"`（若使用 Compose `ollama` 服务则设为 `"http://ollama:11434"`），或从 `settings.json` 中省略 `ANTHROPIC_BASE_URL`，让容器使用 `docker-compose.yml` 中的 `ANTHROPIC_BASE_URL` 配置。

### 搭配 Azure OpenAI 模型使用 Codex CLI（`~/.codex/config.toml`）

如果您希望使用 **Codex CLI (`codex`)** 搭配 Azure OpenAI 模型（而非 ChatGPT／Codex 订阅登录 `codex login`），可参考以下推荐配置编辑 **`~/.codex/config.toml`**：

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

- 请将 `<project_name>` 替换为您的 Azure OpenAI 资源／项目名称，并设置 `experimental_bearer_token = "<token>"`（或取消注释 `env_key = "AZURE_OPENAI_API_KEY"` 并在环境中导出 `AZURE_OPENAI_API_KEY`）。
- 在 Docker（`uniquebible-server`）中，`~/.codex` 会自动挂载进容器，因此该配置同时适用于本地与 Docker 部署。

---

## 使用方式

### 1. 作为独立工具标签页使用

1. 打开导航栏的 **AI** 菜单（`auto_awesome` 图标，或移动端左侧抽屉中的 **AI**）。
2. 点击菜单底部的 **工作室模式**（Studio Mode）。
3. 工具区域将打开全高度的 **STUDIO** 标签页：
   - **后端切换器**：在已检测到的后端之间自由切换（存在 `agy` 时默认选用 `agy`，并会记住您的偏好）。
   - **经文与主题同步**：自动带入圣经区当前阅读的经文引用，并自动同步深色／浅色模式与主题配色。
   - **重新加载／在新标签页打开**：点击刷新图标可重载工作区；点击外链图标可在新浏览器标签页中全屏打开 `/agentic-workspace`。

### 2. 在多工具工作区中使用

您可以在单个标签页内，将**工作室模式**（以及其他 AI 模式）与传统研经工具并排使用：

1. 打开 **工具** → **多工具工作区**。
2. 点击 **`+ 添加工具`**（或使用任一面板的工具切换下拉菜单）。
3. 选择 AI 资源选项：
   - `AI：对话模式`
   - `AI：伙伴模式`
   - `AI：代理模式`
   - `AI：工作室模式` *（当 `~/biblemate` 已安装且 `custom_data` 可访问时显示）*

借此即可在相邻面板同时对照注释、串珠、原文字典或圣经地图，并与 **AI：工作室模式** 中的自主代理协作研经。

---

相关主题：[AI 功能](README.md) · [多工具工作区](../tools/tool_multi_tool.md) · [AI 菜单](../basics/menu_ai.md)

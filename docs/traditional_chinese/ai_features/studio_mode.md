# 工作室模式（整合 BibleMate Agentic Workspace）

**工作室模式（Studio Mode）**將兩者的優勢完美結合在同一個介面中：

- **BibleMate Web**：快速的多譯本聖經閱讀、原文逐字對照與形態學分析、註釋書、百科全書、地圖、時間軸與多工具工作區。
- **BibleMate Agentic Workspace**：具備專業角色設定（Personas）、釋經技能（Skills）、斜線指令、筆記與經文檔案管理（`notes/`、`bibles/`、`images/`）以及 Markdown / DOCX 匯出的自主型 AI 代理——**與 BibleMate Web 共用同一個伺服器**，無需額外啟動第二個伺服器。

---

## 前置條件與存取控制

1. **自訂資料存取權限**：僅當 `custom_data` 可存取時才會顯示並啟用工作室模式（未設定 `config.custom_token`，或在**設定**／網址參數 `?t=...` 中提供相符的 `custom_token`）。
2. **工作區目錄**：將 `biblemate-agentic-workspace` 安裝至 `~/biblemate`（或設定環境變數 `BIBLEMATE_WORKSPACE_DIR` 指向自訂路徑）。
3. **至少一個 AI 後端**：安裝並登入至少一個支援的 CLI 工具（CLI 後端無需額外 API 金鑰），或設定 `GEMINI_API_KEY`：
   - **Antigravity CLI (`agy`)** *（存在時預設選用）*——使用已登入的 Google 訂閱帳號（`web_app_agy.py`）。
   - **Claude Code CLI (`claude`)**——使用已登入的 Claude Code 工作階段（`web_app_claude.py`）。
   - **Codex CLI (`codex`)**——使用已透過 `codex login` 登入的 OpenAI Codex（`web_app_codex.py`）。
   - **Grok Build CLI (`grok`)**——使用已透過 `grok login` 登入的 Grok 工作階段（`web_app_grok.py`）。
   - **Gemini API (`gemini_api`)**——使用 `google-antigravity` Python SDK 搭配環境變數 `GEMINI_API_KEY`（`web_app_gemini_api_key.py`）。

---

## 安裝與設定步驟

下載並解壓縮 [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip) 至 `~/biblemate`，或依作業系統執行下列指令：

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

下載 [`manual_setup.zip`](https://github.com/eliranwong/antigravity-biblemate-workspace/raw/main/manual_setup.zip)，解壓縮至 `%USERPROFILE%\biblemate`（例如 `C:\Users\<您的使用者名稱>\biblemate`），並在其中建立 `biblemate`、`notes`、`images`、`export` 與 `bibles` 子資料夾。

### 安裝 AI 後端

在使用工作室模式前，請先安裝並驗證**至少一個**以下後端：

- **Antigravity CLI (`agy`)**：安裝 Antigravity CLI 並登入您的 Google 帳號。
- **Claude Code CLI (`claude`)**：安裝 Claude Code 並完成登入。
- **Codex CLI (`codex`)**：安裝 Codex CLI 並執行 `codex login`。
- **Grok Build CLI (`grok`)**：安裝 Grok Build 並執行 `grok login`。
- **Gemini API (`gemini_api`)**：安裝 `google-antigravity`（`pip install -U google-antigravity`），並在啟動 `biblemateweb` 的終端機中設定環境變數 `GEMINI_API_KEY="your-gemini-api-key"`。

完成上述檔案配置後，重新啟動 `biblemateweb`，系統會自動偵測已安裝的 `web_app_*.py` 後端。

---

## 使用方式

### 1. 作為獨立工具標籤頁使用

1. 開啟導覽列的 **AI** 選單（`auto_awesome` 圖示，或行動版左側抽屜中的 **AI**）。
2. 點擊選單底部的 **工作室模式**（Studio Mode）。
3. 工具區域將開啟全高度的 **STUDIO** 標籤頁：
   - **後端切換器**：在已偵測到的後端之間自由切換（有 `agy` 時預設選用 `agy`，並會記住您的偏好）。
   - **經文與主題同步**：自動帶入聖經區目前閱讀的經文參照，並自動同步深色／淺色模式與佈景配色。
   - **重新載入／在新分頁開啟**：點擊重新整理圖示可重載工作區；點擊外部連結圖示可在新瀏覽器分頁中全螢幕開啟 `/agentic-workspace`。

### 2. 在多工具工作區中使用

您可以在單一標籤頁內，將**工作室模式**（以及其他 AI 模式）與傳統研經工具並排使用：

1. 開啟 **工具** → **多工具工作區**。
2. 點擊 **`+ 新增工具`**（或使用任一面板的工具切換下拉選單）。
3. 選擇 AI 資源選項：
   - `AI：對話模式`
   - `AI：夥伴模式`
   - `AI：代理模式`
   - `AI：工作室模式` *（當 `~/biblemate` 已安裝且 `custom_data` 可存取時顯示）*

藉此即可在相鄰面板同時對照註釋、串珠、原文字典或聖經地圖，並與 **AI：工作室模式** 中的自主代理協作研經。

---

相關主題：[AI 功能](README.md) · [多工具工作區](../tools/tool_multi_tool.md) · [AI 選單](../basics/menu_ai.md)

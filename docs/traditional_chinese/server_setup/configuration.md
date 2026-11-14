# BibleMate Web 配置設定指南

本指南提供使用 `~/biblemate/biblemateweb.config` 設定檔配置 BibleMate Web 的詳細參考資料。

---

## 概述

BibleMate Web 將伺服器層級的設定保存在以下路徑的設定檔中：

```
~/biblemate/biblemateweb.config
```

*(完整路徑：`/home/<username>/biblemate/biblemateweb.config`)*

### 主要特性：
* **自動建立**：若設定檔不存在，BibleMate Web 會在首次啟動時自動建立帶有預設值的設定檔。
* **檔案格式**：該檔案使用 Python 賦值語法（例如 `config.port=33355`）。
* **自動遷移**：升級 BibleMate Web 時，任何新加入的配置選項都會自動合併至您的 `biblemateweb.config` 檔案中，不會覆蓋現有的設定。
* **套用變更**：每當修改 `biblemateweb.config` 後，您必須重新啟動 `biblemateweb` 行程以使變更生效。

---

## 完整配置範例

以下是使用標準預設值與範例金鑰的完整設定檔範例。**切勿將實際的正式環境機密金鑰提交到共用的版本控制系統中。**

```python
config.hot_reload=False
config.avatar=""
config.ai_backend=""
config.show_grok_build=False
config.use_grok_build_for_default=False
config.show_claude_code=False
config.use_claude_code_for_default=False
config.show_antigravity=False
config.use_antigravity_for_default=False
config.embedding_model="paraphrase-multilingual"
config.custom_token="your-custom-access-token-12345"
config.google_client_id="123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
config.google_client_secret="BIBLEMATE-sample_client_secret_xyz123456789"
config.auth_uri=""
config.storage_secret="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
config.port=33355
config.verses_limit=2000
config.disable_agent_mode=False
config.disable_partner_mode=False
config.limit_agent_mode_once_daily=False
config.limit_partner_mode_once_daily=False
config.disable_local_api_endpoint=True
```

---

## 詳細選項參考

### 1. 核心與伺服器設定

#### `config.port`
* **類型**：`int`
* **預設值**：`33355`
* **說明**：指定 Web 伺服器監聽的 TCP 網路通訊埠。
* **範例**：
  ```python
  config.port=33355
  ```

#### `config.storage_secret`
* **類型**：`str`
* **預設值**：`"REPLACE_ME_WITH_A_REAL_SECRET"`
* **說明**：用於 NiceGUI 中的工作階段加密與瀏覽器狀態管理的機密金鑰。**在公開部署時對安全性至關重要。**
* **範例**：
  ```python
  config.storage_secret="4a8f9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
  ```
* **取得 / 產生方式**：
  在終端機中執行以下任一命令：
  - 使用 OpenSSL：
    ```bash
    openssl rand -hex 32
    ```
  - 使用 Python：
    ```bash
    python3 -c "import secrets; print(secrets.token_hex(32))"
    ```

#### `config.hot_reload`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：啟用開發期間的自動重新載入模式。當為 `True` 時，原始碼檔案變更時伺服器會自動重啟。
* **範例**：
  ```python
  config.hot_reload=False
  ```

#### `config.avatar`
* **類型**：`str`
* **預設值**：`""`
* **說明**：自訂圖片檔案的絕對路徑，用作應用程式圖示 / 頭像（favicon/avatar）。若留空，應用程式將使用預設圖示。
* **範例**：
  ```python
  config.avatar="/home/user/images/my_custom_logo.png"
  ```

---

### 2. AI 與嵌入模型設定

#### `config.ai_backend`
* **類型**：`str`
* **預設值**：`""`
* **說明**：指定伺服器端的預設 AI 提供商後端（例如 `"googleai"`, `"openai"`, `"anthropic"`, `"groq"`, `"ollama"`, `"deepseek"`, `"grok"`, `"claude"`, `"antigravity"`）。若為空，系統將回退至內建預設值。`"grok"` 透過 `grokbuildstreaming` 從已登入的 Grok Build CLI (`grok login`) 進行串流。`"claude"` 透過 `claudecodestreaming` 從已登入的 Claude Code CLI (`claude auth login`) 進行串流。`"antigravity"` 透過 `antigravitystreaming` 從已登入的 Antigravity CLI (`agy`) 進行串流。這三者皆不需要使用 API 金鑰。若使用者自行選擇其他後端並儲存 API 金鑰，仍會使用該使用者指定的後端。
* **範例**：
  ```python
  config.ai_backend="googleai"
  ```
* **如何取得 API 金鑰**：
  - **Google Gemini（提供免費額度）**：
    1. 造訪 [Google AI Studio](https://aistudio.google.com/)。
    2. 點擊 **Get API Key** -> **Create API Key**。
    3. 複製您的金鑰。（請參閱 [API 金鑰設定指南](../user_preferences/api_key_setup.md)）。
  - **OpenAI**：
    1. 登入 [OpenAI Platform](https://platform.openai.com/api-keys)。
    2. 點擊 **Create new secret key**。
  - **Anthropic (Claude)**：
    1. 登入 [Anthropic Console](https://console.anthropic.com/)。
    2. 前往 **API Keys** 並生成新金鑰。
  - **Groq**：
    1. 登入 [Groq Console](https://console.groq.com/keys)。
    2. 建立 API 金鑰。
  - **Ollama（本地 AI）**：
    1. 在本機安裝並執行 `ollama serve`（不需要 API 金鑰）。
  - *備註*：個別使用者也可以在介面的**偏好設定**中設定個人專屬的 API 金鑰（BYOK 模式）。

#### `config.show_grok_build`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，偏好設定中的 AI 後端清單會包含 `grok (Grok Build subscription)`。當為 `False` 時，該選項隱藏。該訂閱來自透過 `grokbuildstreaming` 套件已登入的 `grok login` 工作階段，不需要 API 金鑰。
* **範例**：
  ```python
  config.show_grok_build=True
  ```

#### `config.use_grok_build_for_default`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，將 AI 後端保留為 `default` 的使用者將接收來自已登入 Grok Build 訂閱的串流回覆。當為 `False` 時，`default` 會保持伺服器的 `config.ai_backend` 設定，或者在該值為空時使用內建後端。選擇特定後端的使用者將繼續使用該後端。若下方多個 `use_*_for_default` 標記均為 `True`，則優先使用 grok，其次是 claude，最後是 antigravity。
* **範例**：
  ```python
  config.use_grok_build_for_default=True
  ```

#### `config.show_claude_code`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，偏好設定中的 AI 後端清單會包含 `claude (Claude Code subscription)`。當為 `False` 時，該選項隱藏。該訂閱來自透過 `claudecodestreaming` 套件已登入的 `claude auth login` 工作階段，不需要 API 金鑰。
* **範例**：
  ```python
  config.show_claude_code=True
  ```

#### `config.use_claude_code_for_default`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，將 AI 後端保留為 `default` 的使用者將接收來自已登入 Claude Code 訂閱的串流回覆。當為 `False` 時，`default` 會保持伺服器的 `config.ai_backend` 設定，或者在該值為空時使用內建後端。選擇特定後端的使用者將繼續使用該後端。若 `config.use_grok_build_for_default` 同時為 `True`，則優先使用 grok。
* **範例**：
  ```python
  config.use_claude_code_for_default=True
  ```

#### `config.show_antigravity`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，偏好設定中的 AI 後端清單會包含 `antigravity (Antigravity subscription)`。當為 `False` 時，該選項隱藏。該訂閱來自透過 `antigravitystreaming` 套件已登入的 Antigravity CLI (`agy`) 工作階段，不需要 API 金鑰。
* **範例**：
  ```python
  config.show_antigravity=True
  ```

#### `config.use_antigravity_for_default`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，將 AI 後端保留為 `default` 的使用者將接收來自已登入 Antigravity CLI 的串流回覆。當為 `False` 時，`default` 會保持伺服器的 `config.ai_backend` 設定，或者在該值為空時使用內建後端。選擇特定後端的使用者將繼續使用該後端。若 `config.use_grok_build_for_default` 或 `config.use_claude_code_for_default` 亦為 `True`，則會優先使用前面的選項。
* **範例**：
  ```python
  config.use_antigravity_for_default=True
  ```

#### `config.embedding_model`
* **類型**：`str`
* **預設值**：`"paraphrase-multilingual"`
* **說明**：用於生成向量嵌入（Vector Embeddings）的 sentence-transformer 模型，用於語義聖經搜索與主題索引功能。
* **範例**：
  ```python
  config.embedding_model="paraphrase-multilingual"
  ```

---

### 3. 存取控制與權杖

#### `config.custom_token`
* **類型**：`str`
* **預設值**：`""`
* **說明**：由伺服器管理員設定的主存取權杖（Token）。在應用程式偏好設定中輸入此權杖（或透過 URL 查詢參數 `?custom_token=YOUR_TOKEN`）的使用者，可以存取自訂資源（存儲在 `~/biblemate/data_custom` 中）並跳過伺服器速率限制。自訂參考書籍可放置在 `~/biblemate/data_custom/books`（詳見[書籍指南](../tools/tool_books.md)）。
* **範例**：
  ```python
  config.custom_token="my-secret-community-token-2026"
  ```
* **使用者如何使用**：
  1. 將權杖字串分享給授權使用者。
  2. 使用者在 Web 應用程式中前往**偏好設定** -> **使用者與自訂數據** -> **自訂 Token** 進行輸入。
  3. 詳細說明請參閱[自訂 Token 指南](../user_preferences/custom_token.md)。

#### `config.disable_local_api_endpoint`
* **類型**：`bool`
* **預設值**：`True`
* **說明**：安全性設定。當為 `True` 時，禁止 Web 介面使用者指定本地 API 端點（如 `http://localhost:11434` 或 `http://127.0.0.1:5000`）進行 AI 串流。這能保護公開部署的伺服器免受伺服器端請求偽造（SSRF）攻擊。
* **範例**：
  ```python
  config.disable_local_api_endpoint=True
  ```

---

### 4. 使用限制與模式控制

#### `config.disable_agent_mode`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，對全體一般使用者禁用整個應用程式中的**代理模式**。（透過 BYOK 提供自訂 API 金鑰或提供有效 `custom_token` 的使用者仍可存取代理模式）。
* **範例**：
  ```python
  config.disable_agent_mode=False
  ```

#### `config.disable_partner_mode`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，對一般使用者禁用**夥伴模式**。
* **範例**：
  ```python
  config.disable_partner_mode=False
  ```

#### `config.limit_agent_mode_once_daily`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，限制一般使用者每天只能執行一次**代理模式**。提供自用 API 金鑰或輸入有效 `custom_token` 的使用者不受此限制。
* **範例**：
  ```python
  config.limit_agent_mode_once_daily=True
  ```

#### `config.limit_partner_mode_once_daily`
* **類型**：`bool`
* **預設值**：`False`
* **說明**：當為 `True` 時，限制一般使用者每天只能執行一次**夥伴模式**。提供自用 API 金鑰或輸入有效 `custom_token` 的使用者不受此限制。
* **範例**：
  ```python
  config.limit_partner_mode_once_daily=True
  ```

---

### 5. Google Drive 筆記同步 (OAuth 2.0)

這些設定用於啟用個人聖經研經筆記與 Google Drive 的同步。

#### `config.google_client_id`
* **類型**：`str`
* **預設值**：`""`
* **說明**：Google Cloud Console 所核發的 OAuth 2.0 客戶端 ID（Client ID）。
* **範例**：
  ```python
  config.google_client_id="123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
  ```

#### `config.google_client_secret`
* **類型**：`str`
* **預設值**：`""`
* **說明**：與您的 `google_client_id` 對應的 OAuth 2.0 客戶端金鑰（Client Secret）。
* **範例**：
  ```python
  config.google_client_secret="GOCSPX-sample_client_secret_xyz123456789"
  ```

#### `config.auth_uri`
* **類型**：`str`
* **預設值**：`""`
* **說明**：明確覆蓋的 OAuth 2.0 重新導向 URI。若留空 `""`，BibleMate Web 會根據連入的 Web 請求自動建構回呼網址（例如 `http://localhost:33355/auth`）。如果您在 Nginx/Apache 反向代理或自訂 HTTPS 網域後方運行，請明確指定此項。
* **範例**：
  ```python
  config.auth_uri="https://biblemate.example.com/auth"
  ```

* **如何取得 Google OAuth 憑證**：
  1. 開啟 [Google Cloud Console](https://console.cloud.google.com/)。
  2. 建立新專案（例如 `"BibleMate AI"`）。
  3. 前往 **API 和服務** -> **程式庫**，搜尋 **Google Drive API**，然後點擊**啟用**。
  4. 設定 **OAuth 同意畫面**（選擇使用者類型：*外部*，並在測試使用者下新增您的電子郵件）。
  5. 前往**憑證** -> **建立憑證** -> **OAuth 2.0 用戶端 ID**。
  6. 選擇應用程式類型：**網路應用程式**。
  7. 在**已授權的重新導向 URI** 下，新增 `http://localhost:33355/auth` 和 `http://127.0.0.1:33355/auth`（或您的等效網域）。
  8. 將產生的**用戶端編號**與**用戶端金鑰**複製到您的設定檔中。
  9. 有關詳細逐步指南，請參閱 [Google Drive 筆記設定指南](google_drive_notes_setup.md)。

---

### 6. 數據查詢限制

#### `config.verses_limit`
* **類型**：`int`
* **預設值**：`2000`
* **說明**：單次搜索或查詢執行所回傳的聖經經文數量上限，以防止高記憶體佔用和 UI 卡頓。
* **範例**：
  ```python
  config.verses_limit=2000
  ```

---

## 測試與驗證設定

1. 使用所需的配置值編輯 `~/biblemate/biblemateweb.config`。
2. 儲存檔案。
3. 啟動或重啟 BibleMate Web：
   ```bash
   biblemateweb
   ```
4. 開啟瀏覽器並前往：
   ```
   http://localhost:33355
   ```
5. 檢查終端機控制台日誌，確認伺服器在您指定的連接埠上啟動且無錯誤。

---

## 相關文檔

- [自備金鑰 (BYOK) 設定](../user_preferences/api_key_setup.md)
- [自訂存取權杖](../user_preferences/custom_token.md)
- [Google Drive 筆記 OAuth 設定](google_drive_notes_setup.md)
- [API 查詢語法](../api/api_query.md)

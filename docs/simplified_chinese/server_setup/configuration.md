# BibleMate Web 配置设定指南

本指南提供使用 `~/biblemate/biblemateweb.config` 配置文件配置 BibleMate Web 的详细参考资料。

---

## 概述

BibleMate Web 将服务器层级的设定保存在以下路径的配置文件中：

```
~/biblemate/biblemateweb.config
```

*(完整路径：`/home/<username>/biblemate/biblemateweb.config`)*

### 主要特性：
* **自动创建**：若配置文件不存在，BibleMate Web 会在首次启动时自动创建带有默认值的配置文件。
* **文件格式**：该文件使用 Python 赋值语法（例如 `config.port=33355`）。
* **自动迁移**：升级 BibleMate Web 时，任何新加入的配置选项都会自动合并至您的 `biblemateweb.config` 文件中，不会覆盖现有的设定。
* **应用变更**：每当修改 `biblemateweb.config` 后，您必须重启 `biblemateweb` 进程以使变更生效。

---

## 完整配置示例

以下是使用标准默认值与示例密钥的完整配置文件示例。**切勿将实际的生产环境机密密钥提交到共享的版本控制系统中。**

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

## 详细选项参考

### 1. 核心与服务器设定

#### `config.port`
* **类型**：`int`
* **默认值**：`33355`
* **说明**：指定 Web 服务器监听的 TCP 网络端口。
* **示例**：
  ```python
  config.port=33355
  ```

#### `config.storage_secret`
* **类型**：`str`
* **默认值**：`"REPLACE_ME_WITH_A_REAL_SECRET"`
* **说明**：用于 NiceGUI 中的会话加密与浏览器状态管理的机密密钥。**在公开部署时对安全性至关重要。**
* **示例**：
  ```python
  config.storage_secret="4a8f9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
  ```
* **获取 / 生成方式**：
  在终端中运行以下任一命令：
  - 使用 OpenSSL：
    ```bash
    openssl rand -hex 32
    ```
  - 使用 Python：
    ```bash
    python3 -c "import secrets; print(secrets.token_hex(32))"
    ```

#### `config.hot_reload`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：启用开发期间的自动重新加载模式。当为 `True` 时，源码文件变更时服务器会自动重启。
* **示例**：
  ```python
  config.hot_reload=False
  ```

#### `config.avatar`
* **类型**：`str`
* **默认值**：`""`
* **说明**：自定义图像文件的绝对路径，用作应用程序图标 / 头像（favicon/avatar）。若留空，应用程序将使用默认图标。
* **示例**：
  ```python
  config.avatar="/home/user/images/my_custom_logo.png"
  ```

---

### 2. AI 与嵌入模型设定

#### `config.ai_backend`
* **类型**：`str`
* **默认值**：`""`
* **说明**：指定服务器端的默认 AI 提供商后端（例如 `"googleai"`, `"openai"`, `"anthropic"`, `"groq"`, `"ollama"`, `"deepseek"`, `"grok"`, `"claude"`, `"antigravity"`）。若为空，系统将回退至内置默认值。`"grok"` 通过 `grokbuildstreaming` 从已登录的 Grok Build CLI (`grok login`) 进行流式传输。`"claude"` 通过 `claudecodestreaming` 从已登录的 Claude Code CLI (`claude auth login`) 进行流式传输。`"antigravity"` 通过 `antigravitystreaming` 从已登录的 Antigravity CLI (`agy`) 进行流式传输。这三者均不需要使用 API 密钥。若用户自行选择其他后端并保存 API 密钥，仍会使用该用户指定的后端。
* **示例**：
  ```python
  config.ai_backend="googleai"
  ```
* **如何获取 API 密钥**：
  - **Google Gemini（提供免费额度）**：
    1. 访问 [Google AI Studio](https://aistudio.google.com/)。
    2. 点击 **Get API Key** -> **Create API Key**。
    3. 复制您的密钥。（请参阅 [API 密钥设定指南](../user_preferences/api_key_setup.md)）。
  - **OpenAI**：
    1. 登录 [OpenAI Platform](https://platform.openai.com/api-keys)。
    2. 点击 **Create new secret key**。
  - **Anthropic (Claude)**：
    1. 登录 [Anthropic Console](https://console.anthropic.com/)。
    2. 前往 **API Keys** 并生成新密钥。
  - **Groq**：
    1. 登录 [Groq Console](https://console.groq.com/keys)。
    2. 创建 API 密钥。
  - **Ollama（本地 AI）**：
    1. 在本地机器安装并运行 `ollama serve`（无需 API 密钥）。
  - *注*：个别用户也可以在界面的**偏好设定**中设置个人专属的 API 密钥（BYOK 模式）。

#### `config.show_grok_build`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，偏好设定中的 AI 后端列表会包含 `grok (Grok Build subscription)`。当为 `False` 时，该选项隐藏。该订阅来自通过 `grokbuildstreaming` 软件包已登录的 `grok login` 会话，不需要 API 密钥。
* **示例**：
  ```python
  config.show_grok_build=True
  ```

#### `config.use_grok_build_for_default`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，将 AI 后端保留为 `default` 的用户将接收来自已登录 Grok Build 订阅的流式回复。当为 `False` 时，`default` 会保持服务器的 `config.ai_backend` 设定，或者在该值为空时使用内置后端。选择特定后端的用户将继续使用该后端。若下方多个 `use_*_for_default` 标记均为 `True`，则优先使用 grok，其次是 claude，最后是 antigravity。
* **示例**：
  ```python
  config.use_grok_build_for_default=True
  ```

#### `config.show_claude_code`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，偏好设定中的 AI 后端列表会包含 `claude (Claude Code subscription)`。当为 `False` 时，该选项隐藏。该订阅来自通过 `claudecodestreaming` 软件包已登录的 `claude auth login` 会话，不需要 API 密钥。
* **示例**：
  ```python
  config.show_claude_code=True
  ```

#### `config.use_claude_code_for_default`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，将 AI 后端保留为 `default` 的用户将接收来自已登录 Claude Code 订阅的流式回复。当为 `False` 时，`default` 会保持服务器的 `config.ai_backend` 设定，或者在该值为空时使用内置后端。选择特定后端的用户将继续使用该后端。若 `config.use_grok_build_for_default` 同时也为 `True`，则优先使用 grok。
* **示例**：
  ```python
  config.use_claude_code_for_default=True
  ```

#### `config.show_antigravity`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，偏好设定中的 AI 后端列表会包含 `antigravity (Antigravity subscription)`。当为 `False` 时，该选项隐藏。该订阅来自通过 `antigravitystreaming` 软件包已登录的 Antigravity CLI (`agy`) 会话，不需要 API 密钥。
* **示例**：
  ```python
  config.show_antigravity=True
  ```

#### `config.use_antigravity_for_default`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，将 AI 后端保留为 `default` 的用户将接收来自已登录 Antigravity CLI 的流式回复。当为 `False` 时，`default` 会保持服务器的 `config.ai_backend` 设定，或者在该值为空时使用内置后端。选择特定后端的用户将继续使用该后端。若 `config.use_grok_build_for_default` 或 `config.use_claude_code_for_default` 亦为 `True`，则会优先使用前面的选项。
* **示例**：
  ```python
  config.use_antigravity_for_default=True
  ```

#### `config.embedding_model`
* **类型**：`str`
* **默认值**：`"paraphrase-multilingual"`
* **说明**：用于生成向量嵌入（Vector Embeddings）的 sentence-transformer 模型，用于语义圣经搜索与主题索引功能。
* **示例**：
  ```python
  config.embedding_model="paraphrase-multilingual"
  ```

---

### 3. 访问控制与令牌

#### `config.custom_token`
* **类型**：`str`
* **默认值**：`""`
* **说明**：由服务器管理员设置的主访问令牌（Token）。在应用程序偏好设定中输入此令牌（或通过 URL 查询参数 `?custom_token=YOUR_TOKEN`）的用户，可以访问自定义资源（保存在 `~/biblemate/data_custom` 中）并绕过服务器速率限制。自定义参考书籍可放置在 `~/biblemate/data_custom/books`（详见[书籍指南](../tools/tool_books.md)）。
* **示例**：
  ```python
  config.custom_token="my-secret-community-token-2026"
  ```
* **用户如何使用**：
  1. 将令牌字符串分享给授权用户。
  2. 用户在 Web 应用程序中前往**偏好设定** -> **用户与自定义数据** -> **自定义 Token** 进行输入。
  3. 详细说明请参阅[自定义 Token 指南](../user_preferences/custom_token.md)。

#### `config.disable_local_api_endpoint`
* **类型**：`bool`
* **默认值**：`True`
* **说明**：安全性设定。当为 `True` 时，禁止 Web 界面用户指定本地 API 端点（如 `http://localhost:11434` 或 `http://127.0.0.1:5000`）进行 AI 流式传输。这能保护公开部署的服务器免受服务器端请求伪造（SSRF）攻击。
* **示例**：
  ```python
  config.disable_local_api_endpoint=True
  ```

---

### 4. 使用限制与模式控制

#### `config.disable_agent_mode`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，对全体普通用户禁用整个应用程序中的**代理模式**。（通过 BYOK 提供自带 API 密钥或提供有效 `custom_token` 的用户仍可访问代理模式）。
* **示例**：
  ```python
  config.disable_agent_mode=False
  ```

#### `config.disable_partner_mode`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，对普通用户禁用**伙伴模式**。
* **示例**：
  ```python
  config.disable_partner_mode=False
  ```

#### `config.limit_agent_mode_once_daily`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，限制普通用户每天只能运行一次**代理模式**。提供自带 API 密钥或输入有效 `custom_token` 的用户不受此限制。
* **示例**：
  ```python
  config.limit_agent_mode_once_daily=True
  ```

#### `config.limit_partner_mode_once_daily`
* **类型**：`bool`
* **默认值**：`False`
* **说明**：当为 `True` 时，限制普通用户每天只能运行一次**伙伴模式**。提供自带 API 密钥或输入有效 `custom_token` 的用户不受此限制。
* **示例**：
  ```python
  config.limit_partner_mode_once_daily=True
  ```

---

### 5. Google Drive 笔记同步 (OAuth 2.0)

这些设定用于启用个人圣经研经笔记与 Google Drive 的同步。

#### `config.google_client_id`
* **类型**：`str`
* **默认值**：`""`
* **说明**：Google Cloud Console 所核发的 OAuth 2.0 客户端 ID（Client ID）。
* **示例**：
  ```python
  config.google_client_id="123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
  ```

#### `config.google_client_secret`
* **类型**：`str`
* **默认值**：`""`
* **说明**：与您的 `google_client_id` 对应的 OAuth 2.0 客户端密钥（Client Secret）。
* **示例**：
  ```python
  config.google_client_secret="GOCSPX-sample_client_secret_xyz123456789"
  ```

#### `config.auth_uri`
* **类型**：`str`
* **默认值**：`""`
* **说明**：显式覆盖的 OAuth 2.0 重定向 URI。若留空 `""`，BibleMate Web 会根据连入的 Web 请求自动构建回调网址（例如 `http://localhost:33355/auth`）。如果您在 Nginx/Apache 反向代理或自定义 HTTPS 域名后方运行，请显式指定此项。
* **示例**：
  ```python
  config.auth_uri="https://biblemate.example.com/auth"
  ```

* **如何获取 Google OAuth 凭据**：
  1. 打开 [Google Cloud Console](https://console.cloud.google.com/)。
  2. 创建新项目（例如 `"BibleMate AI"`）。
  3. 前往 **API 与服务** -> **库**，搜索 **Google Drive API**，然后点击**启用**。
  4. 配置 **OAuth 同意屏幕**（选择用户类型：*外部*，并在测试用户下添加您的电子邮件）。
  5. 前往**凭据** -> **创建凭据** -> **OAuth 2.0 客户端 ID**。
  6. 选择应用程序类型：**Web 应用程序**。
  7. 在**已授权的重定向 URI** 下，添加 `http://localhost:33355/auth` 和 `http://127.0.0.1:33355/auth`（或您的等效域名）。
  8. 将生成的**客户端 ID** 与**客户端密钥**复制到您的配置文件中。
  9. 有关详细分步指南，请参阅 [Google Drive 笔记设定指南](google_drive_notes_setup.md)。

---

### 6. 数据查询限制

#### `config.verses_limit`
* **类型**：`int`
* **默认值**：`2000`
* **说明**：单次搜索或查询执行所返回的圣经经文数量上限，以防止高内存占用和 UI 卡顿。
* **示例**：
  ```python
  config.verses_limit=2000
  ```

---

## 测试与验证设定

1. 使用所需的配置值编辑 `~/biblemate/biblemateweb.config`。
2. 保存文件。
3. 启动或重启 BibleMate Web：
   ```bash
   biblemateweb
   ```
4. 打开浏览器并前往：
   ```
   http://localhost:33355
   ```
5. 检查终端控制台日志，确认服务器在您指定的端口上启动且无错误。

---

## 相关文档

- [自带密钥 (BYOK) 设定](../user_preferences/api_key_setup.md)
- [自定义访问令牌](../user_preferences/custom_token.md)
- [Google Drive 笔记 OAuth 设定](google_drive_notes_setup.md)
- [API 查询语法](../api/api_query.md)

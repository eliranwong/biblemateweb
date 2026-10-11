# BibleMate Web Configuration Guide

This guide provides a detailed reference for configuring BibleMate Web using the `~/biblemate/biblemateweb.config` configuration file.

---

## Overview

BibleMate Web stores server-wide settings in a configuration file located at:

```
~/biblemate/biblemateweb.config
```

*(Full path: `/home/<username>/biblemate/biblemateweb.config`)*

### Key Characteristics:
* **Automatic Creation**: If the configuration file does not exist, BibleMate Web creates it automatically with default values on its first launch.
* **File Format**: The file uses Python assignment syntax (e.g. `config.port=33355`).
* **Automatic Migration**: When upgrading BibleMate Web, any newly added configuration options are automatically merged into your `biblemateweb.config` file without overwriting your existing settings.
* **Applying Changes**: Whenever you modify `biblemateweb.config`, you must restart the `biblemateweb` process for changes to take effect.

---

## Complete Configuration Sample

Below is a complete sample configuration file using standard defaults and sample keys. **Do not put actual production secret keys in shared version control.**

```python
config.hot_reload=False
config.avatar=""
config.ai_backend=""
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

## Detailed Option Reference

### 1. Core & Server Settings

#### `config.port`
* **Type**: `int`
* **Default**: `33355`
* **Description**: Specifies the TCP network port on which the web server listens.
* **Example**:
  ```python
  config.port=33355
  ```

#### `config.storage_secret`
* **Type**: `str`
* **Default**: `"REPLACE_ME_WITH_A_REAL_SECRET"`
* **Description**: Secret key used for session encryption and browser state management in NiceGUI. **Crucial for security when deploying publicly.**
* **Example**:
  ```python
  config.storage_secret="4a8f9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
  ```
* **How to Obtain / Generate**:
  Run either of the following commands in your terminal:
  - Using OpenSSL:
    ```bash
    openssl rand -hex 32
    ```
  - Using Python:
    ```bash
    python3 -c "import secrets; print(secrets.token_hex(32))"
    ```

#### `config.hot_reload`
* **Type**: `bool`
* **Default**: `False`
* **Description**: Enables auto-reload mode during development. When `True`, server restarts automatically when source files change.
* **Example**:
  ```python
  config.hot_reload=False
  ```

#### `config.avatar`
* **Type**: `str`
* **Default**: `""`
* **Description**: Absolute path to a custom image file to use as the application favicon/avatar. If left empty, the application uses its default icon.
* **Example**:
  ```python
  config.avatar="/home/user/images/my_custom_logo.png"
  ```

---

### 2. AI & Embedding Configuration

#### `config.ai_backend`
* **Type**: `str`
* **Default**: `""`
* **Description**: Specifies the default server-side AI provider backend (e.g. `"googleai"`, `"openai"`, `"anthropic"`, `"groq"`, `"ollama"`, `"deepseek"`, `"grok"`). If empty, the system falls back to its internal default. `"grok"` streams from the signed-in Grok Build CLI (`grok login`) through the `grokbuildstreaming` package and does not use an API key. A user who selects another backend and saves an API key still uses that backend.
* **Example**:
  ```python
  config.ai_backend="googleai"
  ```
* **How to Obtain API Keys**:
  - **Google Gemini (Free tier available)**:
    1. Visit [Google AI Studio](https://aistudio.google.com/).
    2. Click **Get API Key** -> **Create API Key**.
    3. Copy your key. (See [API Key Setup Guide](api_key_setup.md)).
  - **OpenAI**:
    1. Log in to [OpenAI Platform](https://platform.openai.com/api-keys).
    2. Click **Create new secret key**.
  - **Anthropic (Claude)**:
    1. Sign in to [Anthropic Console](https://console.anthropic.com/).
    2. Go to **API Keys** and generate a new key.
  - **Groq**:
    1. Sign in to [Groq Console](https://console.groq.com/keys).
    2. Create an API key.
  - **Ollama (Local AI)**:
    1. Install and run `ollama serve` on your local machine (no API key required).
  - *Note*: Individual users can also set their own personal API key in the UI under **Preferences** (BYOK model).

#### `config.embedding_model`
* **Type**: `str`
* **Default**: `"paraphrase-multilingual"`
* **Description**: The sentence-transformer model used for generating vector embeddings used in semantic Bible search and topical index features.
* **Example**:
  ```python
  config.embedding_model="paraphrase-multilingual"
  ```

---

### 3. Access Control & Tokens

#### `config.custom_token`
* **Type**: `str`
* **Default**: `""`
* **Description**: A master access token defined by the server administrator. Users who enter this token in their app Preferences (or via URL query string `?custom_token=YOUR_TOKEN`) gain access to custom resources (stored in `~/biblemate/data_custom`) and bypass server rate limits.
* **Example**:
  ```python
  config.custom_token="my-secret-community-token-2026"
  ```
* **How Users Use It**:
  1. Share the token string with authorized users.
  2. Users enter it in the web app under **Preferences** -> **User & Custom Data** -> **Custom Token**.
  3. See [Custom Token Guide](custom_token.md) for details.

#### `config.disable_local_api_endpoint`
* **Type**: `bool`
* **Default**: `True`
* **Description**: Security setting. When `True`, prevents web interface users from specifying local API endpoints (such as `http://localhost:11434` or `http://127.0.0.1:5000`) for AI streaming. This protects public server deployments against Server-Side Request Forgery (SSRF) attacks.
* **Example**:
  ```python
  config.disable_local_api_endpoint=True
  ```

---

### 4. Usage Limits & Mode Controls

#### `config.disable_agent_mode`
* **Type**: `bool`
* **Default**: `False`
* **Description**: When `True`, disables access to **Agent Mode** across the application for general users. (Users who supply their own API key via BYOK or present a valid `custom_token` can still access Agent Mode).
* **Example**:
  ```python
  config.disable_agent_mode=False
  ```

#### `config.disable_partner_mode`
* **Type**: `bool`
* **Default**: `False`
* **Description**: When `True`, disables access to **Partner Mode** for general users.
* **Example**:
  ```python
  config.disable_partner_mode=False
  ```

#### `config.limit_agent_mode_once_daily`
* **Type**: `bool`
* **Default**: `False`
* **Description**: When `True`, limits general users to running **Agent Mode** only once per day. Users providing their own API key or entering a valid `custom_token` bypass this restriction.
* **Example**:
  ```python
  config.limit_agent_mode_once_daily=True
  ```

#### `config.limit_partner_mode_once_daily`
* **Type**: `bool`
* **Default**: `False`
* **Description**: When `True`, limits general users to running **Partner Mode** only once per day. Users providing their own API key or entering a valid `custom_token` bypass this restriction.
* **Example**:
  ```python
  config.limit_partner_mode_once_daily=True
  ```

---

### 5. Google Drive Notes Sync (OAuth 2.0)

These settings enable personal Bible study notes synchronization with Google Drive.

#### `config.google_client_id`
* **Type**: `str`
* **Default**: `""`
* **Description**: The OAuth 2.0 Client ID issued by Google Cloud Console.
* **Example**:
  ```python
  config.google_client_id="123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com"
  ```

#### `config.google_client_secret`
* **Type**: `str`
* **Default**: `""`
* **Description**: The OAuth 2.0 Client Secret corresponding to your `google_client_id`.
* **Example**:
  ```python
  config.google_client_secret="GOCSPX-sample_client_secret_xyz123456789"
  ```

#### `config.auth_uri`
* **Type**: `str`
* **Default**: `""`
* **Description**: Explicit OAuth 2.0 redirect URI override. If left empty `""`, BibleMate Web automatically constructs the callback URL based on incoming web requests (e.g. `http://localhost:33355/auth`). Specify this explicitly if you run behind an Nginx/Apache reverse proxy or custom HTTPS domain.
* **Example**:
  ```python
  config.auth_uri="https://biblemate.example.com/auth"
  ```

* **How to Obtain Google OAuth Credentials**:
  1. Open the [Google Cloud Console](https://console.cloud.google.com/).
  2. Create a new project (e.g., `"BibleMate AI"`).
  3. Navigate to **APIs & Services** -> **Library**, search for **Google Drive API**, and click **Enable**.
  4. Configure the **OAuth Consent Screen** (Select User Type: *External* and add your email under Test Users).
  5. Go to **Credentials** -> **Create Credentials** -> **OAuth 2.0 Client ID**.
  6. Select Application Type: **Web Application**.
  7. Under **Authorized redirect URIs**, add `http://localhost:33355/auth` and `http://127.0.0.1:33355/auth` (or your domain equivalent).
  8. Copy the generated **Client ID** and **Client Secret** into your config file.
  9. For a step-by-step walkthrough, see [Google Drive Notes Setup Guide](google_drive_notes_setup.md).

---

### 6. Data Query Limits

#### `config.verses_limit`
* **Type**: `int`
* **Default**: `2000`
* **Description**: Maximum number of Bible verses returned in a single search or query execution to prevent high memory usage and UI slowdowns.
* **Example**:
  ```python
  config.verses_limit=2000
  ```

---

## Testing & Verifying Your Setup

1. Edit `~/biblemate/biblemateweb.config` with your desired configuration values.
2. Save the file.
3. Start or restart BibleMate Web:
   ```bash
   biblemateweb
   ```
4. Open your browser and navigate to:
   ```
   http://localhost:33355
   ```
5. Check your console logs to confirm that the server started on your specified port and without errors.

---

## Related Documentation

- [Bring Your Own Key (BYOK) Setup](api_key_setup.md)
- [Custom Access Tokens](custom_token.md)
- [Google Drive Notes OAuth Setup](google_drive_notes_setup.md)
- [API Query Syntax](api_query.md)

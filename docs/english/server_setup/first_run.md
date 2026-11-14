# First Run

1. **Storage secret** – for anything beyond local testing, generate one and put it in `~/biblemate/biblemateweb.config`:
   ```bash
   openssl rand -hex 32
   ```
   ```python
   config.storage_secret="your-generated-secret"
   ```
   It protects the per-user browser storage ([Security](security_and_deployment.md)).
2. **AI backend** (optional) – the administrator can set `config.ai_backend`; users can use their own key in [Preferences](../user_preferences/README.md) ([BYOK](../user_preferences/api_key_setup.md)).
3. **Port / avatar** – `config.port` (default 33355), `config.avatar`.
4. **Restart** after editing the config.
5. Open <http://localhost:33355> and follow the [Basics guide](../basics/README.md).

All options: [Configuration Guide](configuration.md).

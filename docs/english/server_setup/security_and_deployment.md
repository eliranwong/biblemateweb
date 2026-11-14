# Security & Deployment

## Checklist for public servers

- Set a secure `config.storage_secret`.
- Serve over HTTPS using a reverse proxy (Nginx, Apache, Caddy).
- Restrict Agent/Partner modes (`config.disable_*`, `config.limit_*_once_daily`) – see [Usage Limits](../ai_features/usage_limits.md).
- Keep `config.disable_local_api_endpoint=True` to block SSRF through user-supplied local API endpoints.
- Set `config.verses_limit` to prevent excessive queries.
- Restrict Google OAuth redirect URIs ([guide](google_drive_notes_setup.md)).
- Use `config.custom_token` for private resources.

## Data privacy

The server stores no user accounts. Preferences live in the browser ([User Data & Storage](../user_preferences/user_data_and_storage.md)); notes live in the user's own Google Drive.

## Hosting options

Standalone with a process manager ([Running the Server](running_the_server.md)), reverse proxy, or cloud hosting. See the [NiceGUI deployment guide](https://nicegui.io/documentation/section_configuration_deployment#server_hosting).

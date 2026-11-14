# Google Login (google_token)

Not a setting you edit: this key holds the token created when you log in with Google (`/login` → `/auth`). It enables [Google Drive notes](../integrations/google_drive_notes.md) and per-user daily limit tracking ([Usage Limits](../ai_features/usage_limits.md)).

- Stored in your browser storage only.
- Removed by `Reset All Preferences` ([User Data & Storage](user_data_and_storage.md)).
- Requires the administrator to configure `config.google_client_id` and `config.google_client_secret` ([setup](../server_setup/google_drive_notes_setup.md)).

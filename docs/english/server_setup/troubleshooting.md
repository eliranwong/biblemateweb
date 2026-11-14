# Troubleshooting

| Problem | Things to check |
|---|---|
| No Bibles or empty menus | Run `biblematedata`; verify files in `~/biblemate/data` ([Data & Resources](data_and_resources.md)) |
| Semantic search fails | [Ollama set up](semantic_search_setup.md), model pulled, vectors present |
| DOCX download fails | Install `pandoc` ([guide](docx_export.md)) |
| Google login fails | Redirect URIs and `config.auth_uri` ([setup](google_drive_notes_setup.md)) |
| Agent/Partner shows CLI-only page | `config.disable_*` is set; enter your own API key ([Usage Limits](../ai_features/usage_limits.md)) |
| AI gives no answer | Check [AI backend, key and model](../ai_features/ai_backends.md) |
| Config changes ignored | Restart the server |
| Strange display or stuck state | Use `Reset All Preferences` ([User Data & Storage](../user_preferences/user_data_and_storage.md)) |
| Custom Bibles missing | Enter the [custom token](../user_preferences/custom_token.md) |
| Port already in use | Change `config.port` or stop the other process |
| Works locally, not remotely | Firewall/reverse proxy; Google OAuth redirect |

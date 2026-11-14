# Routes & Endpoints

| Route | Type | Description |
|---|---|---|
| `/` | Page | Main app. Accepts [URL parameters](../layout/url_parameters.md) |
| `/settings` | Page | [Preferences](../user_preferences/README.md). Accepts `t` (custom token for this visit) |
| `/login` | Page | Starts Google sign-in (for [notes](../integrations/google_drive_notes.md) and limits) |
| `/auth` | Page | Google OAuth callback; stores the token in your browser session and returns to `/` |
| `/api/data` | REST | Query Bible data – [REST API](../integrations/rest_api.md), [API Query](api_query.md) |
| `/api/tooltip/{word}` | REST | Tooltip data – [Word Tooltips](../integrations/word_tooltips.md) |

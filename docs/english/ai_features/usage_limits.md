# Usage Limits & Availability

Administrators control access to the heavier AI modes via the server configuration (`~/biblemate/biblemateweb.config`; see [Configuration](../server_setup/configuration.md)).

| Setting | Effect |
|---|---|
| `config.disable_agent_mode` | Agent Mode shows a CLI-only information page |
| `config.disable_partner_mode` | Partner Mode shows a CLI-only information page |
| `config.limit_agent_mode_once_daily` | Agent Mode limited to once per day |
| `config.limit_partner_mode_once_daily` | Partner Mode limited to once per day |

## Bypass

- Disabled modes become available if you enter your own API key.
- Daily limits do not apply if you have a valid [custom token](../user_preferences/custom_token.md) or your own [API key](../user_preferences/api_key.md).

When a daily limit applies, you may be asked to log in with Google so usage can be tracked; your data stays in your own Google account. Once the limit is reached, a message explains how to remove it via Preferences.

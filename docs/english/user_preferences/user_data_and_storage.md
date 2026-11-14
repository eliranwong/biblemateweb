# User Data & Storage

## Where preferences live

Your preferences are saved in NiceGUI's per-user browser storage, tied to the server's `config.storage_secret`. There are **no user accounts** on the server, and the server does not keep your personal notes.

## What is stored

- **Settings** – everything listed in the [index](README.md).
- **Tab state** – each Bible and tool tab (`tab1_*`, `tab2_*`): content, label, book/chapter/verse and query. Tabs are restored on your next visit ([Tabs Management](../layout/tabs_management.md)).
- **Working values** – `bible_*` and `tool_*` book/chapter/verse/query used to pass context between windows.
- **Google token** – if you log in with Google (`google_token`) for [Drive notes](../integrations/google_drive_notes.md).
- **Custom token** – `custom_token` ([guide](custom_token.md)).

## Not stored

- A custom token passed in the URL with `?t=` is used for that visit only (useful on public devices).

## Reset

`Preferences` → `Reset All Preferences` → `Delete` clears everything and returns to the home page. Clearing browser data has the same effect.

## Moving between devices

Preferences do not sync. Notes do, through Google Drive. Use [shareable links](../integrations/sharing_deep_links.md) to carry a view to another device.

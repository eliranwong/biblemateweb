# Reusable Dialogs

In `dialogs/`:

| Dialog | Use |
|---|---|
| `ReviewDialog` | Edit text: `await ReviewDialog().open_with_text(text, label="Edit")` returns edited text or `None` if cancelled |
| `SelectionDialog(big=False)` | Choose one option: `await SelectionDialog().open_with_options(options, title)` returns the selection or `None` |
| `FilenameDialog` | `await FilenameDialog().open_with_filename("name")` returns a filename |

Also `fx/bible_selection_dialog.py`: the book/chapter/verse picker behind the [Go button](../layout/bible_selection_dialog.md).

User view: [Review](../ai_features/chat_review.md), [Partner Mode](../ai_features/partner_mode.md).

# Chat Mode

A conversational assistant for questions about the Bible: verses, historical context, topics and more.

## Open

- **AI** menu → `AI Chat`
- Right-click a verse or chapter → `Ask BibleMate` ([guide](ask_biblemate.md)), which pre-fills your question.

## Using it

1. Type your request in the text box.
2. Press **Send** or **Shift+Enter**.
3. The answer streams in as formatted text. Each round is remembered, so you can ask follow-ups.
4. While a task runs, the Send button becomes **Stop**; confirm to cancel.

## Pipeline

Depending on the checkboxes below the input, each request goes through:

1. [Prompt Engineering](prompt_engineering.md) (`Enhance`) – optional
2. [Tool Selection](chat_tool_selection.md) (`Tools`) – optional
3. Response, optionally with the [Agent](chat_agent_option.md) option
4. [Review](chat_review.md) points – optional

## Controls

| Control | Purpose |
|---|---|
| Auto-scroll | Follow the output as it streams (`auto_scroll`) |
| Enhance | `prompt_engineering` (default On) |
| Agent | `use_agent` (default On) |
| Tools | `auto_tool_selection` (default Off) |
| Review | `chat_mode_review` (default Off) |

Checkbox states are saved with your preferences.

## Other actions

[Copy, download, edit and export](export_edit_responses.md). Buttons at the bottom of the welcome message switch to [Partner Mode](partner_mode.md) or [Agent Mode](agent_mode.md).

## Requirements

Uses your configured [AI backend](ai_backends.md).

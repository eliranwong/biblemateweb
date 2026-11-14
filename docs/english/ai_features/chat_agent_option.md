# Agent Option (Chat Mode)

The `Agent` checkbox lets BibleMate create helper agents to produce more detailed, better-reasoned answers (tooltip: "Create agents to improve responses").

| | |
|---|---|
| Key | `use_agent` |
| Default | On |

## Behaviour

- When a plain text answer is generated with the option on, an **Agent** panel shows the agent working, followed by the answer.
- When off, the AI answers directly with a single response (faster, cheaper).
- Some specialist [tools](chat_tool_selection.md) use agents automatically regardless of this setting.

This is different from [Agent Mode](agent_mode.md), which is a separate page for multi-round tasks.

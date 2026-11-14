# Review

When enabled, the AI pauses at key points so you can approve, edit or cancel before it continues.

| | |
|---|---|
| Where | `Review` checkbox in Chat Mode |
| Key | `chat_mode_review` |
| Default | Off |

## Review points

- **Improved prompt** (if [Enhance](prompt_engineering.md) is on): edit the rewritten prompt.
- **Tool choice** (if [Tools](chat_tool_selection.md) is on): choose from suggested tools; `More...` lists all.
- **Tool instruction**: edit the instruction before running.

Cancelling at any dialog stops that request and shows `[Cancelled!]`.

In [Partner Mode](partner_mode.md), these review steps are always on. In [Agent Mode](agent_mode.md) they never appear.

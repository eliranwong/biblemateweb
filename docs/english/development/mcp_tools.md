# AI Tool Definitions (MCP)

`mcp_tools/` defines what the AI can call:

| File | Purpose |
|---|---|
| `elements.py` | `TOOL_ELEMENTS`: tool name → API query prefix (data tools, e.g. `"verses:::"`) or dict with `system` / `instruction` (AI tools) |
| `tools.py` | `TOOLS`: tool name → short description used for tool selection |
| `tools_schema.py` | Tool schemas |
| `tool_descriptions.py` | Descriptions shown to the model/user |
| `system_tool_selection_*.md` | Prompts for tool selection (`mini` is used by Chat) |

Data tools run `get_api_content(prefix + request)`; AI tools stream a response using an agentmake system or instruction. See the user view: [Tool Selection](../ai_features/chat_tool_selection.md).

To add a tool: add an entry to `TOOL_ELEMENTS`, describe it in the selection prompts and `tool_descriptions.py`.

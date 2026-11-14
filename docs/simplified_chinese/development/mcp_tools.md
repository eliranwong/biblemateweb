# AI 工具定义 (MCP)

`mcp_tools/` 定义了 AI 可以调用的内容：

| 文件 | 用途 |
|---|---|
| `elements.py` | `TOOL_ELEMENTS`：工具名称 → API 查询前缀（数据工具，例如 `"verses:::"`）或包含 `system` / `instruction` 的字典（AI 工具） |
| `tools.py` | `TOOLS`：工具名称 → 用于选择工具的简短描述 |
| `tools_schema.py` | 工具架构 (Schemas) |
| `tool_descriptions.py` | 显示给模型／用户的描述 |
| `system_tool_selection_*.md` | 选择工具的提示词（`mini` 供对话模式使用） |

数据工具运行 `get_api_content(prefix + request)`；AI 工具则使用 agentmake 系统或指示流式传输响应。请参阅用户视角：[选择工具](../ai_features/chat_tool_selection.md)。

若要添加工具：在 `TOOL_ELEMENTS` 中添加一个条目，并在选择工具提示词与 `tool_descriptions.py` 中进行描述。

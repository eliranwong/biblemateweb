# AI 工具定義 (MCP)

`mcp_tools/` 定義了 AI 可以呼叫的內容：

| 檔案 | 用途 |
|---|---|
| `elements.py` | `TOOL_ELEMENTS`：工具名稱 → API 查詢前綴（資料工具，例如 `"verses:::"`）或包含 `system` / `instruction` 的字典（AI 工具） |
| `tools.py` | `TOOLS`：工具名稱 → 用於選用工具的簡短描述 |
| `tools_schema.py` | 工具綱要 (Schemas) |
| `tool_descriptions.py` | 顯示給模型／使用者的描述 |
| `system_tool_selection_*.md` | 選用工具的提示詞（`mini` 供對話模式使用） |

資料工具執行 `get_api_content(prefix + request)`；AI 工具則使用 agentmake 系統或指示串流回傳回應。請參閱使用者視角：[選用工具](../ai_features/chat_tool_selection.md)。

若要新增工具：在 `TOOL_ELEMENTS` 中新增一個項目，並在選用工具提示詞與 `tool_descriptions.py` 中進行描述。

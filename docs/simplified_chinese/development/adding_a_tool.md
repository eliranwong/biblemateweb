# 添加工具或页面

1. 在 `pages/tools/`（或 `search/`、`bibles/`）中创建模块并定义函数：
   ```python
   def my_tool(gui=None, b=1, c=1, v=1, q="", area=2, tab1=None, tab2=None, **_):
       ...  # build NiceGUI elements; they render into the active tab
   ```
2. 在 `pages/home.py` 中导入它，并将关键字添加到 `self.tools`：
   ```python
   "mytool": my_tool,
   ```
3. 在 `create_menu()` 中添加菜单项：
   ```python
   ui.menu_item(get_translation("My Tool"), on_click=lambda: self.load_area_2_content(title='MyTool', sync=True))
   ```
   使用 `sync=True` 可在当前经文处开启；独立工具则使用 `False`。
4. 添加翻译（[语言翻译](translations.md)）。
5. 使用 `gui.update_active_area2_tab_records(...)` 持久化标签页状态，并通过 `app.storage.user['tool_query']` 接收来自快速搜索的查询。
6. 可选择性通过 API（`api/api.py`）与 AI 工具（[MCP 工具](mcp_tools.md)）公开它。
7. 在 `docs/tools/` 中编写相关文档，并从 [研经工具](../tools/README.md) 建立链接。

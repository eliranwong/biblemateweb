# 新增工具或頁面

1. 在 `pages/tools/`（或 `search/`、`bibles/`）中建立模組並定義函式：
   ```python
   def my_tool(gui=None, b=1, c=1, v=1, q="", area=2, tab1=None, tab2=None, **_):
       ...  # build NiceGUI elements; they render into the active tab
   ```
2. 在 `pages/home.py` 中匯入它，並將關鍵字新增至 `self.tools`：
   ```python
   "mytool": my_tool,
   ```
3. 在 `create_menu()` 中新增選單項目：
   ```python
   ui.menu_item(get_translation("My Tool"), on_click=lambda: self.load_area_2_content(title='MyTool', sync=True))
   ```
   使用 `sync=True` 可在目前經文處開啟；獨立工具則使用 `False`。
4. 新增翻譯（[語言翻譯](translations.md)）。
5. 使用 `gui.update_active_area2_tab_records(...)` 保存標籤頁狀態，並透過 `app.storage.user['tool_query']` 接收來自快速搜索的查詢。
6. 可選擇性透過 API（`api/api.py`）與 AI 工具（[MCP 工具](mcp_tools.md)）公開它。
7. 在 `docs/tools/` 中撰寫相關文檔，並從 [研經工具](../tools/README.md) 建立連結。

# Adding a Tool or Page

1. Create a module in `pages/tools/` (or `search/`, `bibles/`) with a function:
   ```python
   def my_tool(gui=None, b=1, c=1, v=1, q="", area=2, tab1=None, tab2=None, **_):
       ...  # build NiceGUI elements; they render into the active tab
   ```
2. Import it in `pages/home.py` and add a keyword to `self.tools`:
   ```python
   "mytool": my_tool,
   ```
3. Add a menu item in `create_menu()`:
   ```python
   ui.menu_item(get_translation("My Tool"), on_click=lambda: self.load_area_2_content(title='MyTool', sync=True))
   ```
   Use `sync=True` to open at the current verse; `False` for independent tools.
4. Add translations ([Translations](translations.md)).
5. Use `gui.update_active_area2_tab_records(...)` to persist tab state, and `app.storage.user['tool_query']` to receive queries from quick search.
6. Optionally expose it through the API (`api/api.py`) and AI tools ([MCP Tools](mcp_tools.md)).
7. Document it in `docs/tools/` and link from [Study Tools](../tools/README.md).

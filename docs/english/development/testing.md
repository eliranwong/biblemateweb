# Testing & Prototypes

There is no unified test runner. `tests/` holds standalone scripts that prototype or demonstrate features (tabs, sync scrolling, context menus, tooltips, indexes, notes, search modes, subscription backends, API client ...). Run one directly:

```bash
python tests/api_client.py
```

Many are NiceGUI demos: run the script and open the printed URL. `tests/sync_scrolling.md` explains the synchronised scrolling design ([user view](../integrations/synchronised_windows.md)).

Manual checks before release: start `biblemateweb`, open Bible/tool tabs, run a verse search in each mode, try the [API](../integrations/rest_api.md), and test mobile layout.

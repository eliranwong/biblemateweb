# Project Structure

```
biblemateweb/
├── README.md, README_pypi.md, CLAUDE.md
├── docs/                    documentation
├── scripts/                 startup.sh, promises_indexes.py
├── tests/                   prototypes and experiments
└── package/
    ├── setup.py             entry points: biblemateweb, bmweb, biblemategui, biblemateapi, bmapi
    └── biblemateweb/
        ├── main.py          NiceGUI pages: /, /settings, /login, /auth; REST routes
        ├── __init__.py      config, defaults, resource discovery, helpers
        ├── api_client.py    biblemateapi command
        ├── api/             query parser and content (api.py)
        ├── pages/
        │   ├── home.py      BibleMateWeb: layout, menus, tabs, sync
        │   ├── ai/          chat, partner, agent, stream (+ *_cli info pages)
        │   ├── bibles/      translation + ORB/OIB/OPB/ODB/OLB
        │   ├── tools/       study tools
        │   ├── search/      search pages
        │   └── teachings/   articles
        ├── fx/              bible.py, original.py, tooltips.py, shared.py, cloud_index_manager.py, location_finder.py, bible_selection_dialog.py
        ├── dialogs/         review, selection, filename dialogs
        ├── mcp_tools/       tool definitions and prompts for AI tool selection
        ├── js/ css/         injected JavaScript and CSS
        ├── data/            bundled reference data (events, locations, timelines, names, lexical)
        ├── translations/    eng.py, tc.py, sc.py
        └── fonts/           Hebrew and Greek fonts
```

User docs: [Documentation index](../README.md).

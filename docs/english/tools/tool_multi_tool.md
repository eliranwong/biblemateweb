# Multi-Tool Workspace

The **Multi-Tool Workspace** lets you open and use multiple study tools and search pages side by side inside a single Tool Area tab, each in its own independent container.

## How to Open

- **Tools menu**: Open the `Tools` menu (`build` icon) or left drawer and select `Multi-Tool Workspace`.
- **Quick Search**: `multitool`

## Features

- **Independent Tool Panes**: Click `+ Add Tool` to add any supported tool, search page, or AI mode (commentary, treasury, cross-references, morphology, indexes, lexicons, dictionaries, verse search, notepad, `AI: Chat Mode`, `AI: Partner Mode`, `AI: Agent Mode`, and `AI: Studio Mode` when available). Each pane has its own scrollable container, tool switcher, and state.
- **Responsive Layout & Height Switchers**: Switch between `1`, `2`, `3`, or `4` columns and `1x`, `1.5x`, `2x`, or `2.5x` pane height in the workspace toolbar. Multi-column layouts automatically fall back to 1 column on narrow or portrait screens, and both choices are saved across reloads (`multitool_cols`, `multitool_height_scale`).
- **Per-Pane Controls**:
  - **Tool Switcher**: Change the tool displayed in that pane without affecting other panes.
  - **Sync Toggle**: Control whether the pane auto-refreshes when the Bible Area changes book, chapter, or verse. Non-synced search panes keep their results untouched.
  - **Refresh**: Manually sync that pane to the Bible Area's current passage.
  - **Move / Maximize / Collapse / Close**: Reorder panes, expand one pane to full width, collapse its body, or close it.
- **Presets & Persistence**:
  - **Remember Last Workspace**: Automatically restores your previous panes and column layout when reopening Multi-Tool Workspace (`multitool_last`).
  - **Built-in Presets**: Load curated setups (*Chapter Study*, *Verse Deep Dive*, *Word & Topic Study*, *Study & Notes*) from the `Presets` menu.
  - **Custom Presets**: Click the save icon to store your current layout and panes as a named custom preset (`multitool_custom_presets`).
- **Safe Link Navigation**: Clicking a tool link inside a pane opens the target tool in a new Tool Area tab so your Multi-Tool Workspace stays intact.

# Layout Overview

The home page is made of:

1. **Header** – avatar/title button, quick search box and the menu buttons: Bibles, Parallel Bibles, Tools, Search, AI and Settings.
2. **Bible Area (Area 1)** – the main reading window, with its own tabs (`Bible 1`, `Bible 2` ...).
3. **Tool Area (Area 2)** – a second window with its own tabs (`Tool 1`, `Tool 2` ...). It hosts parallel Bibles, tools, search results and AI features.
4. **Splitter** – a draggable divider between the two areas.
5. **Floating buttons** – [Swap Layout and Go](floating_buttons.md), draggable anywhere on screen.

## Responsive orientation

The splitter adapts to the browser window: on landscape screens the areas sit **side by side**; on portrait screens (height greater than width, e.g. phones) they are **stacked vertically**.

## Layout modes

| Mode | Value | Visible |
|---|---|---|
| Bible Only | `1` | Area 1 fills the screen |
| Bible & Tool | `2` | Both areas, 50/50 |
| Tool Only | `3` | Area 2 fills the screen |

See [Toggle Layout](toggle_layout.md).

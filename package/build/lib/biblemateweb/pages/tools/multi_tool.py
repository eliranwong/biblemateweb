import copy
import traceback
import uuid
from nicegui import ui, app
from biblemateweb import get_translation
from biblemateweb.pages.ai.agentic_workspace import is_workspace_available


# Curated tools/search pages available as panes inside Multi-Tool Workspace.
# (key in gui.tools, display label, default sync-with-Area-1 flag)
AVAILABLE_PANE_TOOLS = [
    ("commentary", "Bible Commentary", True),
    ("treasury", "Treasury of Scripture Knowledge", True),
    ("xrefs", "Cross References", True),
    ("summary", "Chapter Summary", True),
    ("analysis", "Book Analysis", True),
    ("morphology", "Morphology", True),
    ("chapterindexes", "Chapter Indexes", True),
    ("bookindexes", "Book Indexes", True),
    ("indexes", "Verse Indexes", True),
    ("comparechapter", "Chapter Comparison", True),
    ("timelines", "Bible Timelines", True),
    ("chronology", "Bible Chronology", False),
    ("books", "Books", False),
    ("reading", "Bible Reading Plan", False),
    ("notepad", "Notepad", True),
    ("notes", "Bible Notes", True),
    ("podcast", "Bible Podcast", True),
    ("audio", "Bible Audio", True),
    ("verses", "Search: Verses", False),
    ("lexicons", "Search: Lexicons", False),
    ("dictionaries", "Search: Dictionaries", False),
    ("encyclopedias", "Search: Encyclopedias", False),
    ("topics", "Search: Topics", False),
    ("characters", "Search: Characters", False),
    ("relationships", "Search: Relationships", False),
    ("locations", "Search: Locations", False),
    ("maps", "Search: Maps", False),
    ("names", "Search: Names", False),
    ("parallels", "Search: Parallels", False),
    ("promises", "Search: Promises", False),
    ("chat", "AI: Chat Mode", False),
    ("partner", "AI: Partner Mode", False),
    ("agent", "AI: Agent Mode", False),
    ("studio", "AI: Studio Mode", False),
]

TOOL_DEFAULTS = {key: {"label": label, "sync": sync} for key, label, sync in AVAILABLE_PANE_TOOLS}

BUILTIN_PRESETS = {
    "Chapter Study": {
        "cols": 2,
        "panes": [
            {"tool": "commentary", "sync": True},
            {"tool": "treasury", "sync": True},
            {"tool": "summary", "sync": True},
        ],
    },
    "Verse Deep Dive": {
        "cols": 3,
        "panes": [
            {"tool": "xrefs", "sync": True},
            {"tool": "morphology", "sync": True},
            {"tool": "indexes", "sync": True},
        ],
    },
    "Word & Topic Study": {
        "cols": 3,
        "panes": [
            {"tool": "lexicons", "sync": False},
            {"tool": "dictionaries", "sync": False},
            {"tool": "verses", "sync": False},
        ],
    },
    "Study & Notes": {
        "cols": 2,
        "panes": [
            {"tool": "commentary", "sync": True},
            {"tool": "notepad", "sync": True},
        ],
    },
}


class PaneGuiProxy:
    """Lightweight gui wrapper passed to each tool pane so it stays isolated inside Multi-Tool."""

    def __init__(self, real_gui, pane_state, save_fn, tab2_id):
        self._real_gui = real_gui
        self._pane_state = pane_state
        self._save_fn = save_fn
        self._tab2_id = tab2_id

    def update_active_area2_tab_records(self, title=None, label=None, bt=None, b=None, c=None, v=None, q=None):
        if bt is not None:
            self._pane_state["bt"] = bt
        if b is not None:
            self._pane_state["b"] = b
        if c is not None:
            self._pane_state["c"] = c
        if v is not None:
            self._pane_state["v"] = v
        if q is not None:
            self._pane_state["q"] = q
        self._save_fn()
        app.storage.user["tool_query"] = ""

    def select_empty_area2_tab(self):
        # Never overwrite the multi-tool tab when a pane opens another tool
        if self._real_gui.get_active_area2_tab() == self._tab2_id:
            self._real_gui.add_tab_area2()
        else:
            self._real_gui.select_empty_area2_tab()

    def load_area_2_content(self, content=None, title="Tool", tab=None, args=None, keep=True, sync=True, update_url=True):
        target_tab = tab or self._real_gui.get_active_area2_tab()
        if target_tab == self._tab2_id:
            self._real_gui.add_tab_area2()
            target_tab = self._real_gui.get_active_area2_tab()
        return self._real_gui.load_area_2_content(
            content=content,
            title=title,
            tab=target_tab,
            args=args,
            keep=keep,
            sync=sync,
            update_url=update_url,
        )

    def __getattr__(self, name):
        return getattr(self._real_gui, name)


def _make_pane(tool_key, sync=None, bt=None, b=1, c=1, v=1, q=""):
    default_sync = TOOL_DEFAULTS.get(tool_key, {}).get("sync", False)
    return {
        "id": uuid.uuid4().hex[:8],
        "tool": tool_key,
        "sync": default_sync if sync is None else bool(sync),
        "collapsed": False,
        "maximized": False,
        "bt": bt,
        "b": int(b or 1),
        "c": int(c or 1),
        "v": int(v or 1),
        "q": q or "",
    }


def _snapshot_client_listeners(client):
    """Return current listener counts per event type on the NiceGUI client."""
    counts = {}
    if client is not None and hasattr(client, "_event_listeners"):
        try:
            for ev_type, listeners in client._event_listeners.items():
                counts[ev_type] = len(listeners)
        except Exception:
            pass
    return counts


def _dedupe_new_listeners(client, before_counts, owned_listeners):
    """Replace any previously owned Multi-Tool listener for the same event type to avoid duplicate firing."""
    if client is None or not hasattr(client, "_event_listeners"):
        return
    try:
        for ev_type, listeners in list(client._event_listeners.items()):
            prev_len = before_counts.get(ev_type, 0)
            if len(listeners) > prev_len:
                newly_added = listeners[prev_len:]
                # Remove older listeners for ev_type that were registered by earlier panes in this Multi-Tool tab
                old_owned = owned_listeners.get(ev_type, [])
                if old_owned:
                    client._event_listeners[ev_type] = [l for l in listeners if l not in old_owned]
                owned_listeners[ev_type] = list(newly_added)
    except Exception:
        pass


def multi_tool(gui=None, bt=None, b=1, c=1, v=1, q="", tab2=None, **_):
    """Multi-Tool Workspace: host multiple tools/searches in independent containers within one Area 2 tab."""
    active_tab2 = tab2 or (gui.get_active_area2_tab() if gui else "tab2_1")

    def _area1_bcv():
        if gui:
            tab1 = gui.get_active_area1_tab()
            t1 = app.storage.user.get(tab1, {})
            return (
                t1.get("bt") or gui.get_area_1_bible_text(),
                int(t1.get("b") or app.storage.user.get("bible_book_number", b) or 1),
                int(t1.get("c") or app.storage.user.get("bible_chapter_number", c) or 1),
                int(t1.get("v") or app.storage.user.get("bible_verse_number", v) or 1),
            )
        return bt, int(b or 1), int(c or 1), int(v or 1)

    cur_bt, cur_b, cur_c, cur_v = _area1_bcv()
    if bt:
        cur_bt = bt
    if b:
        cur_b = int(b)
    if c:
        cur_c = int(c)
    if v:
        cur_v = int(v)

    def _find_preset(name):
        if not name:
            return None
        needle = name.strip().lower()
        for k, val in BUILTIN_PRESETS.items():
            if k.lower() == needle:
                return val
        for k, val in (app.storage.user.get("multitool_custom_presets") or {}).items():
            if k.lower() == needle:
                return val
        return None

    # Load workspace state: tab storage -> preset in q -> multitool_last -> default built-in preset
    tab_record = app.storage.user.get(active_tab2)
    q_preset = _find_preset(q)
    saved_ws = None
    if isinstance(tab_record, dict) and isinstance(tab_record.get("panes"), list) and tab_record["panes"]:
        saved_ws = tab_record
    elif q_preset is not None:
        saved_ws = q_preset
    elif isinstance(app.storage.user.get("multitool_last"), dict) and app.storage.user["multitool_last"].get("panes"):
        saved_ws = app.storage.user["multitool_last"]
    else:
        saved_ws = BUILTIN_PRESETS["Chapter Study"]

    saved_cols = (
        saved_ws.get("cols")
        if (q_preset is None or (isinstance(tab_record, dict) and tab_record.get("panes"))) and saved_ws.get("cols") in (1, 2, 3, 4)
        else app.storage.user.get("multitool_cols", saved_ws.get("cols", 2))
    )
    saved_height = (
        saved_ws.get("height_scale")
        if saved_ws.get("height_scale") in (1.0, 1.5, 2.0, 2.5)
        else app.storage.user.get("multitool_height_scale", 1.0)
    )

    state = {
        "cols": int(saved_cols) if saved_cols in (1, 2, 3, 4) else 2,
        "height_scale": float(saved_height) if saved_height in (1.0, 1.5, 2.0, 2.5) else 1.0,
        "panes": [
            _make_pane(
                p.get("tool", "commentary"),
                sync=p.get("sync"),
                bt=p.get("bt") or cur_bt,
                b=p.get("b") if p.get("sync", True) is False else cur_b,
                c=p.get("c") if p.get("sync", True) is False else cur_c,
                v=p.get("v") if p.get("sync", True) is False else cur_v,
                q=p.get("q", ""),
            )
            for p in saved_ws.get("panes", [])
            if gui is None or p.get("tool") in gui.tools
        ],
    }
    if not state["panes"]:
        state["panes"] = [_make_pane("commentary", True, cur_bt, cur_b, cur_c, cur_v)]

    def save_workspace():
        clean_panes = [
            {
                "tool": p["tool"],
                "sync": bool(p.get("sync", False)),
                "bt": p.get("bt"),
                "b": p.get("b", 1),
                "c": p.get("c", 1),
                "v": p.get("v", 1),
                "q": p.get("q", ""),
            }
            for p in state["panes"]
        ]
        app.storage.user["multitool_cols"] = state["cols"]
        app.storage.user["multitool_height_scale"] = state["height_scale"]
        app.storage.user["multitool_last"] = {
            "cols": state["cols"],
            "height_scale": state["height_scale"],
            "panes": copy.deepcopy(clean_panes),
        }
        existing_tab = app.storage.user.get(active_tab2)
        if isinstance(existing_tab, dict):
            existing_tab["cols"] = state["cols"]
            existing_tab["height_scale"] = state["height_scale"]
            existing_tab["panes"] = clean_panes
            app.storage.user[active_tab2] = existing_tab

    save_workspace()

    # Track per-pane containers & event listeners so we can refresh individual panes cleanly
    pane_body_containers = {}
    owned_listeners = {}

    tool_options = {
        key: get_translation(label)
        for key, label, _ in AVAILABLE_PANE_TOOLS
        if (gui is None or key in gui.tools) and (key != "studio" or is_workspace_available())
    }

    def render_pane_body(pane):
        container = pane_body_containers.get(pane["id"])
        if container is None:
            return
        container.clear()
        if pane["tool"] == "studio":
            container.classes(add="book-fill studio-fill")
        else:
            container.classes(remove="book-fill studio-fill")
        if pane.get("collapsed"):
            return
        tool_fn = gui.tools.get(pane["tool"]) if gui else None
        if tool_fn is None:
            with container:
                ui.label(f"Tool not found: {pane['tool']}").classes("text-negative p-4")
            return

        client = ui.context.client
        before_counts = _snapshot_client_listeners(client)
        proxy = PaneGuiProxy(gui, pane, save_workspace, active_tab2)
        tab1 = gui.get_active_area1_tab() if gui else "tab1_1"
        args = {
            "title": pane["tool"].capitalize(),
            "label": pane["tool"].capitalize(),
            "bt": pane.get("bt") or cur_bt,
            "b": pane.get("b", cur_b),
            "c": pane.get("c", cur_c),
            "v": pane.get("v", cur_v),
            "q": pane.get("q", ""),
            "area": 2,
            "tab1": tab1,
            "tab2": active_tab2,
        }
        with container:
            try:
                tool_fn(gui=proxy, **args)
            except Exception as ex:
                print(traceback.format_exc())
                ui.label(f"Error loading {pane['tool']}: {ex}").classes("text-negative p-4")
        _dedupe_new_listeners(client, before_counts, owned_listeners)

    def sync_panes_from_area1(new_b, new_c, new_v):
        new_bt = gui.get_area_1_bible_text() if gui else cur_bt
        changed = False
        for pane in state["panes"]:
            if pane.get("sync"):
                pane["bt"] = new_bt
                pane["b"] = new_b
                pane["c"] = new_c
                pane["v"] = new_v
                render_pane_body(pane)
                changed = True
        if changed:
            save_workspace()

    if gui is not None and hasattr(gui, "_multitool_sync_callbacks"):
        gui._multitool_sync_callbacks[active_tab2] = sync_panes_from_area1

    # --- Top Toolbar ---
    with ui.row().classes("w-full items-center justify-between gap-2 px-3 py-2 border-b flex-wrap"):
        with ui.row().classes("items-center gap-2 flex-wrap"):
            ui.icon("dashboard_customize", size="sm").classes("text-primary")
            ui.label(get_translation("Multi-Tool Workspace")).classes("font-semibold text-base")

            # Add Tool menu button
            with ui.button(f"+ {get_translation('Add Tool')}", icon="add").props("dense outline color=primary"):
                with ui.menu():
                    for key, label in tool_options.items():
                        ui.menu_item(label, on_click=lambda k=key: add_pane(k))

            # Presets menu button (Built-in + Custom)
            presets_btn = ui.button(get_translation("Presets"), icon="bookmarks").props("dense outline")
            presets_menu = ui.menu()

            def rebuild_presets_menu():
                presets_menu.clear()
                with presets_menu:
                    ui.item_label(get_translation("Built-in Presets")).classes("text-xs font-bold opacity-70 px-3 pt-2")
                    for pname, pdata in BUILTIN_PRESETS.items():
                        ui.menu_item(pname, on_click=lambda d=pdata, n=pname: apply_preset(d, n))
                    custom = app.storage.user.get("multitool_custom_presets") or {}
                    if custom:
                        ui.separator()
                        ui.item_label(get_translation("Custom Presets")).classes("text-xs font-bold opacity-70 px-3 pt-2")
                        for pname, pdata in list(custom.items()):
                            with ui.menu_item(on_click=lambda d=pdata, n=pname: apply_preset(d, n)):
                                with ui.row().classes("w-full items-center justify-between gap-3"):
                                    ui.label(pname)
                                    del_btn = ui.button(
                                        icon="delete",
                                        on_click=lambda n=pname: delete_custom_preset(n),
                                    ).props("flat dense round size=xs color=negative")
                                    del_btn.on("click", js_handler="(e) => e.stopPropagation()")

            with presets_btn:
                presets_menu
            presets_btn.on("click", rebuild_presets_menu)

            # Save Custom Preset button
            ui.button(icon="save", on_click=lambda: open_save_preset_dialog()).props("dense flat").tooltip(
                get_translation("Save Current as Preset")
            )

        with ui.row().classes("items-center gap-2 flex-wrap"):
            layout_toggle = ui.toggle(
                {1: "1", 2: "2", 3: "3", 4: "4"},
                value=state["cols"],
                on_change=lambda e: set_layout_cols(e.value),
            ).props("dense outline no-caps").tooltip(get_translation("Columns"))

            height_toggle = ui.toggle(
                {1.0: "1x", 1.5: "1.5x", 2.0: "2x", 2.5: "2.5x"},
                value=state["height_scale"],
                on_change=lambda e: set_height_scale(e.value),
            ).props("dense outline no-caps").tooltip(get_translation("Pane Height"))

            ui.button(
                icon="sync",
                on_click=lambda: sync_panes_from_area1(*_area1_bcv()[1:]),
            ).props("dense flat").tooltip(get_translation("Sync All with Bible"))

    # Grid container for panes
    grid_container = ui.element("div").classes("w-full p-2 gap-3 grid")

    def apply_grid_classes():
        cols = state["cols"]
        grid_container.classes(remove="grid-cols-1 md:grid-cols-2 lg:grid-cols-3 lg:grid-cols-4")
        if cols == 1:
            grid_container.classes(add="grid-cols-1")
        elif cols == 2:
            grid_container.classes(add="grid-cols-1 md:grid-cols-2")
        elif cols == 3:
            grid_container.classes(add="grid-cols-1 md:grid-cols-2 lg:grid-cols-3")
        else:
            grid_container.classes(add="grid-cols-1 md:grid-cols-2 lg:grid-cols-4")

    def _pane_height_px(pane):
        base = 680 if pane.get("maximized") else (520 if state["cols"] == 1 else 460)
        return int(round(base * state["height_scale"]))

    def set_layout_cols(cols):
        state["cols"] = int(cols)
        apply_grid_classes()
        for pane in state["panes"]:
            if not pane.get("collapsed") and pane["id"] in pane_body_containers:
                pane_body_containers[pane["id"]].style(f"height: {_pane_height_px(pane)}px")
        save_workspace()

    def set_height_scale(scale):
        state["height_scale"] = float(scale)
        for pane in state["panes"]:
            if not pane.get("collapsed") and pane["id"] in pane_body_containers:
                pane_body_containers[pane["id"]].style(f"height: {_pane_height_px(pane)}px")
        save_workspace()

    def add_pane(tool_key):
        bt_now, b_now, c_now, v_now = _area1_bcv()
        state["panes"].append(_make_pane(tool_key, bt=bt_now, b=b_now, c=c_now, v=v_now))
        save_workspace()
        render_grid()

    def remove_pane(pane_id):
        if len(state["panes"]) <= 1:
            ui.notify(get_translation("Keep at least one tool pane."), type="warning")
            return
        state["panes"] = [p for p in state["panes"] if p["id"] != pane_id]
        pane_body_containers.pop(pane_id, None)
        save_workspace()
        render_grid()

    def move_pane(pane_id, delta):
        idx = next((i for i, p in enumerate(state["panes"]) if p["id"] == pane_id), None)
        if idx is None:
            return
        new_idx = idx + delta
        if 0 <= new_idx < len(state["panes"]):
            state["panes"][idx], state["panes"][new_idx] = state["panes"][new_idx], state["panes"][idx]
            save_workspace()
            render_grid()

    def change_pane_tool(pane, new_tool):
        if pane["tool"] == new_tool:
            return
        pane["tool"] = new_tool
        pane["q"] = ""
        pane["sync"] = TOOL_DEFAULTS.get(new_tool, {}).get("sync", False)
        if pane["sync"]:
            bt_now, b_now, c_now, v_now = _area1_bcv()
            pane["bt"], pane["b"], pane["c"], pane["v"] = bt_now, b_now, c_now, v_now
        save_workspace()
        render_grid()

    def toggle_pane_sync(pane):
        pane["sync"] = not pane.get("sync", False)
        if pane["sync"]:
            bt_now, b_now, c_now, v_now = _area1_bcv()
            pane["bt"], pane["b"], pane["c"], pane["v"] = bt_now, b_now, c_now, v_now
        save_workspace()
        render_grid()

    def toggle_pane_collapse(pane):
        pane["collapsed"] = not pane.get("collapsed", False)
        render_grid()

    def toggle_pane_maximize(pane):
        pane["maximized"] = not pane.get("maximized", False)
        if pane["maximized"]:
            pane["collapsed"] = False
        render_grid()

    def apply_preset(preset_data, preset_name=""):
        bt_now, b_now, c_now, v_now = _area1_bcv()
        cols = preset_data.get("cols", 2)
        state["cols"] = cols if cols in (1, 2, 3, 4) else 2
        layout_toggle.value = state["cols"]
        state["panes"] = [
            _make_pane(
                p.get("tool", "commentary"),
                sync=p.get("sync"),
                bt=bt_now,
                b=b_now,
                c=c_now,
                v=v_now,
                q=p.get("q", ""),
            )
            for p in preset_data.get("panes", [])
            if gui is None or p.get("tool") in gui.tools
        ]
        if not state["panes"]:
            state["panes"] = [_make_pane("commentary", True, bt_now, b_now, c_now, v_now)]
        save_workspace()
        render_grid()
        if preset_name:
            ui.notify(f"{get_translation('Loaded preset')}: {preset_name}", type="positive")

    def delete_custom_preset(name):
        custom = dict(app.storage.user.get("multitool_custom_presets") or {})
        if name in custom:
            del custom[name]
            app.storage.user["multitool_custom_presets"] = custom
            rebuild_presets_menu()
            ui.notify(f"{get_translation('Deleted preset')}: {name}", type="info")

    def open_save_preset_dialog():
        with ui.dialog() as dlg, ui.card().classes("w-80"):
            ui.label(get_translation("Save Custom Preset")).classes("text-base font-bold")
            name_input = ui.input(label=get_translation("Preset Name"), placeholder="e.g. My Study").classes("w-full")

            def do_save():
                name = (name_input.value or "").strip()
                if not name:
                    ui.notify(get_translation("Please enter a preset name."), type="warning")
                    return
                custom = dict(app.storage.user.get("multitool_custom_presets") or {})
                custom[name] = {
                    "cols": state["cols"],
                    "panes": [{"tool": p["tool"], "sync": bool(p.get("sync", False))} for p in state["panes"]],
                }
                app.storage.user["multitool_custom_presets"] = custom
                dlg.close()
                ui.notify(f"{get_translation('Saved preset')}: {name}", type="positive")

            name_input.on("keydown.enter", do_save)
            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button(get_translation("Cancel"), on_click=dlg.close).props("flat")
                ui.button(get_translation("Save"), on_click=do_save).props("color=primary")
        dlg.open()

    def render_grid():
        apply_grid_classes()
        grid_container.clear()
        pane_body_containers.clear()
        owned_listeners.clear()

        with grid_container:
            for idx, pane in enumerate(state["panes"]):
                card_classes = "w-full flex flex-col p-0 overflow-hidden border"
                if pane.get("maximized"):
                    card_classes += " col-span-full"
                with ui.card().classes(card_classes):
                    # Pane Header
                    with ui.row().classes("w-full items-center justify-between gap-1 px-2 py-1 border-b bg-black/5 dark:bg-white/5"):
                        ui.select(
                            tool_options,
                            value=pane["tool"],
                            on_change=lambda e, p=pane: change_pane_tool(p, e.value),
                        ).props("dense borderless options-dense").classes("min-w-[140px] flex-grow text-sm font-medium")

                        with ui.row().classes("items-center gap-0"):
                            sync_color = "primary" if pane.get("sync") else "grey"
                            ui.button(
                                icon="sync",
                                on_click=lambda p=pane: toggle_pane_sync(p),
                            ).props(f"flat dense round size=xs color={sync_color}").tooltip(
                                get_translation("Sync with Bible (On)" if pane.get("sync") else "Sync with Bible (Off)")
                            )
                            ui.button(
                                icon="refresh",
                                on_click=lambda p=pane: (
                                    p.update(zip(("bt", "b", "c", "v"), _area1_bcv())),
                                    save_workspace(),
                                    render_pane_body(p),
                                ),
                            ).props("flat dense round size=xs").tooltip(get_translation("Refresh from Bible"))
                            if idx > 0:
                                ui.button(
                                    icon="arrow_back" if state["cols"] > 1 else "arrow_upward",
                                    on_click=lambda pid=pane["id"]: move_pane(pid, -1),
                                ).props("flat dense round size=xs").tooltip(get_translation("Move Earlier"))
                            if idx < len(state["panes"]) - 1:
                                ui.button(
                                    icon="arrow_forward" if state["cols"] > 1 else "arrow_downward",
                                    on_click=lambda pid=pane["id"]: move_pane(pid, 1),
                                ).props("flat dense round size=xs").tooltip(get_translation("Move Later"))
                            ui.button(
                                icon="fullscreen_exit" if pane.get("maximized") else "fullscreen",
                                on_click=lambda p=pane: toggle_pane_maximize(p),
                            ).props("flat dense round size=xs").tooltip(
                                get_translation("Restore" if pane.get("maximized") else "Maximize")
                            )
                            ui.button(
                                icon="expand_more" if pane.get("collapsed") else "expand_less",
                                on_click=lambda p=pane: toggle_pane_collapse(p),
                            ).props("flat dense round size=xs").tooltip(
                                get_translation("Expand" if pane.get("collapsed") else "Collapse")
                            )
                            ui.button(
                                icon="close",
                                on_click=lambda pid=pane["id"]: remove_pane(pid),
                            ).props("flat dense round size=xs color=negative").tooltip(get_translation("Close Pane"))

                    # Pane Body
                    if not pane.get("collapsed"):
                        height_px = _pane_height_px(pane)
                        body = ui.scroll_area().classes("w-full").style(f"height: {height_px}px")
                        pane_body_containers[pane["id"]] = body
                        render_pane_body(pane)

    render_grid()

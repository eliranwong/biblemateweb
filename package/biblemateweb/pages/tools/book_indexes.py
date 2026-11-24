import apsw
import re, os
from functools import partial
from nicegui import ui, app, run
from biblemateweb import BIBLEMATEWEB_DATA, config as app_config, get_translation, download_txt
from biblemateweb.fx.bible import BibleSelector
from biblemateweb.pages.tools.indexes import render_exlb_chips
from biblemateweb.pages.tools.chapter_indexes import (
    ORIGINAL_LANGUAGE_BIBLES,
    fetch_chapter_vocabulary,
    fetch_chapter_translation_vocabulary,
    render_grouped_module_chips,
    render_locations_map_expansion,
)
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks


def book_indexes(gui=None, bt=None, b=1, c=1, v=1, area=2, **_):

    def exlbl(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Locations')
    ui.on('exlbl', exlbl)

    def exlbp(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Characters')
    ui.on('exlbp', exlbp)

    def exlbt(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Topics')
    ui.on('exlbt', exlbt)

    DB_FILE = os.path.join(BIBLEMATEWEB_DATA, 'indexes2.sqlite')

    def localized_exlb_table(name):
        lang = app.storage.user.get("ui_language", "eng")
        if lang in ("tc", "sc"):
            return f"{name}_{lang}"
        return name

    TABLE_CONFIG = {
        "Bible People": {"table": localized_exlb_table("exlbp"), "icon": "groups"},
        "Bible Locations": {"table": localized_exlb_table("exlbl"), "icon": "place"},
        "Bible Topics": {"table": localized_exlb_table("exlbt"), "icon": "category"},
    }

    def fetch_book_data(table_name: str, book_id: int):
        try:
            with apsw.Connection(DB_FILE) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"SELECT Information FROM {table_name} WHERE Book=? ORDER BY Chapter, Verse",
                    (book_id,),
                )
                rows = cursor.fetchall()
                return "\n\n".join([row[0].replace("</td><td>", "&nbsp;&nbsp;</td><td>") for row in rows]) if rows else None
        except Exception as e:
            return f"Error querying database: {str(e)}"

    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):

        bible_selector = BibleSelector(version_options=["KJV"])

        def additional_items():
            nonlocal gui, bible_selector, area

            def change_indexes(selection):
                if area == 1:
                    app.storage.user['tool_book_text'], app.storage.user['bible_book_number'], *_ = selection
                    gui.load_area_1_content(title="Bookindexes")
                else:
                    app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], *_ = selection
                    gui.load_area_2_content(title="Bookindexes", sync=False)

            ui.button(get_translation('Go'), on_click=lambda: change_indexes(bible_selector.get_selection()))

        bible_selector.create_ui("KJV", b, c, v, additional_items=additional_items, show_versions=False, show_chapters=False, show_verses=False)

        results_container = ui.column().classes('w-full gap-4')

    def search_action(book_id):
        results_container.clear()

        with results_container:
            results = {}
            for title, tbl_cfg in TABLE_CONFIG.items():
                results[title] = fetch_book_data(tbl_cfg['table'], book_id)

            found_any = False

            def open_lexicon(module, entry):
                nonlocal gui
                app.storage.user['favorite_lexicon'] = module
                app.storage.user['tool_query'] = entry
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='lexicons')

            def search_bible_word(bible_version, word):
                nonlocal gui
                app.storage.user['tool_book_text'] = bible_version
                book_abbrev = BibleBooks.abbrev["eng"].get(str(book_id), ["Gen"])[0]
                if word.isascii() and app.storage.user.get('search_mode') == 2:
                    query_term = rf"\b{re.escape(word)}\b"
                else:
                    query_term = word
                app.storage.user['tool_query'] = f"{book_abbrev}:::{query_term}"
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Verses')

            # --- BOOK TRANSLATION VOCABULARY (hidden for original-language Bibles) ---
            active_bible = gui.get_area_1_bible_text() if gui else app.storage.user.get('primary_bible', 'NET')
            ui_lang = app.storage.user.get('ui_language', 'eng')
            is_original_bible = active_bible in ORIGINAL_LANGUAGE_BIBLES
            if not is_original_bible:
                trans_vocab_loaded = {'done': False}

                async def load_trans_vocab(e):
                    if not e.value or trans_vocab_loaded['done']:
                        return
                    trans_vocab_loaded['done'] = True
                    trans_vocab_container.clear()
                    with trans_vocab_container:
                        ui.spinner(size='sm')
                    version_col, matched, filtered_top, unfiltered_top, rare_items = await run.io_bound(
                        fetch_chapter_translation_vocabulary,
                        book_id,
                        None,
                        active_bible,
                        ui_lang,
                        app.storage.client["custom"],
                    )
                    trans_vocab_container.clear()
                    with trans_vocab_container:
                        if not version_col or (not unfiltered_top and not rare_items):
                            ui.label(get_translation('No data found.')).classes('p-2 italic')
                            return

                        if not matched:
                            ui.label(
                                f"{get_translation('Showing')} {version_col} ({active_bible} {get_translation('is not in tagged translations')})"
                            ).classes('text-xs text-gray-500 italic')

                        def _chip_tooltip(item):
                            vv = ", ".join(str(v_num) for v_num in item["verses"][:10])
                            if len(item["verses"]) > 10:
                                vv += ", ..."
                            lemmas_str = "; ".join(item["lemmas"][:3])
                            return f"{vv}" + (f" · {lemmas_str}" if lemmas_str else "")

                        hide_common = {'value': True}
                        chips_area = ui.column().classes('w-full gap-2')

                        def render_trans_chips():
                            chips_area.clear()
                            top_list = filtered_top if (hide_common['value'] and filtered_top) else unfiltered_top
                            with chips_area:
                                if top_list:
                                    ui.label(get_translation('Key Words in Book')).classes('font-bold text-sm mt-1')
                                    with ui.row().classes('w-full gap-2 flex-wrap'):
                                        for item in top_list:
                                            chip = ui.chip(
                                                f"{item['word']} ({item['count']})",
                                                icon='search',
                                                on_click=partial(search_bible_word, version_col, item['word']),
                                            ).props('outline').classes('cursor-pointer')
                                            chip.tooltip(_chip_tooltip(item))
                                if rare_items:
                                    ui.label(get_translation('Rare-Lemma Words in Book (<= 3x in Bible)')).classes('font-bold text-sm mt-3')
                                    with ui.row().classes('w-full gap-2 flex-wrap'):
                                        for item in rare_items[:30]:
                                            rc = item['rare_count']
                                            badge = "1x (hapax)" if rc == 1 else f"{rc}x"
                                            chip = ui.chip(
                                                f"{item['word']} [{badge}]",
                                                icon='search',
                                                color='deep-orange' if rc == 1 else 'amber-8',
                                                on_click=partial(search_bible_word, version_col, item['word']),
                                            ).props('text-color=white').classes('cursor-pointer')
                                            chip.tooltip(_chip_tooltip(item))

                        def on_toggle_common(ev):
                            hide_common['value'] = bool(ev.value)
                            render_trans_chips()

                        ui.switch(get_translation('Hide common words'), value=True, on_change=on_toggle_common).classes('text-sm')
                        render_trans_chips()

                with ui.expansion(get_translation('Book Translation Vocabulary'), icon='translate', value=True, on_value_change=load_trans_vocab) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    trans_vocab_container = ui.column().classes('w-full p-2 gap-2')
                ui.timer(0.05, lambda: load_trans_vocab(type('E', (), {'value': True})()), once=True)

            # --- BOOK VOCABULARY & RARE WORDS ---
            vocab_loaded = {'done': False}

            async def load_vocab(e):
                if not e.value or vocab_loaded['done']:
                    return
                vocab_loaded['done'] = True
                vocab_container.clear()
                with vocab_container:
                    ui.spinner(size='sm')
                top_words, rare_words = await run.io_bound(fetch_chapter_vocabulary, book_id, None, app.storage.client["custom"])
                vocab_container.clear()
                with vocab_container:
                    if not top_words:
                        ui.label(get_translation('No data found.')).classes('p-2 italic')
                        return
                    ui.label(get_translation('Top Book Lemmas')).classes('font-bold text-sm mt-1')
                    with ui.row().classes('w-full gap-2 flex-wrap'):
                        for entry, lexeme, gloss, cnt in top_words:
                            first_entry = entry.split(",")[0]
                            lex_entry = entry.split(",")[-2] if entry.endswith(",") and len(entry.split(",")) > 1 else first_entry
                            ui.chip(
                                f"{lexeme} ({cnt}) — {gloss}",
                                icon='search',
                                on_click=partial(open_lexicon, app.storage.user['hebrew_lexicon'] if book_id < 40 else app.storage.user['greek_lexicon'], lex_entry),
                            ).props('outline').classes('cursor-pointer')
                    if rare_words:
                        ui.label(get_translation('Rare Words in Book (<= 3x in Bible)')).classes('font-bold text-sm mt-3')
                        with ui.row().classes('w-full gap-2 flex-wrap'):
                            for entry, lexeme, gloss, bk_cnt, total_cnt in rare_words[:30]:
                                lex_entry = entry.split(",")[-2] if entry.endswith(",") and len(entry.split(",")) > 1 else entry.split(",")[0]
                                badge_label = "1x (hapax)" if total_cnt == 1 else f"{total_cnt}x"
                                ui.chip(
                                    f"{lexeme} [{badge_label}] — {gloss}",
                                    color='deep-orange' if total_cnt == 1 else 'amber-8',
                                    on_click=partial(open_lexicon, app.storage.user['hebrew_lexicon'] if book_id < 40 else app.storage.user['greek_lexicon'], lex_entry),
                                ).props('text-color=white').classes('cursor-pointer')

            with ui.expansion(get_translation('Book Vocabulary & Rare Words'), icon='analytics', value=is_original_bible, on_value_change=load_vocab) \
                    .classes('w-full border rounded-lg shadow-sm') \
                    .props('header-class="font-bold text-lg text-secondary"'):
                vocab_container = ui.column().classes('w-full p-2 gap-2')
            if is_original_bible:
                ui.timer(0.05, lambda: load_vocab(type('E', (), {'value': True})()), once=True)

            # --- PEOPLE RELATIONSHIP GRAPH (book-wide, lazy-loaded on expand) ---
            people_html = results.get("Bible People") or ""
            if re.search(r"BP\d+", people_html):
                people_loaded = {'done': False}

                async def load_people_graph(e):
                    if not e.value or people_loaded['done']:
                        return
                    people_loaded['done'] = True
                    people_graph_container.clear()
                    lang = app.storage.user.get("ui_language", "eng")
                    p_tbl = f"PEOPLE_{lang.upper()}" if lang in ("tc", "sc") else "PEOPLE"
                    r_tbl = f"PEOPLERELATIONSHIP_{lang.upper()}" if lang in ("tc", "sc") else "PEOPLERELATIONSHIP"
                    db_people = os.path.join(BIBLEMATEWEB_DATA, "data", "biblePeople.data")
                    nodes, links = [], []
                    try:
                        with apsw.Connection(db_people) as connn:
                            cur = connn.cursor()
                            cur.execute(f"SELECT DISTINCT PersonID, Name, Sex FROM {p_tbl} WHERE Book=?", (book_id,))
                            book_people = cur.fetchall()
                            if book_people:
                                id_set = {r[0] for r in book_people}
                                for pid, pname, psex in book_people:
                                    clean_name = re.sub(r'\s*\[.*?\]', '', str(pname)).strip() or str(pname)
                                    nodes.append({
                                        'id': str(pid),
                                        'name': clean_name,
                                        'value': pid,
                                        'symbolSize': 24,
                                        'itemStyle': {'color': '#3b82f6' if psex == 'M' else '#ec4899'},
                                    })
                                placeholders = ",".join("?" for _ in id_set)
                                cur.execute(
                                    f"SELECT PersonID, RelatedPersonID, Relationship FROM {r_tbl} WHERE PersonID IN ({placeholders}) AND RelatedPersonID IN ({placeholders})",
                                    list(id_set) + list(id_set),
                                )
                                seen_edges = set()
                                for pid1, pid2, rel in cur.fetchall():
                                    edge_key = (min(pid1, pid2), max(pid1, pid2), rel)
                                    if edge_key not in seen_edges:
                                        seen_edges.add(edge_key)
                                        links.append({'source': str(pid1), 'target': str(pid2), 'value': rel, 'label': {'show': True, 'formatter': rel}})
                    except Exception:
                        pass

                    with people_graph_container:
                        if not nodes:
                            ui.label(get_translation('No people found in this book.')).classes('italic p-2')
                            return
                        dark = app.storage.user.get('dark_mode', False)
                        text_color = '#e5e7eb' if dark else '#1f2937'

                        def on_book_node_click(ev):
                            args = ev.args if isinstance(ev.args, dict) else {}
                            if args.get('dataType') == 'edge':
                                return
                            idx = args.get('dataIndex')
                            if idx is None or idx < 0 or idx >= len(nodes):
                                return
                            app.storage.user['tool_query'] = f"BP{nodes[idx]['id']}"
                            gui.select_next_area2_tab()
                            gui.load_area_2_content(title='Characters', sync=False)

                        bk_graph = ui.echart({
                            'tooltip': {'trigger': 'item'},
                            'series': [{
                                'type': 'graph',
                                'layout': 'force',
                                'roam': True,
                                'draggable': True,
                                'label': {'show': True, 'position': 'right', 'color': text_color},
                                'edgeSymbol': ['none', 'arrow'],
                                'edgeSymbolSize': [4, 8],
                                'edgeLabel': {'fontSize': 10, 'color': text_color},
                                'force': {'repulsion': 180, 'edgeLength': 90},
                                'data': nodes,
                                'links': links,
                            }],
                        }).classes('w-full h-96 cursor-pointer')
                        bk_graph.on('chart:click', on_book_node_click, ['dataType', 'dataIndex'])

                with ui.expansion(get_translation('People Relationship Graph'), icon='hub', value=False, on_value_change=load_people_graph) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    people_graph_container = ui.column().classes('w-full p-2')

            # --- BOOK MAP (lazy-loaded on expand) ---
            render_locations_map_expansion(results.get("Bible Locations") or "", "Book Map")

            def open_exlb(target_title, entry_id):
                nonlocal gui
                app.storage.user['tool_query'] = entry_id
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title=target_title)

            for title, tbl_cfg in TABLE_CONFIG.items():
                content = results.get(title)
                with ui.expansion(get_translation(title), icon=tbl_cfg['icon'], value=False) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    if content:
                        if title in ("Bible People", "Bible Locations"):
                            target_title = "Characters" if title == "Bible People" else "Locations"
                            chip_icon = "person" if title == "Bible People" else "place"
                            if render_exlb_chips(content, chip_icon, partial(open_exlb, target_title)):
                                found_any = True
                            else:
                                ui.label(get_translation('No entries found for this category.')).classes('p-4 italic')
                        elif title == "Bible Topics":
                            if render_grouped_module_chips(content, "topics", "topic", partial(open_exlb, "Topics")):
                                found_any = True
                            else:
                                ui.label(get_translation('No entries found for this category.')).classes('p-4 italic')
                    else:
                        ui.label(get_translation('No entries found for this category.')).classes('p-4 italic')

            if not found_any:
                ui.notify(get_translation('No data found in any index for this book.'), type='info')

            # --- EXPORT UNIFIED BOOK STUDY SHEET ---
            async def export_book_study_sheet():
                lang = app.storage.user.get("ui_language", "eng")
                abbrev_map = BibleBooks.abbrev.get(lang, BibleBooks.abbrev['eng'])
                book_name = abbrev_map[str(book_id)][-1] if str(book_id) in abbrev_map else str(book_id)
                lines = [f"# {book_name} — {get_translation('Study Sheet')}", ""]
                try:
                    top_lemmas, rare_lemmas = await run.io_bound(fetch_chapter_vocabulary, book_id, None, app.storage.client["custom"])
                    if top_lemmas:
                        lines.append(f"## {get_translation('Top Book Lemmas')}")
                        for _, lexeme, gloss, cnt in top_lemmas:
                            lines.append(f"- {lexeme} ({cnt}x): {gloss}")
                        lines.append("")
                    if rare_lemmas:
                        lines.append(f"## {get_translation('Rare Words in Book (<= 3x in Bible)')}")
                        for _, lexeme, gloss, bk_cnt, total_cnt in rare_lemmas[:30]:
                            badge = "1x (hapax)" if total_cnt == 1 else f"{total_cnt}x"
                            lines.append(f"- {lexeme} [{badge}]: {gloss}")
                        lines.append("")
                    v_col, _, trans_top, _, _ = await run.io_bound(
                        fetch_chapter_translation_vocabulary,
                        book_id,
                        None,
                        active_bible,
                        lang,
                        app.storage.client["custom"],
                    )
                    if v_col and trans_top:
                        lines.append(f"## {get_translation('Key Words in Book')} ({v_col})")
                        for item in trans_top:
                            lines.append(f"- {item['word']} ({item['count']}x)")
                        lines.append("")
                except Exception:
                    pass
                await download_txt("\n".join(lines))

            with ui.row().classes('w-full justify-end mt-2'):
                ui.button(get_translation('Export Study Sheet'), icon='download', on_click=export_book_study_sheet).props('outline color=primary')

            # --- BOOK TOOLS QUICK LAUNCH ---
            def open_book_tool(title, setup_fn=None):
                nonlocal gui
                app.storage.user["tool_book_number"] = book_id
                app.storage.user["tool_chapter_number"] = c
                app.storage.user["tool_verse_number"] = v
                if setup_fn:
                    setup_fn()
                gui.select_next_area2_tab()
                gui.load_area_2_content(title=title, sync=False)

            def _setup_analysis(section=None):
                if section:
                    app.storage.user["tool_query"] = section

            def _setup_book_note():
                app.storage.user["tool_chapter_number"] = 0
                app.storage.user["tool_verse_number"] = 0

            with ui.column().classes('w-full gap-2 mt-2 pt-3 border-t border-gray-200'):
                ui.label(get_translation('Book Tools')).classes('font-bold text-sm text-secondary')
                with ui.row().classes('w-full gap-2 flex-wrap'):
                    ui.button(get_translation('Timelines'), icon='timeline', on_click=partial(open_book_tool, 'Timelines')).props('outline size=sm')
                    ui.button(get_translation('Book Analysis'), icon='auto_awesome', on_click=partial(open_book_tool, 'Analysis')).props('outline size=sm')
                    for sec in ("Overview", "Structural Outline", "Themes", "Theology", "Summary"):
                        ui.button(get_translation(sec), icon='insights', on_click=partial(open_book_tool, 'Analysis', partial(_setup_analysis, sec))).props('outline size=sm')
                    ui.button(get_translation('Chapter Indexes'), icon='library_books', on_click=partial(open_book_tool, 'Chapterindexes')).props('outline size=sm')
                    if app_config.google_client_id and app_config.google_client_secret:
                        ui.button(get_translation('Notes'), icon='edit_note', on_click=partial(open_book_tool, 'Notes', _setup_book_note)).props('outline size=sm')

    search_action(b)

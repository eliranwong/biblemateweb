import apsw
import re, os, asyncio, html as html_lib
from nicegui import ui, app, run
from biblemateweb import BIBLEMATEWEB_DATA, get_translation, download_txt, get_morphology_db
from functools import partial
from biblemateweb.fx.bible import BibleSelector
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks


def chapter_indexes(gui=None, bt=None, b=1, c=1, v=1, area=2, **_):

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
    def bibleDict(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Dictionaries')
    ui.on('bibleDict', bibleDict)
    def encyclopedia(event):
        nonlocal gui
        app.storage.user['favorite_encyclopedia'], app.storage.user['tool_query'] = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Encyclopedias')
    ui.on('encyclopedia', encyclopedia)

    # --- CONFIGURATION ---
    DB_FILE = os.path.join(BIBLEMATEWEB_DATA, 'indexes2.sqlite')

    def localized_exlb_table(name):
        lang = app.storage.user.get("ui_language", "eng")
        if lang in ("tc", "sc"):
            return f"{name}_{lang}"
        return name

    # Define your tables, their display titles, and their icons
    TABLE_CONFIG = {
        "Bible People": {
            "table": localized_exlb_table("exlbp"),
            "icon": "groups"        # Icon for people/groups
        },
        "Bible Locations": {
            "table": localized_exlb_table("exlbl"),
            "icon": "place"         # Icon for maps/locations
        },
        "Bible Topics": {
            "table": "exlbt", 
            "icon": "category"      # Icon for topics/categories
        },
        "Bible Dictionaries": {
            "table": "dictionaries", 
            "icon": "loyalty"     # Icon for definitions/books
        },
        "Bible Encyclopedia": {
            "table": "encyclopedia", 
            "icon": "diamond" # Icon for deep knowledge/library
        }
    }

    def fetch_data(table_name: str, book_id: int, chapter: int):
        """
        Connects to SQLite and retrieves information for the specific verse.
        """
        try:
            with apsw.Connection(DB_FILE) as connection:
                cursor = connection.cursor()
                query = f"SELECT Information FROM {table_name} WHERE Book=? AND Chapter=? ORDER BY Verse"
                cursor.execute(query, (book_id, chapter))
                rows = cursor.fetchall()
                return "\n\n".join([row[0].replace("</td><td>", "&nbsp;&nbsp;</td><td>") for row in rows]) if rows else None
        except Exception as e:
            return f"Error querying database: {str(e)}"

    # --- UI LAYOUT ---
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):

        # Bible Selection menu
        bible_selector = BibleSelector(version_options=["KJV"])
        def additional_items():
            nonlocal gui, bible_selector, area
            def change_indexes(selection):
                if area == 1:
                    app.storage.user['tool_book_text'], app.storage.user['bible_book_number'], app.storage.user['bible_chapter_number'], app.storage.user['bible_verse_number'] = selection
                    gui.load_area_1_content(title="Chapterindexes")
                else:
                    app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
                    gui.load_area_2_content(title="Chapterindexes", sync=False)
            ui.button(get_translation('Go'), on_click=lambda: change_indexes(bible_selector.get_selection()))
        bible_selector.create_ui("KJV", b, c, v, additional_items=additional_items, show_versions=False, show_verses=False)

        # Results Container
        results_container = ui.column().classes('w-full gap-4')

    def search_action(book_id, chapter):
        # Clear UI and show loading spinner
        results_container.clear()
        
        with results_container:
            
            # Run IO-bound DB operations
            results = {}
            for title, config in TABLE_CONFIG.items():
                data = fetch_data(config['table'], book_id, chapter)
                results[title] = data
            
            #parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
            #ui.label(f"Resources for {parser.bcvToVerseReference(book_id, chapter, verse)}") \
            #    .classes('text-xl font-semibold text-secondary mb-2')

            # --- RENDER EXPANSIONS ---
            found_any = False

            # --- CHAPTER PEOPLE RELATIONSHIP GRAPH (lazy-loaded on expand, before Bible People) ---
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
                            cur.execute(f"SELECT DISTINCT PersonID, Name, Sex FROM {p_tbl} WHERE Book=? AND Chapter=?", (book_id, chapter))
                            chapter_people = cur.fetchall()
                            if chapter_people:
                                id_set = {r[0] for r in chapter_people}
                                for pid, pname, psex in chapter_people:
                                    clean_name = re.sub(r'\s*\[.*?\]', '', str(pname)).strip() or str(pname)
                                    nodes.append({
                                        'id': str(pid),
                                        'name': clean_name,
                                        'value': pid,
                                        'symbolSize': 28,
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
                            ui.label(get_translation('No people found in this chapter.')).classes('italic p-2')
                            return
                        dark = app.storage.user.get('dark_mode', False)
                        text_color = '#e5e7eb' if dark else '#1f2937'

                        def on_chapter_node_click(ev):
                            args = ev.args if isinstance(ev.args, dict) else {}
                            if args.get('dataType') == 'edge':
                                return
                            idx = args.get('dataIndex')
                            if idx is None or idx < 0 or idx >= len(nodes):
                                return
                            app.storage.user['tool_query'] = f"BP{nodes[idx]['id']}"
                            gui.select_next_area2_tab()
                            gui.load_area_2_content(title='Characters', sync=False)

                        ch_graph = ui.echart({
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
                        ch_graph.on('chart:click', on_chapter_node_click, ['dataType', 'dataIndex'])

                with ui.expansion(get_translation('People Relationship Graph'), icon='hub', value=False, on_value_change=load_people_graph) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    people_graph_container = ui.column().classes('w-full p-2')

            # --- CHAPTER MAP (lazy-loaded on expand, before Bible People) ---
            loc_html = results.get("Bible Locations") or ""
            loc_ids = list(dict.fromkeys(re.findall(r"BL\d+", loc_html)))
            if loc_ids:
                map_loaded = {'done': False}
                async def load_chapter_map(e):
                    if not e.value or map_loaded['done']:
                        return
                    map_loaded['done'] = True
                    map_container.clear()
                    lang = app.storage.user.get("ui_language", "eng")
                    exlbli_tbl = f"exlbli_{lang}" if lang in ("tc", "sc") else "exlbli"
                    db_exlb = os.path.join(BIBLEMATEWEB_DATA, "data", "exlb3.data")
                    markers_data = []
                    try:
                        with apsw.Connection(db_exlb) as connn:
                            cur = connn.cursor()
                            placeholders = ",".join("?" for _ in loc_ids)
                            cur.execute(f"SELECT path, location, lat, lng FROM {exlbli_tbl} WHERE path IN ({placeholders})", loc_ids)
                            for p, loc_name, lat_s, lng_s in cur.fetchall():
                                try:
                                    lat_f, lng_f = float(lat_s), float(lng_s)
                                    if lat_f and lng_f:
                                        markers_data.append((p, loc_name, lat_f, lng_f))
                                except (TypeError, ValueError):
                                    pass
                    except Exception:
                        pass

                    with map_container:
                        if not markers_data:
                            ui.label(get_translation('No coordinates found for locations in this chapter.')).classes('italic p-2')
                            return
                        avg_lat = sum(m[2] for m in markers_data) / len(markers_data)
                        avg_lng = sum(m[3] for m in markers_data) / len(markers_data)
                        m = ui.leaflet(center=(avg_lat, avg_lng), zoom=7).classes('w-full h-96')
                        def open_location_next_tab(path):
                            app.storage.user['tool_query'] = path
                            gui.select_next_area2_tab()
                            gui.load_area_2_content(title='Locations', sync=False)

                        created_markers = []
                        for p, loc_name, lat_f, lng_f in markers_data:
                            mk = m.marker(latlng=(lat_f, lng_f))
                            mk.on('click', lambda _, path=p: open_location_next_tab(path))
                            created_markers.append((mk, loc_name))
                        async def bind_all():
                            await asyncio.sleep(0.2)
                            for mk, loc_name in created_markers:
                                if mk.id is not None:
                                    mk.run_method('bindTooltip', html_lib.escape(str(loc_name)))
                        ui.timer(0.1, bind_all, once=True)

                with ui.expansion(f"{get_translation('Chapter Map')} ({len(loc_ids)})", icon='map', value=False, on_value_change=load_chapter_map) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    map_container = ui.column().classes('w-full p-2')
            
            for title, config in TABLE_CONFIG.items():
                content = results.get(title)
                
                # Check if this should be open by default
                is_open = (title == "Bible Topics")
                
                # Create the Expansion with specific icon
                with ui.expansion(get_translation(title), icon=config['icon'], value=is_open) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    
                    if content:
                        # convert links, e.g. <ref onclick="bcv(3,19,26)">
                        content = content.replace("<table><tr>", "<tr>")
                        content = content.replace("<tr>", "<table><tr>")
                        content = content.replace("</tr></table>", "</tr>")
                        content = content.replace("</tr>", "</tr></table>")
                        content = re.sub(r'''<ref onclick="(searchEncyc|searchDict)\('.*?'\)">(.*?)</ref>''', r"\2", content)
                        content = re.sub(r'''(onclick|ondblclick)="(cr|bcv|website|exlbl|exlbp|exlbt|bibleDict|encyclopedia)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
                        content = re.sub(r"""(onclick|ondblclick)='(cr|bcv|website|exlbl|exlbp|exlbt|bibleDict|encyclopedia)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
                        ui.html(f'<div class="content-text">{content}</div>', sanitize=False).classes('p-4')
                        found_any = True
                    else:
                        ui.label(get_translation('No entries found for this category.')) \
                            .classes('p-4 italic')

            def open_collection(collection, tool, number):
                nonlocal gui
                app.storage.user['tool_query'] = f"{tool}.{number}"
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title=collection)

            for i in ("PROMISES_INDEXES", "PARALLEL_INDEXES"):

                # Create the Expansion with specific icon
                with ui.expansion(get_translation("Bible Promises" if i == "PROMISES_INDEXES" else "Bible Parallels"), icon="redeem" if i == "PROMISES_INDEXES" else "link", value=is_open) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):

                    DB_FILE2 = os.path.join(BIBLEMATEWEB_DATA, "collections3.sqlite")
                    sql_query = "SELECT Tool, Number, Topic FROM " + i + " WHERE Passages LIKE ?"
                    with apsw.Connection(DB_FILE2) as connn:
                        cursor = connn.cursor()
                        cursor.execute(sql_query, (f"%({book_id}, {chapter},%",))
                        fetches = cursor.fetchall()
                    
                    if fetches:
                        for tool, number, topic in fetches:
                            ui.chip(
                                topic,
                                icon='book',
                                color='primary',
                                on_click=partial(open_collection, "Promises" if i == "PROMISES_INDEXES" else "Parallels", tool, number),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                    else:
                        ui.label(get_translation('No entries found for this category.')) \
                            .classes('p-4 italic')

            if not found_any:
                ui.notify('No data found in any index for this verse.', type='info')

            # --- EXPORT UNIFIED CHAPTER STUDY SHEET ---
            async def export_study_sheet():
                lang = app.storage.user.get("ui_language", "eng")
                abbrev_map = BibleBooks.abbrev.get(lang, BibleBooks.abbrev['eng'])
                book_name = abbrev_map[str(book_id)][-1] if str(book_id) in abbrev_map else str(book_id)
                lines = [f"# {book_name} {chapter} — {get_translation('Study Sheet')}", ""]
                for title in TABLE_CONFIG:
                    raw = results.get(title) or ""
                    clean = re.sub(r"<[^>]+?>", " ", raw)
                    clean = re.sub(r"[ \t]+", " ", clean).strip()
                    if clean:
                        lines.append(f"## {get_translation(title)}")
                        lines.append(clean)
                        lines.append("")
                try:
                    morph_db = get_morphology_db(app.storage.client["custom"])
                    with apsw.Connection(morph_db) as connn:
                        cur = connn.cursor()
                        cur.execute(
                            "SELECT Lexeme, Gloss, COUNT(*) as cnt FROM morphology WHERE Book=? AND Chapter=? AND LexicalEntry != '' GROUP BY LexicalEntry ORDER BY cnt DESC LIMIT 15",
                            (book_id, chapter),
                        )
                        top_lemmas = cur.fetchall()
                    if top_lemmas:
                        lines.append(f"## {get_translation('Top Chapter Lemmas')}")
                        for lexeme, gloss, cnt in top_lemmas:
                            lines.append(f"- {lexeme} ({cnt}x): {gloss}")
                        lines.append("")
                except Exception:
                    pass
                await download_txt("\n".join(lines))

            with ui.row().classes('w-full justify-end mt-2'):
                ui.button(get_translation('Export Study Sheet'), icon='download', on_click=export_study_sheet).props('outline color=primary')
        
    search_action(b,c)

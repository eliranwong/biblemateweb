import apsw
import re, os, asyncio, html as html_lib
from nicegui import ui, app, run
from biblemateweb import BIBLEMATEWEB_DATA, config as app_config, get_translation, download_txt, get_morphology_db, get_tagged_translations_db
from functools import partial
from biblemateweb.fx.bible import BibleSelector
from biblemateweb.pages.tools.indexes import render_exlb_chips
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser


_NON_TRANSLATION_COLS = {
    "WordID", "ClauseID", "Book", "Chapter", "Verse", "Word", "LexicalEntry",
    "MorphologyCode", "Morphology", "Lexeme", "Transliteration", "Pronunciation",
    "Interlinear", "Translation", "Gloss", "BDBE", "BDBEContextSpecific",
    "CHALOT", "CHALOTContextSpecific", "HALOT", "HALOTContextSpecific",
    "BDAG", "BDAGContextSpecific", "LSJ", "LSJContextSpecific",
    "eStrong", "eStrongContextSpecific",
}

_COMMON_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "from", "by", "with", "as", "is", "are", "was", "were", "be", "been", "being",
    "he", "she", "it", "they", "them", "his", "her", "its", "their", "this", "that",
    "these", "those", "who", "whom", "which", "not", "no", "so", "if", "then",
    "when", "all", "into", "unto", "upon", "out", "up", "over", "have", "has", "had",
    "do", "does", "did", "will", "shall", "would", "should", "may", "might", "can",
    "could", "i", "you", "we", "us", "my", "your", "our", "me", "him", "there",
    "的", "了", "和", "與", "在", "是", "有", "也", "都", "就", "而", "及", "以",
    "於", "于", "為", "为", "之", "其", "這", "这", "那", "他", "她", "它",
    "們", "们", "我", "你", "不", "沒", "没", "把", "被", "從", "从", "向",
    "對", "对", "給", "给", "到", "著", "着",
}

_PUNCT_STRIP = ".,;:!?'\"()[]{}「」『』《》〈〉、。，；：！？（）【】“”‘’—–- \t\n\r"


def extract_grouped_module_entries(content: str, category: str) -> dict:
    """Parse table rows and return {module: [(key, label), ...]} deduplicated per module."""
    grouped = {}
    seen_per_mod = {}
    pattern_map = {
        "topics": r'''<ref onclick="exlbt\('([^']+)'\)">(.*?)</ref>''',
        "dictionaries": r'''<ref onclick="bibleDict\('([^']+)'\)">(.*?)</ref>''',
        "encyclopedia": r'''<ref onclick="encyclopedia\('([^']+)','([^']+)'\)">(.*?)</ref>''',
    }
    entry_re = pattern_map.get(category)
    if not entry_re:
        return grouped

    for td1, td2 in re.findall(r'<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>', content, flags=re.DOTALL):
        mod_match = re.search(r'''<ref onclick="(?:searchDict|searchEncyc)\('([^']+)'\)">''', td1)
        if mod_match:
            mod = mod_match.group(1).strip()
        else:
            mod = re.sub(r'<[^<>]+?>', '', td1).strip('[] \t\n\r')
        if not mod:
            continue
        mod_entries = grouped.setdefault(mod, [])
        seen = seen_per_mod.setdefault(mod, set())
        for match in re.findall(entry_re, td2, flags=re.DOTALL):
            if category == "encyclopedia":
                enc_mod, entry_id, raw_label = match
                key = (enc_mod, entry_id)
            else:
                entry_id, raw_label = match
                key = entry_id
            if key in seen:
                continue
            seen.add(key)
            clean_label = html_lib.unescape(re.sub(r'<[^<>]+?>', '', raw_label)).strip()
            clean_label = re.sub(r'^\(-?\d+\)\s*', '', clean_label)
            if clean_label:
                mod_entries.append((key, clean_label))
    return {k: v for k, v in sorted(grouped.items()) if v}


def render_locations_map_expansion(loc_html: str, title_key: str = "Chapter Map"):
    """Render a lazy-loaded Leaflet map expansion for BL location IDs found in loc_html."""
    loc_ids = list(dict.fromkeys(re.findall(r"BL\d+", loc_html or "")))
    if not loc_ids:
        return
    map_loaded = {'done': False}

    async def load_locations_map(e):
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

            created_markers = []
            for p, loc_name, lat_f, lng_f in markers_data:
                mk = m.marker(latlng=(lat_f, lng_f))
                created_markers.append((mk, p, loc_name))

            async def bind_all():
                await asyncio.sleep(0.3)
                for mk, p, loc_name in created_markers:
                    if mk.id is not None:
                        safe_loc = html_lib.escape(str(loc_name))
                        safe_path = html_lib.escape(str(p))
                        mk.run_method('bindTooltip', safe_loc)
                        mk.run_method('bindPopup', f'''<a href="#" onclick="emitEvent('exlbl', ['{safe_path}']); return false;" style="text-decoration: underline; cursor: pointer;"><b>{safe_loc}</b></a>''')

            ui.timer(0.1, bind_all, once=True)

    with ui.expansion(f"{get_translation(title_key)} ({len(loc_ids)})", icon='map', value=False, on_value_change=load_locations_map) \
            .classes('w-full border rounded-lg shadow-sm') \
            .props('header-class="font-bold text-lg text-secondary"'):
        map_container = ui.column().classes('w-full p-2')


def render_grouped_module_chips(content: str, category: str, icon: str, on_chip_click) -> bool:
    """Render deduplicated module-grouped entries as clickable ui.chip elements."""
    grouped = extract_grouped_module_entries(content, category)
    if not grouped:
        return False
    with ui.column().classes('w-full gap-3 p-4'):
        for mod, entries in grouped.items():
            with ui.column().classes('w-full gap-1'):
                ui.label(f"{mod} ({len(entries)})").classes('font-bold text-sm text-secondary')
                with ui.row().classes('w-full flex-wrap gap-2'):
                    for key, label in entries:
                        ui.chip(
                            label,
                            icon=icon,
                            on_click=partial(on_chip_click, key),
                        ).props('outline').classes('cursor-pointer font-medium shadow-sm')
    return True


ORIGINAL_LANGUAGE_BIBLES = {
    "ORB", "OLB", "OPB", "OIB", "ODB",
    "OHGB", "OHGBi", "LXX", "LXX1", "LXX1i", "LXX2", "LXX2i",
}


def fetch_chapter_vocabulary(b, c=None, custom=None):
    """Fetch top and rare original-language lemmas for a Bible chapter or entire book (c=None)."""
    db = get_morphology_db(custom)
    where_clause = "WHERE Book=? AND Chapter=? AND LexicalEntry != ''" if c is not None else "WHERE Book=? AND LexicalEntry != ''"
    params = (b, c) if c is not None else (b,)
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(
            f"""
            SELECT LexicalEntry, Lexeme, Gloss, COUNT(*) as cnt
            FROM morphology
            {where_clause}
            GROUP BY LexicalEntry
            ORDER BY cnt DESC
            """,
            params,
        )
        chapter_rows = cursor.fetchall()
        if not chapter_rows:
            return [], []
        top_words = chapter_rows[:15 if c is not None else 20]
        entries = [r[0] for r in chapter_rows]
        placeholders = ",".join("?" for _ in entries)
        cursor.execute(
            f"SELECT LexicalEntry, COUNT(*) as total_cnt FROM morphology WHERE LexicalEntry IN ({placeholders}) GROUP BY LexicalEntry HAVING total_cnt <= 3 ORDER BY total_cnt ASC",
            entries,
        )
        rare_map = dict(cursor.fetchall())
        rare_words = [(r[0], r[1], r[2], r[3], rare_map[r[0]]) for r in chapter_rows if r[0] in rare_map]
    return top_words, rare_words


def fetch_chapter_translation_vocabulary(b, c=None, active_bible="", ui_language="eng", custom=None):
    """Fetch tagged translation vocabulary for a chapter or entire book (c=None), falling back by UI language."""
    db = get_tagged_translations_db(custom)
    fallback_col = {"tc": "CUV", "sc": "CUVs"}.get(ui_language, "NET")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute("PRAGMA table_info(morphology)")
        cols = {row[1] for row in cursor.fetchall()}
        trans_cols = cols - _NON_TRANSLATION_COLS
        if active_bible in trans_cols:
            version_col = active_bible
            matched = True
        elif fallback_col in trans_cols:
            version_col = fallback_col
            matched = False
        else:
            return None, False, [], [], []

        if c is not None:
            cursor.execute(
                f'SELECT Chapter, Verse, LexicalEntry, Lexeme, Gloss, "{version_col}" FROM morphology WHERE Book=? AND Chapter=? AND "{version_col}" != "" ORDER BY WordID',
                (b, c),
            )
        else:
            cursor.execute(
                f'SELECT Chapter, Verse, LexicalEntry, Lexeme, Gloss, "{version_col}" FROM morphology WHERE Book=? AND "{version_col}" != "" ORDER BY WordID',
                (b,),
            )
        rows = cursor.fetchall()
        if not rows:
            return version_col, matched, [], [], []

        entries = list({r[2] for r in rows if r[2]})
        rare_entries = {}
        if entries:
            placeholders = ",".join("?" for _ in entries)
            cursor.execute(
                f"SELECT LexicalEntry, COUNT(*) as total_cnt FROM morphology WHERE LexicalEntry IN ({placeholders}) GROUP BY LexicalEntry HAVING total_cnt <= 3",
                entries,
            )
            rare_entries = dict(cursor.fetchall())

    grouped = {}
    for chap, verse, entry, lexeme, gloss, raw_text in rows:
        cleaned = str(raw_text).strip(_PUNCT_STRIP)
        if not cleaned:
            continue
        key = cleaned.lower() if cleaned.isascii() else cleaned
        item = grouped.get(key)
        if item is None:
            item = {
                "word": cleaned,
                "count": 0,
                "verses": [],
                "chapters": [],
                "lemmas": [],
                "rare_count": None,
                "is_stopword": key in _COMMON_STOPWORDS,
            }
            grouped[key] = item
        item["count"] += 1
        ref_tag = verse if c is not None else f"{chap}:{verse}"
        if ref_tag not in item["verses"]:
            item["verses"].append(ref_tag)
        if chap not in item["chapters"]:
            item["chapters"].append(chap)
        if lexeme:
            lemma_label = f"{lexeme} ({gloss})" if gloss else lexeme
            if lemma_label not in item["lemmas"]:
                item["lemmas"].append(lemma_label)
        if entry in rare_entries:
            rc = rare_entries[entry]
            if item["rare_count"] is None or rc < item["rare_count"]:
                item["rare_count"] = rc

    all_items = sorted(grouped.values(), key=lambda x: (-x["count"], x["chapters"][0]))
    filtered_top = [i for i in all_items if not i["is_stopword"]][:20]
    unfiltered_top = all_items[:20]
    rare_items = [i for i in all_items if i["rare_count"] is not None and not i["is_stopword"]]
    if not rare_items:
        rare_items = [i for i in all_items if i["rare_count"] is not None]
    rare_items.sort(key=lambda x: (x["rare_count"], -x["count"], x["chapters"][0]))
    return version_col, matched, filtered_top, unfiltered_top, rare_items


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
            "table": localized_exlb_table("exlbt"), 
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

            def open_lexicon(module, entry):
                nonlocal gui
                app.storage.user['favorite_lexicon'] = module
                app.storage.user['tool_query'] = entry
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='lexicons')

            def search_bible_word(bible_version, word):
                nonlocal gui
                app.storage.user['tool_book_text'] = bible_version
                if word.isascii() and app.storage.user.get('search_mode') == 2:
                    app.storage.user['tool_query'] = rf"\b{re.escape(word)}\b"
                else:
                    app.storage.user['tool_query'] = word
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Verses')

            # --- CHAPTER TRANSLATION VOCABULARY (expanded by default for translations) ---
            _ORIGINAL_LANGUAGE_BIBLES = {
                "ORB", "OLB", "OPB", "OIB", "ODB",
                "OHGB", "OHGBi", "LXX", "LXX1", "LXX1i", "LXX2", "LXX2i",
            }
            active_bible = gui.get_area_1_bible_text() if gui else app.storage.user.get('primary_bible', 'NET')
            ui_lang = app.storage.user.get('ui_language', 'eng')
            is_original_bible = active_bible in _ORIGINAL_LANGUAGE_BIBLES
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
                        chapter,
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
                            return f"vv. {vv}" + (f" · {lemmas_str}" if lemmas_str else "")

                        hide_common = {'value': True}
                        chips_area = ui.column().classes('w-full gap-2')

                        def render_trans_chips():
                            chips_area.clear()
                            top_list = filtered_top if (hide_common['value'] and filtered_top) else unfiltered_top
                            with chips_area:
                                if top_list:
                                    ui.label(get_translation('Key Words in Chapter')).classes('font-bold text-sm mt-1')
                                    with ui.row().classes('w-full gap-2 flex-wrap'):
                                        for item in top_list:
                                            c = ui.chip(
                                                f"{item['word']} ({item['count']})",
                                                icon='search',
                                                on_click=partial(search_bible_word, version_col, item['word']),
                                            ).props('outline').classes('cursor-pointer')
                                            c.tooltip(_chip_tooltip(item))
                                if rare_items:
                                    ui.label(get_translation('Rare-Lemma Words in Chapter (<= 3x in Bible)')).classes('font-bold text-sm mt-3')
                                    with ui.row().classes('w-full gap-2 flex-wrap'):
                                        for item in rare_items:
                                            rc = item['rare_count']
                                            badge = "1x (hapax)" if rc == 1 else f"{rc}x"
                                            c = ui.chip(
                                                f"{item['word']} [{badge}]",
                                                icon='search',
                                                color='deep-orange' if rc == 1 else 'amber-8',
                                                on_click=partial(search_bible_word, version_col, item['word']),
                                            ).props('text-color=white').classes('cursor-pointer')
                                            c.tooltip(_chip_tooltip(item))

                        def on_toggle_common(ev):
                            hide_common['value'] = bool(ev.value)
                            render_trans_chips()

                        ui.switch(get_translation('Hide common words'), value=True, on_change=on_toggle_common).classes('text-sm')
                        render_trans_chips()

                with ui.expansion(get_translation('Chapter Translation Vocabulary'), icon='translate', value=True, on_value_change=load_trans_vocab) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    trans_vocab_container = ui.column().classes('w-full p-2 gap-2')
                ui.timer(0.05, lambda: load_trans_vocab(type('E', (), {'value': True})()), once=True)

            # --- CHAPTER VOCABULARY & RARE WORDS (lazy-loaded on expand) ---
            vocab_loaded = {'done': False}

            async def load_vocab(e):
                if not e.value or vocab_loaded['done']:
                    return
                vocab_loaded['done'] = True
                vocab_container.clear()
                with vocab_container:
                    ui.spinner(size='sm')
                top_words, rare_words = await run.io_bound(fetch_chapter_vocabulary, book_id, chapter, app.storage.client["custom"])
                vocab_container.clear()
                with vocab_container:
                    if not top_words:
                        ui.label(get_translation('No data found.')).classes('p-2 italic')
                        return
                    ui.label(get_translation('Top Chapter Lemmas')).classes('font-bold text-sm mt-1')
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
                        ui.label(get_translation('Rare Words in Chapter (<= 3x in Bible)')).classes('font-bold text-sm mt-3')
                        with ui.row().classes('w-full gap-2 flex-wrap'):
                            for entry, lexeme, gloss, ch_cnt, total_cnt in rare_words:
                                lex_entry = entry.split(",")[-2] if entry.endswith(",") and len(entry.split(",")) > 1 else entry.split(",")[0]
                                badge_label = "1x (hapax)" if total_cnt == 1 else f"{total_cnt}x"
                                ui.chip(
                                    f"{lexeme} [{badge_label}] — {gloss}",
                                    color='deep-orange' if total_cnt == 1 else 'amber-8',
                                    on_click=partial(open_lexicon, app.storage.user['hebrew_lexicon'] if book_id < 40 else app.storage.user['greek_lexicon'], lex_entry),
                                ).props('text-color=white').classes('cursor-pointer')

            with ui.expansion(get_translation('Chapter Vocabulary & Rare Words'), icon='analytics', value=is_original_bible, on_value_change=load_vocab) \
                    .classes('w-full border rounded-lg shadow-sm') \
                    .props('header-class="font-bold text-lg text-secondary"'):
                vocab_container = ui.column().classes('w-full p-2 gap-2')
            if is_original_bible:
                ui.timer(0.05, lambda: load_vocab(type('E', (), {'value': True})()), once=True)

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
            render_locations_map_expansion(results.get("Bible Locations") or "", "Chapter Map")
            
            def open_exlb(target_title, entry_id):
                nonlocal gui
                app.storage.user['tool_query'] = entry_id
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title=target_title)

            def open_dictionary(entry_id):
                nonlocal gui
                app.storage.user['tool_query'] = entry_id
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Dictionaries')

            def open_encyclopedia(key):
                nonlocal gui
                app.storage.user['favorite_encyclopedia'], app.storage.user['tool_query'] = key
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Encyclopedias')

            for title, config in TABLE_CONFIG.items():
                content = results.get(title)
                
                # Check if this should be open by default
                is_open = False
                
                # Create the Expansion with specific icon
                with ui.expansion(get_translation(title), icon=config['icon'], value=is_open) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    
                    if content:
                        if title in ("Bible People", "Bible Locations"):
                            target_title = "Characters" if title == "Bible People" else "Locations"
                            chip_icon = "person" if title == "Bible People" else "place"
                            if render_exlb_chips(content, chip_icon, partial(open_exlb, target_title)):
                                found_any = True
                            else:
                                ui.label(get_translation('No entries found for this category.')) \
                                    .classes('p-4 italic')
                        elif title == "Bible Topics":
                            if render_grouped_module_chips(content, "topics", "topic", partial(open_exlb, "Topics")):
                                found_any = True
                            else:
                                ui.label(get_translation('No entries found for this category.')) \
                                    .classes('p-4 italic')
                        elif title == "Bible Dictionaries":
                            if render_grouped_module_chips(content, "dictionaries", "loyalty", open_dictionary):
                                found_any = True
                            else:
                                ui.label(get_translation('No entries found for this category.')) \
                                    .classes('p-4 italic')
                        elif title == "Bible Encyclopedia":
                            if render_grouped_module_chips(content, "encyclopedia", "diamond", open_encyclopedia):
                                found_any = True
                            else:
                                ui.label(get_translation('No entries found for this category.')) \
                                    .classes('p-4 italic')
                        else:
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
                ui.notify(get_translation('No data found in any index for this verse.'), type='info')

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
                    top_lemmas, rare_lemmas = await run.io_bound(fetch_chapter_vocabulary, book_id, chapter, app.storage.client["custom"])
                    if top_lemmas:
                        lines.append(f"## {get_translation('Top Chapter Lemmas')}")
                        for _, lexeme, gloss, cnt in top_lemmas:
                            lines.append(f"- {lexeme} ({cnt}x): {gloss}")
                        lines.append("")
                    if rare_lemmas:
                        lines.append(f"## {get_translation('Rare Words in Chapter (<= 3x in Bible)')}")
                        for _, lexeme, gloss, ch_cnt, total_cnt in rare_lemmas:
                            badge = "1x (hapax)" if total_cnt == 1 else f"{total_cnt}x"
                            lines.append(f"- {lexeme} [{badge}]: {gloss}")
                        lines.append("")
                    v_col, _, trans_top, _, _ = await run.io_bound(
                        fetch_chapter_translation_vocabulary,
                        book_id,
                        chapter,
                        active_bible,
                        lang,
                        app.storage.client["custom"],
                    )
                    if v_col and trans_top:
                        lines.append(f"## {get_translation('Key Words in Chapter')} ({v_col})")
                        for item in trans_top:
                            vv = ", ".join(str(v_num) for v_num in item["verses"])
                            lines.append(f"- {item['word']} ({item['count']}x) [vv. {vv}]")
                        lines.append("")
                except Exception:
                    pass
                await download_txt("\n".join(lines))

            with ui.row().classes('w-full justify-end mt-2'):
                ui.button(get_translation('Export Study Sheet'), icon='download', on_click=export_study_sheet).props('outline color=primary')

            def open_chapter_tool(title, setup_fn=None):
                nonlocal gui
                app.storage.user["tool_book_number"] = book_id
                app.storage.user["tool_chapter_number"] = chapter
                app.storage.user["tool_verse_number"] = v
                if setup_fn:
                    setup_fn()
                gui.select_next_area2_tab()
                gui.load_area_2_content(title=title, sync=False)

            def _setup_chapter_map():
                ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(book_id, chapter, v, isChapter=True)
                app.storage.user["tool_query"] = f"{ref}:1-180"

            def _setup_chapter_note():
                app.storage.user["tool_verse_number"] = 0

            with ui.column().classes('w-full gap-2 mt-2 pt-3 border-t border-gray-200'):
                ui.label(get_translation('Chapter Tools')).classes('font-bold text-sm text-secondary')
                with ui.row().classes('w-full gap-2 flex-wrap'):
                    ui.button(get_translation('Chapter Summary'), icon='diamond', on_click=partial(open_chapter_tool, 'Summary')).props('outline size=sm')
                    ui.button(get_translation('Chapter Map'), icon='map', on_click=partial(open_chapter_tool, 'Maps', _setup_chapter_map)).props('outline size=sm')
                    ui.button(get_translation('Bible Podcast'), icon='podcasts', on_click=partial(open_chapter_tool, 'Podcast')).props('outline size=sm')
                    ui.button(get_translation('Bible Audio'), icon='volume_up', on_click=partial(open_chapter_tool, 'Audio')).props('outline size=sm')
                    ui.button(get_translation('Verse Indexes'), icon='list_alt', on_click=partial(open_chapter_tool, 'Indexes')).props('outline size=sm')
                    ui.button(get_translation('Book Indexes'), icon='menu_book', on_click=partial(open_chapter_tool, 'Bookindexes')).props('outline size=sm')
                    if app_config.google_client_id and app_config.google_client_secret:
                        ui.button(get_translation('Notes'), icon='edit_note', on_click=partial(open_chapter_tool, 'Notes', _setup_chapter_note)).props('outline size=sm')
        
    search_action(b,c)

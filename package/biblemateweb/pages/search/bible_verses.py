from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemateweb.fx.bible import add_bible_word_tooltips, build_export_verses_text, build_export_verses_xlsx, get_bible_content, getBiblePath
from biblemateweb import BIBLEMATEWEB_DATA, config, download_docx, download_txt, download_xlsx, get_comparison_bibles, get_morphology_db, get_translation, resolve_verses_additional_options
from collections import Counter
from functools import partial
from nicegui import ui, app, run
import re, apsw, os, difflib, html as html_lib


def search_bible_verses(gui=None, q='', **_):

    last_entry = q
    default_placeholder = get_translation("Search for words or refs")
    multiple_bibles = None
    export_verses_btn = None
    export_docx_btn = None
    limit_notice_label = None
    diff_mode_switch = None
    ot_nt_label = None
    export_table_btn = None

    def get_bibles():
        nonlocal multiple_bibles, gui
        return multiple_bibles.value if multiple_bibles and multiple_bibles.value else gui.get_area_1_bible_text()

    SQL_QUERY = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"

    # --- Data: 66 Bible Books & ID Mapping ---
    BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]

    # Logic Sets
    OT_BOOKS = BIBLE_BOOKS[:39]
    NT_BOOKS = BIBLE_BOOKS[39:]
    SET_OT = set(OT_BOOKS)
    SET_NT = set(NT_BOOKS)

    # Map abbreviations to Book IDs (1-66)
    BOOK_MAP = {book: i + 1 for i, book in enumerate(BIBLE_BOOKS)}

    # Initialize with full selection state
    default_bible = gui.get_area_1_bible_text()
    client_bibles, initial_bibles, initial_books, q = resolve_verses_additional_options(q, default_bible, app.storage.client["custom"])
    
    state = {'previous': initial_books}

    PAGE_SIZE = 100
    results_state = {
        'all_verses': [],
        'filtered_verses': [],
        'rendered_count': 0,
        'highlights': False,
        'query': '',
        'book_counts': {},
        'chapter_counts': {},
        'is_filtered': False,
        'limit_reached': False,
        'book_cache': {},
        'search_params': {},
        'diff_mode': False,
    }
    chart_meta = {'mode': 'book', 'keys': [], 'single_book': None}
    chart_filter = {'book': None, 'chapter': None}

    def get_verse_content(ref, content):
        content = re.sub("<[^<>]+?>", "", content)
        return f"[{ref}] {content}"

    def ask_biblemate(ref, content):
        nonlocal gui
        gui.ask_biblemate(f'''[{ref}] {re.sub("<[^<>]+?>", "", content)}''')

    def _word_diff_html(base_text, other_text):
        base_words = base_text.split()
        other_words = other_text.split()
        matcher = difflib.SequenceMatcher(None, base_words, other_words)
        parts = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            segment = html_lib.escape(" ".join(other_words[j1:j2]))
            if not segment:
                continue
            if tag == 'equal':
                parts.append(segment)
            else:
                parts.append(f"<span style='background-color: rgba(245, 158, 11, 0.3); padding: 0 2px; border-radius: 3px;'>{segment}</span>")
        return " ".join(parts)

    def compare_translations(verse):
        b, c, v_num = verse.get('b'), verse.get('c'), verse.get('v')
        if not (b and c and v_num):
            return
        candidates = []
        selected = get_bibles()
        if isinstance(selected, str):
            selected = [selected]
        for ver in [verse.get('bible'), *get_comparison_bibles(active_bible=verse.get('bible')), app.storage.user.get('secondary_bible'), *(selected or [])]:
            if ver and ver not in candidates and getBiblePath(ver):
                candidates.append(ver)

        rows = []
        for ver in candidates[:6]:
            db_path = getBiblePath(ver)
            try:
                with apsw.Connection(db_path) as connn:
                    cur = connn.cursor()
                    cur.execute("SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse=? LIMIT 1", (b, c, v_num))
                    row = cur.fetchone()
                    if row and row[0]:
                        plain = re.sub("<[^<>]+?>", "", row[0]).strip()
                        rows.append((ver, plain))
            except Exception:
                pass

        with ui.dialog() as dlg, ui.card().classes('w-full max-w-2xl'):
            ui.label(f"{verse['ref']} — {get_translation('Compare Translations')}").classes('text-lg font-bold')
            if not rows:
                ui.label(get_translation('No verses found.'))
            else:
                base_text = rows[0][1]
                for idx, (ver, txt) in enumerate(rows):
                    with ui.column().classes('w-full p-2 rounded border border-gray-200 gap-1'):
                        ui.badge(ver, color='primary' if idx == 0 else 'secondary')
                        if idx == 0:
                            ui.label(txt).classes('text-base leading-relaxed')
                        else:
                            ui.html(_word_diff_html(base_text, txt), sanitize=False).classes('text-base leading-relaxed')
            with ui.row().classes('w-full justify-end'):
                ui.button(get_translation('Close'), on_click=dlg.close).props('flat')
        dlg.open()

    def update_load_more_button():
        remaining = len(results_state['filtered_verses']) - results_state['rendered_count']
        if remaining > 0:
            next_batch = min(PAGE_SIZE, remaining)
            load_more_btn.text = f"{get_translation('Load more')} ({next_batch} / {remaining} {get_translation('remaining')})"
            load_more_btn.set_visibility(True)
        else:
            load_more_btn.set_visibility(False)
        if export_verses_btn is not None:
            export_verses_btn.set_visibility(bool(results_state['filtered_verses']))
        if export_docx_btn is not None:
            export_docx_btn.set_visibility(bool(results_state['filtered_verses']))
        if diff_mode_switch is not None:
            seen_coords = {}
            has_multi_ver = False
            for item in results_state['filtered_verses']:
                coord = (item.get('b'), item.get('c'), item.get('v'))
                if coord[0]:
                    prev_b = seen_coords.get(coord)
                    if prev_b is not None and prev_b != item.get('bible'):
                        has_multi_ver = True
                        break
                    seen_coords[coord] = item.get('bible')
            diff_mode_switch.set_visibility(has_multi_ver)
            if export_table_btn is not None:
                export_table_btn.set_visibility(has_multi_ver)
        if limit_notice_label is not None:
            show_notice = results_state['limit_reached'] and not results_state['is_filtered']
            if show_notice:
                total_matches = sum(results_state['book_counts'].values()) or len(results_state['all_verses'])
                limit_notice_label.text = (
                    f"{get_translation('Showing first')} {len(results_state['all_verses'])} "
                    f"{get_translation('of')} {total_matches} "
                    f"{get_translation('matches — click any book in Distribution Analysis to load that book')}"
                )
            limit_notice_label.set_visibility(show_notice)

    def render_verse_batch():
        start = results_state['rendered_count']
        end = start + PAGE_SIZE
        batch = results_state['filtered_verses'][start:end]
        if not batch:
            update_load_more_button()
            return

        highlights = results_state['highlights']
        search_query = results_state['query']
        diff_mode = results_state['diff_mode']
        base_plain_map = {}
        if diff_mode:
            for item in results_state['filtered_verses']:
                coord = (item.get('b'), item.get('c'), item.get('v'))
                if coord[0] and coord not in base_plain_map:
                    base_plain_map[coord] = (item.get('bible'), re.sub(r"<[^<>]+?>", "", str(item.get('content', ''))).strip())

        with verses_container:
            for v in batch:
                with ui.column().classes('w-full shadow-sm rounded-lg items-start no-wrap border border-gray-200 !gap-0') as row:
                    row.verse_data = v

                    with ui.element('div').classes('flex-none pt-1'):
                        with ui.chip(
                            v['ref'],
                            removable=True,
                            icon='book',
                        ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm') as chip:
                            with ui.menu():
                                ui.menu_item('📋 Copy', on_click=partial(gui.copy_text, get_verse_content(v['ref'], v['content'])))
                                ui.menu_item(f"🔍 {get_translation('Compare Translations')}", on_click=partial(compare_translations, v))
                                ui.separator()
                                ui.menu_item('📜 Open in Bible Area', on_click=partial(gui.change_area_1_bible_chapter, v['bible'], v['b'], v['c'], v['v']))
                                ui.menu_item('📜 Open Here', on_click=partial(gui.change_area_2_bible_chapter, v['bible'], v['b'], v['c'], v['v'], sync=False))
                                ui.menu_item('📜 Open in Next Tab', on_click=partial(open_chapter_next_area2_tab, v['bible'], v['b'], v['c'], v['v']))
                                ui.menu_item('📜 Open in New Tab', on_click=partial(open_chapter_empty_area2_tab, v['bible'], v['b'], v['c'], v['v']))
                                ui.separator()
                                ui.menu_item('💬 Ask BibleMate', on_click=partial(ask_biblemate, v['ref'], v['content']))
                        chip.on('remove', lambda _, r=row, verse=v: remove_verse_row(r, verse['ref'], verse))

                    content = v['content']
                    coord = (v.get('b'), v.get('c'), v.get('v'))
                    if diff_mode and coord in base_plain_map and base_plain_map[coord][0] != v.get('bible'):
                        plain_txt = re.sub(r"<[^<>]+?>", "", str(content)).strip()
                        content = _word_diff_html(base_plain_map[coord][1], plain_txt)
                    else:
                        content = add_bible_word_tooltips(content, v.get('bible', ''))
                        if highlights and search_query:
                            if app.storage.user["dark_mode"]:
                                content = re.sub(f"({search_query})", r"<font color='orange'>\1</font>", content, flags=0 if app.storage.user['search_case_sensitivity'] else re.IGNORECASE)
                            else:
                                content = re.sub(f"({search_query})", r"<span style='background-color: orange;'>\1</span>", content, flags=0 if app.storage.user['search_case_sensitivity'] else re.IGNORECASE)
                    ui.html(content, sanitize=False).classes('grow min-w-0 leading-relaxed pl-2 text-base break-words')

        results_state['rendered_count'] += len(batch)
        update_load_more_button()

    # ----------------------------------------------------------
    # Helper: Filter Logic
    # ----------------------------------------------------------
    def filter_verses(e=None):
        """
        Filters cached search results based on input and renders the first page.
        """
        if not results_state['all_verses']:
            return

        if e is not None and hasattr(e, 'value'):
            text = e.value
        else:
            text = input_field.value

        search_term = text if text else ""
        case_sensitive = app.storage.user['search_case_sensitivity']
        if not case_sensitive:
            search_term = search_term.lower()

        if not search_term:
            results_state['is_filtered'] = False
            if len(results_state['filtered_verses']) == len(results_state['all_verses']) and results_state['rendered_count'] > 0:
                update_load_more_button()
                return
            results_state['filtered_verses'] = list(results_state['all_verses'])
            verses_container.clear()
            results_state['rendered_count'] = 0
            render_verse_batch()
            if analysis_expansion.value:
                update_distribution_chart()
            return

        matched = []
        use_regex = not (app.storage.user['search_mode'] == 2)
        for data in results_state['all_verses']:
            ref_text = data['ref'] if case_sensitive else data['ref'].lower()
            clean_content = re.sub('<[^<]+?>', '', data['content'])
            if not case_sensitive:
                clean_content = clean_content.lower()

            if use_regex:
                try:
                    is_match = bool(re.search(search_term, ref_text) or re.search(search_term, clean_content))
                except re.error:
                    is_match = (search_term in ref_text) or (search_term in clean_content)
            else:
                is_match = (search_term in ref_text) or (search_term in clean_content)

            if is_match:
                matched.append(data)

        results_state['filtered_verses'] = matched
        results_state['is_filtered'] = True
        verses_container.clear()
        results_state['rendered_count'] = 0
        render_verse_batch()
        if analysis_expansion.value:
            update_distribution_chart()

        if matched:
            ui.notify(f"{len(matched)} {'match' if len(matched) == 1 else 'matches'} found!")

    async def _fetch_book_verses(b_filter):
        params = results_state.get('search_params') or {}
        if not params:
            return []
        parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        refs = params.get('refs')
        if refs is not None:
            book_refs = [r for r in refs if r[0] == b_filter]
            if not book_refs:
                return []
            verses = await run.io_bound(
                get_bible_content,
                bible=params['bibles'],
                sql_query=params['sql_query'],
                refs=book_refs,
                parser=parser,
            )
        else:
            scoped_sql = re.sub(r'\bWHERE\b', f'WHERE Book={int(b_filter)} AND', params['sql_query'], count=1, flags=re.IGNORECASE)
            verses = await run.io_bound(
                get_bible_content,
                user_input=params['query'],
                bible=params['bibles'],
                sql_query=scoped_sql,
                search_mode=app.storage.user['search_mode'],
                top_similar_verses=app.storage.user['top_similar_verses'],
                search_case_sensitivity=app.storage.user['search_case_sensitivity'],
                parser=parser,
            )
        if verses and not verses[-1]['ref']:
            verses = verses[:-1]
        return verses

    async def apply_chart_filter():
        b_filter = chart_filter['book']
        c_filter = chart_filter['chapter']
        if b_filter is None:
            results_state['filtered_verses'] = list(results_state['all_verses'])
            results_state['is_filtered'] = bool(input_field.value and input_field.value.strip())
            reset_chart_filter_btn.set_visibility(False)
        else:
            in_memory = [
                v for v in results_state['all_verses']
                if v.get('b') == b_filter and (c_filter is None or v.get('c') == c_filter)
            ]
            expected_book_total = results_state['book_counts'].get(b_filter, 0)
            in_memory_book_total = sum(1 for v in results_state['all_verses'] if v.get('b') == b_filter)
            if results_state['limit_reached'] and in_memory_book_total < expected_book_total:
                if b_filter not in results_state['book_cache']:
                    n = ui.notification(get_translation('Loading ...'), timeout=None, spinner=True)
                    try:
                        results_state['book_cache'][b_filter] = await _fetch_book_verses(b_filter)
                    finally:
                        n.dismiss()
                book_verses = results_state['book_cache'][b_filter]
                results_state['filtered_verses'] = [
                    v for v in book_verses
                    if c_filter is None or v.get('c') == c_filter
                ]
            else:
                results_state['filtered_verses'] = in_memory
            results_state['is_filtered'] = True
            reset_chart_filter_btn.set_visibility(True)
        verses_container.clear()
        results_state['rendered_count'] = 0
        render_verse_batch()
        if analysis_expansion.value:
            update_distribution_chart()

    async def reset_chart_filter():
        chart_filter['book'] = None
        chart_filter['chapter'] = None
        await apply_chart_filter()

    async def handle_chart_click(e):
        idx = getattr(e, 'data_index', None)
        if idx is None or idx < 0 or idx >= len(chart_meta['keys']):
            return
        clicked_key = chart_meta['keys'][idx]
        if chart_meta['mode'] == 'book':
            chart_filter['book'] = clicked_key
            chart_filter['chapter'] = None
            await apply_chart_filter()
        elif chart_meta['mode'] == 'chapter':
            if chart_filter['chapter'] == clicked_key:
                chart_filter['book'] = None
                chart_filter['chapter'] = None
            else:
                chart_filter['book'] = chart_meta['single_book']
                chart_filter['chapter'] = clicked_key
            await apply_chart_filter()

    def update_morphology_chart():
        search_morph = re.search(r"^([EG][0-9]+?)\|", last_entry or '')
        if not search_morph:
            morph_chart.set_visibility(False)
            return
        lexical_entry = search_morph.group(1) + ",%"
        suffix = ""
        for i in (last_entry or '').split("|")[1:]:
            if i:
                suffix += f"AND Morphology LIKE '{i}' "
        if books := re.search("WHERE (Book.*?) AND", SQL_QUERY):
            suffix += f"AND {books.group(1)} "
        if chart_filter['book'] is not None:
            suffix += f"AND Book={int(chart_filter['book'])} "
        if chart_filter['chapter'] is not None:
            suffix += f"AND Chapter={int(chart_filter['chapter'])} "
        try:
            db = get_morphology_db(app.storage.client["custom"])
            with apsw.Connection(db) as connn:
                cursor = connn.cursor()
                cursor.execute(
                    f"SELECT Morphology, COUNT(*) as cnt FROM morphology WHERE LexicalEntry LIKE ? {suffix}GROUP BY Morphology ORDER BY cnt DESC LIMIT 25",
                    (lexical_entry,),
                )
                rows = cursor.fetchall()
        except Exception:
            rows = []

        if not rows:
            morph_chart.set_visibility(False)
            return

        dark = app.storage.user.get('dark_mode', False)
        text_color = '#e5e7eb' if dark else '#1f2937'
        split_color = '#374151' if dark else '#e5e7eb'
        bg_color = '#1f2937' if dark else '#ffffff'

        m_labels = [r[0].rstrip(',') for r in rows]
        m_values = [r[1] for r in rows]
        morph_chart.style(f'height: {max(220, len(m_labels) * 26 + 80)}px;')
        morph_chart.options.clear()
        morph_chart.options.update({
            'backgroundColor': bg_color,
            'title': {
                'text': f"{get_translation('Morphology Breakdown')} ({sum(m_values)})",
                'left': 'center',
                'top': 8,
                'textStyle': {'color': text_color, 'fontSize': 14},
            },
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'grid': {'left': 20, 'right': 50, 'top': 48, 'bottom': 20, 'containLabel': True},
            'xAxis': {
                'type': 'value',
                'minInterval': 1,
                'axisLabel': {'color': text_color},
                'splitLine': {'lineStyle': {'color': split_color}},
            },
            'yAxis': {
                'type': 'category',
                'data': m_labels,
                'inverse': True,
                'axisLabel': {'color': text_color, 'interval': 0},
            },
            'series': [{
                'type': 'bar',
                'data': m_values,
                'barMaxWidth': 20,
                'itemStyle': {'color': '#f97316', 'borderRadius': [0, 4, 4, 0]},
                'label': {'show': True, 'position': 'right', 'color': text_color},
            }],
        })
        morph_chart.set_visibility(True)
        morph_chart.update()

    def update_distribution_chart():
        use_uncapped = not results_state['is_filtered'] and results_state['book_counts']
        if use_uncapped:
            book_counts = {b: c for b, c in results_state['book_counts'].items() if b and c > 0}
        else:
            verses = results_state['filtered_verses']
            book_counts = Counter(v['b'] for v in verses if v.get('b'))

        book_ids = sorted(book_counts.keys())
        if ot_nt_label is not None:
            ot_total = sum(cnt for bk, cnt in book_counts.items() if bk < 40)
            nt_total = sum(cnt for bk, cnt in book_counts.items() if bk >= 40)
            ot_nt_label.text = f"{get_translation('OT')}: {ot_total}  |  {get_translation('NT')}: {nt_total}"
        lang = app.storage.user.get('ui_language', 'eng')
        abbrev_map = BibleBooks.abbrev.get(lang, BibleBooks.abbrev['eng'])

        if len(book_ids) == 1:
            single_book = book_ids[0]
            book_abbrev = abbrev_map[str(single_book)][0] if str(single_book) in abbrev_map else str(single_book)
            if use_uncapped and results_state['chapter_counts']:
                chap_counts = {
                    c: cnt for (b, c), cnt in results_state['chapter_counts'].items()
                    if b == single_book and cnt > 0
                }
            else:
                chap_counts = Counter(
                    v['c'] for v in results_state['filtered_verses']
                    if v.get('b') == single_book and v.get('c')
                )
            chapters = sorted(chap_counts.keys())
            labels = [f"{book_abbrev} {c}" for c in chapters]
            values = [chap_counts[c] for c in chapters]
            chart_meta['mode'] = 'chapter'
            chart_meta['keys'] = chapters
            chart_meta['single_book'] = single_book
        else:
            labels = [abbrev_map[str(b)][0] if str(b) in abbrev_map else str(b) for b in book_ids]
            if results_state['limit_reached']:
                loaded_books = {v['b'] for v in results_state['all_verses'] if v.get('b')} | set(results_state['book_cache'].keys())
                values = [
                    {
                        'value': book_counts[b],
                        'itemStyle': {'color': '#3b82f6' if b in loaded_books else '#93c5fd'},
                    }
                    for b in book_ids
                ]
            else:
                values = [book_counts[b] for b in book_ids]
            chart_meta['mode'] = 'book'
            chart_meta['keys'] = book_ids
            chart_meta['single_book'] = None

        dark = app.storage.user.get('dark_mode', False)
        text_color = '#e5e7eb' if dark else '#1f2937'
        split_color = '#374151' if dark else '#e5e7eb'
        bg_color = '#1f2937' if dark else '#ffffff'

        search_label = last_entry or results_state['query'] or ''
        total_count = sum(v['value'] if isinstance(v, dict) else v for v in values)
        chart_title = f"{search_label} ({total_count})" if search_label else f"{total_count}"
        if results_state['limit_reached'] and chart_meta['mode'] == 'book':
            chart_title += f" — {get_translation('click any book to load')}"
        safe_filename = re.sub(r'[^\w\-]+', '_', search_label).strip('_') or 'bible_search_distribution'

        chart_height = max(240, len(labels) * 28 + 90)
        analysis_chart.style(f'height: {chart_height}px;')

        options = {
            'backgroundColor': bg_color,
            'title': {
                'text': chart_title,
                'left': 'center',
                'top': 8,
                'textStyle': {'color': text_color, 'fontSize': 15},
            },
            'tooltip': {
                'trigger': 'axis',
                'axisPointer': {'type': 'shadow'},
            },
            'toolbox': {
                'right': 16,
                'top': 4,
                'feature': {
                    'saveAsImage': {
                        'show': True,
                        'title': get_translation('Download'),
                        'name': safe_filename,
                        'pixelRatio': 3,
                        'backgroundColor': bg_color,
                    }
                },
            },
            'grid': {
                'left': 20,
                'right': 50,
                'top': 52,
                'bottom': 24,
                'containLabel': True,
            },
            'xAxis': {
                'type': 'value',
                'minInterval': 1,
                'axisLabel': {'color': text_color},
                'splitLine': {'lineStyle': {'color': split_color}},
            },
            'yAxis': {
                'type': 'category',
                'data': labels,
                'inverse': True,
                'axisLabel': {'color': text_color, 'interval': 0},
            },
            'series': [
                {
                    'type': 'bar',
                    'data': values,
                    'barMaxWidth': 22,
                    'itemStyle': {
                        'color': '#3b82f6',
                        'borderRadius': [0, 4, 4, 0],
                    },
                    'label': {
                        'show': True,
                        'position': 'right',
                        'color': text_color,
                    },
                }
            ],
        }
        analysis_chart.options.clear()
        analysis_chart.options.update(options)
        analysis_chart.update()
        update_morphology_chart()

    # ----------------------------------------------------------
    # Helper: Remove Verse
    # ----------------------------------------------------------
    def remove_verse_row(row_element, reference, verse_data=None):
        try:
            verses_container.remove(row_element)
            if verse_data is not None:
                if verse_data in results_state['all_verses']:
                    results_state['all_verses'].remove(verse_data)
                if verse_data in results_state['filtered_verses']:
                    results_state['filtered_verses'].remove(verse_data)
                    results_state['rendered_count'] = max(0, results_state['rendered_count'] - 1)
                b = verse_data.get('b')
                c = verse_data.get('c')
                if b and b in results_state['book_counts']:
                    results_state['book_counts'][b] = max(0, results_state['book_counts'][b] - 1)
                if b and c and (b, c) in results_state['chapter_counts']:
                    results_state['chapter_counts'][(b, c)] = max(0, results_state['chapter_counts'][(b, c)] - 1)
                update_load_more_button()
                if analysis_expansion.value:
                    update_distribution_chart()
            ui.notify(f'Removed: {reference}', type='warning', position='top')
        except Exception as e:
            print(f"Error removing row: {e}")

    # ----------------------------------------------------------
    # Helper: Open Chapter
    # ----------------------------------------------------------
    def open_chapter_next_area2_tab(bible, b, c, v):
        gui.select_next_area2_tab()
        gui.change_area_2_bible_chapter(bible, b, c, v, sync=False)

    def open_chapter_empty_area2_tab(bible, b, c, v):
        gui.select_empty_area2_tab()
        gui.change_area_2_bible_chapter(bible, b, c, v, sync=False)

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------
    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    async def handle_enter(e, keep=True):
        nonlocal SQL_QUERY, last_entry
        query = input_field.value.strip()
    
        # Clear existing rows and cached results first
        verses_container.clear()
        results_state['all_verses'] = []
        results_state['filtered_verses'] = []
        results_state['rendered_count'] = 0
        results_state['highlights'] = False
        results_state['query'] = ''
        results_state['book_counts'] = {}
        results_state['chapter_counts'] = {}
        results_state['is_filtered'] = False
        results_state['limit_reached'] = False
        results_state['book_cache'] = {}
        results_state['search_params'] = {}
        chart_filter['book'] = None
        chart_filter['chapter'] = None
        reset_chart_filter_btn.set_visibility(False)
        morph_chart.set_visibility(False)
        update_load_more_button()
        analysis_expansion.set_visibility(False)

        if not query:
            ui.notify('Display cleared', type='positive', position='top')
            input_field.props(f'placeholder="{default_placeholder}"')
            return

        # update tab record
        last_entry = query
        if keep:
            gui.update_active_area2_tab_records(q=query)

        input_field.disable()
        parser = BibleVerseParser(False, language=app.storage.user['ui_language'])

        try:
            n = ui.notification("Loading ...", timeout=None, spinner=True)
            highlights = False
            fetch = None
            book_counts = {}
            chapter_counts = {}
            if search_morphology := re.search(r"^([EG][0-9]+?)\|", query): # search morphology
                multiple_bibles.value = [app.storage.user["tool_book_text"]]
                lexical_entry = search_morphology.group(1) + ",%"
                suffix = ""
                for i in query.split("|")[1:]:
                    suffix += f"AND Morphology LIKE '{i}' "
                if books := re.search("WHERE (Book.*?) AND", SQL_QUERY):
                    suffix += f"AND {books.group(1)} " # limit morphology search in particular books
                db = get_morphology_db(app.storage.client["custom"])
                with apsw.Connection(db) as connn:
                    query = f"SELECT Book, Chapter, Verse FROM morphology WHERE LexicalEntry LIKE ? {suffix}ORDER BY Book, Chapter, Verse"
                    cursor = connn.cursor()
                    cursor.execute(query, (lexical_entry,))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify(get_translation('No verses found.'), type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
            elif re.search("^BP[0-9]+?$", query): # bible characters entries
                lang = app.storage.user.get("ui_language", "eng")
                people_table = f"PEOPLE_{lang.upper()}" if lang in ("tc", "sc") else "PEOPLE"
                db_file = os.path.join(BIBLEMATEWEB_DATA, "data", "biblePeople.data")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute(f"SELECT Book, Chapter, Verse FROM {people_table} WHERE PersonID=? ORDER BY Book, Chapter, Verse", (int(query[2:]),))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify(get_translation('No verses found.'), type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
            elif re.search("^BL[0-9]+?$", query): # bible locatios entries
                lang = app.storage.user.get("ui_language", "eng")
                exlbl_tbl = f"exlbl_{lang}" if lang in ("tc", "sc") else "exlbl"
                db_file = os.path.join(BIBLEMATEWEB_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute(f'''SELECT Book, Chapter, Verse FROM {exlbl_tbl} WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify(get_translation('No verses found.'), type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
            elif re.search(f'''^({"|".join(list(config.topics.keys()))})[0-9]+?$''', query): # bible topics entries
                lang = app.storage.user.get("ui_language", "eng")
                exlbt_tbl = f"exlbt_{lang}" if lang in ("tc", "sc") else "exlbt"
                db_file = os.path.join(BIBLEMATEWEB_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute(f'''SELECT Book, Chapter, Verse FROM {exlbt_tbl} WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify(get_translation('No verses found.'), type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
            elif re.search(f'''^({"|".join(list(config.dictionaries.keys()))})[0-9]+?$''', query): # bible dictionaries entries
                db_file = os.path.join(BIBLEMATEWEB_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute('''SELECT Book, Chapter, Verse FROM dictionaries WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify(get_translation('No verses found.'), type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
            elif re.search(f'''^(ISBE|{"|".join(list(config.encyclopedias.keys()))})[0-9]+?$''', query): # bible encyclopedia entries
                db_file = os.path.join(BIBLEMATEWEB_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute('''SELECT Book, Chapter, Verse FROM encyclopedia WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify(get_translation('No verses found.'), type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
            else: # regular search
                verses = await run.io_bound(get_bible_content, user_input=query, bible=get_bibles(), sql_query=SQL_QUERY, search_mode=app.storage.user['search_mode'], top_similar_verses=app.storage.user['top_similar_verses'], search_case_sensitivity=app.storage.user['search_case_sensitivity'], parser=parser, book_counts=book_counts, chapter_counts=chapter_counts)
                highlights = True

            if not verses:
                ui.notify('No verses found.', type='negative')
                return

            limit_reached = False
            if not verses[-1]['ref']:
                limit_reached = True
                ui.notify(verses[-1]['content'])
                verses = verses[:-1]

            results_state['all_verses'] = verses
            results_state['filtered_verses'] = list(verses)
            results_state['rendered_count'] = 0
            results_state['highlights'] = highlights
            results_state['query'] = query
            results_state['book_counts'] = book_counts
            results_state['chapter_counts'] = chapter_counts
            results_state['is_filtered'] = False
            results_state['limit_reached'] = limit_reached
            results_state['book_cache'] = {}
            results_state['search_params'] = {
                'query': query,
                'refs': fetch,
                'bibles': get_bibles(),
                'sql_query': SQL_QUERY,
            }
            render_verse_batch()
            analysis_expansion.set_visibility(True)
            if analysis_expansion.value:
                update_distribution_chart()

            # Clear input so user can start typing to filter immediately
            input_field.value = ""
            input_field.props(f'''placeholder="{get_translation('Type to filter')} {len(verses)} {get_translation('results')}..."''')
            ui.notify(f"{len(verses)} {get_translation('result') if not verses or len(verses) == 1 else get_translation('results')}")

        except Exception as e:
            # Handle errors (e.g., network failure)
            #ui.notify(f'Error: {e}', type='negative')
            n.message = f'Error: {str(e)}'
            n.type = 'negative'
        finally:
            n.dismiss()
            # ALWAYS re-enable the input, even if an error occurred above
            input_field.enable()
            # Optional: Refocus the cursor so the user can type the next query immediately
            input_field.run_method('focus')

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=BIBLE_BOOKS,
            placeholder=default_placeholder
        ).classes('flex-grow text-lg') \
        .props('outlined clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        input_field.on('update:model-value', filter_verses)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

        # 2. Scope Dropdown
        # Options: All, None, OT, NT, then the books
        options = ['All', 'None', 'OT', 'NT'] + BIBLE_BOOKS
        
        scope_select = ui.select(
            options=options,
            #label='Search',
            multiple=True,
            with_input=True
        ).classes('w-22').props('dense clearable')

        def update_sql_query(selected_values):
            """Generates the SQLite query based on selection."""
            nonlocal SQL_QUERY
            
            # Filter to keep ONLY the actual book strings (ignore All/None/OT/NT)
            real_books = [b for b in selected_values if b in BIBLE_BOOKS]
            book_ids = [str(BOOK_MAP[b]) for b in real_books]
            
            base_query = "PRAGMA case_sensitive_like = false; SELECT * FROM Verses"
            where_clauses = []

            # Handle Book Logic
            if 'All' in selected_values:
                pass 
            elif not real_books:
                where_clauses.append("1=0")
            elif len(real_books) == 1:
                where_clauses.append(f"Book={book_ids[0]}")
            else:
                # Optimization: check if it's exactly OT or NT for cleaner SQL?
                # (Optional, but strictly sticking to IDs is safer for the engine)
                where_clauses.append(f"Book IN ({', '.join(book_ids)})")

            where_clauses.append(f"(Scripture REGEXP ?) ORDER BY Book, Chapter, Verse")

            # Assemble
            full_query = base_query
            if where_clauses:
                full_query += " WHERE " + " AND ".join(where_clauses)
            
            #ui.notify(full_query)
            SQL_QUERY = full_query

        def handle_scope_change(e):
            """
            Handles complex logic for All, None, OT, NT and individual books.
            """
            current = e.value if e.value else []
            previous = state['previous']
            
            # 1. Determine Triggers
            added = set(current) - set(previous)
            removed = set(previous) - set(current)
            
            # Start with the currently selected actual books
            selected_books = set(x for x in current if x in BIBLE_BOOKS)

            # 2. Apply High-Level Triggers
            # Priority: None > All > OT/NT > Individual removals

            if 'None' in added:
                selected_books.clear()
            
            elif 'All' in added:
                selected_books = set(BIBLE_BOOKS)
            
            elif 'OT' in added:
                selected_books.update(SET_OT)
            
            elif 'NT' in added:
                selected_books.update(SET_NT)
            
            # Handle Removals of Groups
            # We only remove the group's books if the group TAG was explicitly removed
            elif 'All' in removed and len(removed) == 1:
                 # User clicked 'All' to uncheck it -> Clear all
                 selected_books.clear()
            
            elif 'OT' in removed:
                # Check if OT tag was explicitly removed (not just because a child book was clicked)
                # If a child was clicked, 'removed' contains {'ChildBook'}.
                # If OT tag was clicked, 'removed' contains {'OT'}.
                # Note: NiceGUI might remove OT from 'current' automatically if child removed,
                # but 'removed' set captures the diff.
                if not (removed & SET_OT): # If no individual OT books were in the removed set
                    selected_books -= SET_OT

            elif 'NT' in removed:
                if not (removed & SET_NT):
                    selected_books -= SET_NT

            # 3. Reconstruct Selection State
            # We rebuild the list from scratch based on the books we decided are selected
            new_selection = []
            
            # Helper: Check completeness
            has_ot = SET_OT.issubset(selected_books)
            has_nt = SET_NT.issubset(selected_books)
            has_all = len(selected_books) == 66
            is_empty = len(selected_books) == 0

            # Add Meta Tags
            if has_all:
                new_selection.append('All')
            if is_empty:
                new_selection.append('None')
            if has_ot:
                new_selection.append('OT')
            if has_nt:
                new_selection.append('NT')

            # Add Books (maintain order)
            for book in BIBLE_BOOKS:
                if book in selected_books:
                    new_selection.append(book)

            # 4. Update UI and State
            if set(new_selection) != set(current):
                scope_select.value = new_selection
                state['previous'] = new_selection
                update_sql_query(new_selection)
                return

            state['previous'] = current
            update_sql_query(current)

        # Checkbox
        ui.checkbox(
            get_translation('Case-sensitive')
        ).bind_value(
            app.storage.user, 'search_case_sensitivity'
        ).props('dense')
            
        # Radio Buttons
        # options: dictionary maps the stored value (keys) to the display label (values)
        # props('inline'): makes the radio buttons layout horizontally
        modes = ui.radio(
            options={1: get_translation('Literal'), 2: get_translation('Regex'), 3: get_translation('Semantic')},
        ).bind_value(
            app.storage.user, 'search_mode'
        ).props('dense inline color=primary')
        #modes.tooltip = ui.tooltip('Search Modes:\n1. Literal search for plain text\n2. Search for regular expression\n3. Semantic search for meaning')

        # Multi-select dropdown
        multiple_bibles = ui.select(
            client_bibles,
            value=initial_bibles,
            #label='Select Bibles to search', 
            multiple=True,
            with_input=True,
        ).classes('grow').props('use-chips outlined dense clearable')

        # --- Bindings ---
        scope_select.on_value_change(handle_scope_change)

        # Initialize
        scope_select.value = initial_books

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        with ui.expansion(
            get_translation('Distribution Analysis'),
            icon='bar_chart',
            value=False,
            on_value_change=lambda e: update_distribution_chart() if e.value else None,
        ).classes('w-full rounded-lg border border-gray-200') as analysis_expansion:
            with ui.row().classes('w-full items-center justify-between px-2'):
                ot_nt_label = ui.label('').classes('text-xs font-semibold text-secondary')
                reset_chart_filter_btn = ui.button(
                    get_translation('Reset Filter'),
                    icon='filter_alt_off',
                    on_click=reset_chart_filter,
                ).props('flat dense size=sm')
                reset_chart_filter_btn.set_visibility(False)
            analysis_chart = ui.echart({}, on_point_click=handle_chart_click).classes('w-full cursor-pointer')
            morph_chart = ui.echart({}).classes('w-full mt-4')
            morph_chart.set_visibility(False)
        analysis_expansion.set_visibility(False)

        async def export_filtered_verses(fmt='txt'):
            verses = list(results_state['filtered_verses'])
            if not verses:
                ui.notify(get_translation('No verses found.'), type='info')
                return
            if fmt == 'xlsx':
                xlsx_bytes = await run.io_bound(build_export_verses_xlsx, verses)
                await download_xlsx(xlsx_bytes)
            elif fmt == 'docx':
                use_table = bool(export_table_btn and export_table_btn.visible)
                content = await run.io_bound(build_export_verses_text, verses, use_table)
                await download_docx(content)
            else:
                content = await run.io_bound(build_export_verses_text, verses, False)
                await download_txt(content)

        def on_toggle_diff_mode(e):
            results_state['diff_mode'] = bool(e.value)
            verses_container.clear()
            results_state['rendered_count'] = 0
            render_verse_batch()

        with ui.row().classes('w-full items-center justify-between gap-2'):
            limit_notice_label = ui.label('').classes('text-xs text-amber-700 dark:text-amber-300 italic')
            limit_notice_label.set_visibility(False)
            with ui.row().classes('items-center gap-2 ml-auto'):
                diff_mode_switch = ui.switch(
                    get_translation('Highlight Differences'),
                    value=False,
                    on_change=on_toggle_diff_mode,
                ).props('dense').classes('text-sm')
                diff_mode_switch.set_visibility(False)
                export_table_btn = ui.button(
                    get_translation('Export Table'),
                    icon='table_chart',
                    on_click=lambda: export_filtered_verses('xlsx'),
                ).props('outline size=sm color=secondary')
                export_table_btn.set_visibility(False)
                export_docx_btn = ui.button(
                    'DOCX',
                    icon='description',
                    on_click=lambda: export_filtered_verses('docx'),
                ).props('outline size=sm color=secondary')
                export_docx_btn.set_visibility(False)
                export_verses_btn = ui.button(
                    get_translation('Export Verses'),
                    icon='download',
                    on_click=lambda: export_filtered_verses('txt'),
                ).props('outline size=sm color=primary')
                export_verses_btn.set_visibility(False)

        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')
        load_more_btn = ui.button(get_translation('Load more'), on_click=render_verse_batch).props('outline').classes('my-2')
        load_more_btn.set_visibility(False)

    if q:
        input_field.value = q
        #handle_enter(None, keep=False) # RuntimeWarning: coroutine 'search_bible_verses.<locals>.handle_enter' was never awaited
        ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    else:
        input_field.run_method('focus')
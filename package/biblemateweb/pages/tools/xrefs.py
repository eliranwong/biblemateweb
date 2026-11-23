from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from biblemateweb import BIBLEMATEWEB_DATA, get_translation
from biblemateweb.fx.bible import get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from collections import Counter
from functools import partial
from nicegui import ui, app, run
import re, apsw, os

def fetch_xrefs(b, c, v):
    db = os.path.join(BIBLEMATEWEB_DATA, "cross-reference.sqlite")
    with apsw.Connection(db) as connn:
        sql_query = "SELECT Information FROM ScrollMapper WHERE Book=? AND Chapter=? AND Verse=? limit 1"
        cursor = connn.cursor()
        cursor.execute(sql_query, (b, c, v))
        query = cursor.fetchone()
        return query

def xrefs(gui=None, b=1, c=1, v=1, q='', **_):

    last_entry = q
    SQL_QUERY = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"

    # --- Data: 66 Bible Books & ID Mapping ---
    BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]
    xref_verses_cache = []
    xref_chart_meta = {'mode': 'book', 'keys': [], 'single_book': None}
    xref_chart_filter = {'book': None, 'chapter': None}

    def apply_xref_chart_filter():
        b_filter = xref_chart_filter['book']
        c_filter = xref_chart_filter['chapter']
        for row in verses_container.default_slot.children:
            if not hasattr(row, 'verse_data'):
                continue
            if b_filter is None:
                row.set_visibility(True)
            else:
                d = row.verse_data
                row.set_visibility(d.get('b') == b_filter and (c_filter is None or d.get('c') == c_filter))
        reset_xref_filter_btn.set_visibility(b_filter is not None)
        if xref_expansion.value:
            update_xref_chart()

    def reset_xref_chart_filter():
        xref_chart_filter['book'] = None
        xref_chart_filter['chapter'] = None
        apply_xref_chart_filter()

    def handle_xref_chart_click(e):
        idx = getattr(e, 'data_index', None)
        if idx is None or idx < 0 or idx >= len(xref_chart_meta['keys']):
            return
        clicked_key = xref_chart_meta['keys'][idx]
        if xref_chart_meta['mode'] == 'book':
            xref_chart_filter['book'] = clicked_key
            xref_chart_filter['chapter'] = None
            apply_xref_chart_filter()
        elif xref_chart_meta['mode'] == 'chapter':
            if xref_chart_filter['chapter'] == clicked_key:
                xref_chart_filter['book'] = None
                xref_chart_filter['chapter'] = None
            else:
                xref_chart_filter['book'] = xref_chart_meta['single_book']
                xref_chart_filter['chapter'] = clicked_key
            apply_xref_chart_filter()

    def update_xref_chart():
        if not xref_verses_cache:
            return
        b_filter = xref_chart_filter['book']
        c_filter = xref_chart_filter['chapter']
        active_verses = [
            vr for vr in xref_verses_cache
            if b_filter is None or (vr.get('b') == b_filter and (c_filter is None or vr.get('c') == c_filter))
        ]
        counts = Counter(vr['b'] for vr in active_verses if vr.get('b'))
        book_ids = sorted(counts.keys())
        lang = app.storage.user.get('ui_language', 'eng')
        abbrev_map = BibleBooks.abbrev.get(lang, BibleBooks.abbrev['eng'])
        if len(book_ids) == 1:
            sb = book_ids[0]
            ba = abbrev_map[str(sb)][0] if str(sb) in abbrev_map else str(sb)
            cc = Counter(vr['c'] for vr in active_verses if vr.get('b') == sb and vr.get('c'))
            chaps = sorted(cc.keys())
            labels = [f"{ba} {ch}" for ch in chaps]
            values = [cc[ch] for ch in chaps]
            xref_chart_meta['mode'] = 'chapter'
            xref_chart_meta['keys'] = chaps
            xref_chart_meta['single_book'] = sb
        else:
            labels = [abbrev_map[str(bk)][0] if str(bk) in abbrev_map else str(bk) for bk in book_ids]
            values = [counts[bk] for bk in book_ids]
            xref_chart_meta['mode'] = 'book'
            xref_chart_meta['keys'] = book_ids
            xref_chart_meta['single_book'] = None

        dark = app.storage.user.get('dark_mode', False)
        text_color = '#e5e7eb' if dark else '#1f2937'
        split_color = '#374151' if dark else '#e5e7eb'
        bg_color = '#1f2937' if dark else '#ffffff'

        xref_chart.style(f'height: {max(240, len(labels) * 28 + 90)}px;')
        xref_chart.options.clear()
        xref_chart.options.update({
            'backgroundColor': bg_color,
            'title': {
                'text': f"{last_entry} ({sum(values)})",
                'left': 'center',
                'top': 8,
                'textStyle': {'color': text_color, 'fontSize': 15},
            },
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'toolbox': {
                'right': 16,
                'top': 4,
                'feature': {
                    'saveAsImage': {
                        'show': True,
                        'title': get_translation('Download'),
                        'name': re.sub(r'[^\w\-]+', '_', last_entry).strip('_') or 'xref_distribution',
                        'pixelRatio': 3,
                        'backgroundColor': bg_color,
                    }
                },
            },
            'grid': {'left': 20, 'right': 50, 'top': 52, 'bottom': 24, 'containLabel': True},
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
            'series': [{
                'type': 'bar',
                'data': values,
                'barMaxWidth': 22,
                'itemStyle': {'color': '#10b981', 'borderRadius': [0, 4, 4, 0]},
                'label': {'show': True, 'position': 'right', 'color': text_color},
            }],
        })
        xref_chart.update()


    # ----------------------------------------------------------
    # Helper: Filter Logic
    # ----------------------------------------------------------
    def filter_verses(e=None):
        """
        Filters visibility based on input.
        Iterates over default_slot.children to find rows.
        """
        total_matches = 0
        # Robustly determine the search text
        text = ""
        if e is not None and hasattr(e, 'value'):
            text = e.value 
        else:
            text = input_field.value 
            
        search_term = text.lower() if text else ""
        
        # Iterate over the actual children of the container
        for row in verses_container.default_slot.children:
            # Skip elements that aren't our verse rows (if any)
            if not hasattr(row, 'verse_data'):
                continue

            # Explicitly show all if search is empty
            if not search_term:
                row.set_visibility(True)
                continue

            data = row.verse_data
            ref_text = data['ref'].lower()
            clean_content = re.sub('<[^<]+?>', '', data['content']).lower()

            is_match = (search_term in ref_text) or (search_term in clean_content)
            row.set_visibility(is_match)
            if is_match:
                total_matches += 1
        if total_matches:
            ui.notify(f"{total_matches} {'match' if total_matches == 1 else 'matches'} found!")

    # ----------------------------------------------------------
    # Helper: Remove Verse
    # ----------------------------------------------------------
    def remove_verse_row(row_element, reference):
        try:
            verses_container.remove(row_element)
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
        nonlocal SQL_QUERY, input_field, verses_container, last_entry
        query = input_field.value.strip()
        if not query:
            return
        last_entry = query
        parser = BibleVerseParser(False)
        refs = parser.extractAllReferences(query)
        if not refs:
            ui.notify('No verses found!', type='negative')
            return
        # update tab records
        if keep:
            gui.update_active_area2_tab_records(q=query)
        # Clear existing rows first
        verses_container.clear()
        xref_verses_cache.clear()
        xref_chart_filter['book'] = None
        xref_chart_filter['chapter'] = None
        reset_xref_filter_btn.set_visibility(False)
        xref_expansion.set_visibility(False)

        input_field.disable()

        try:

            for ref in refs:
                for ref2 in parser.extractExhaustiveReferences([ref]):
                    b, c, v = ref2
                    query = ""
                    n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
                    query = await run.io_bound(fetch_xrefs, b, c, v)
                    n.dismiss()
                    if query:
                        query = query[0]
                    else:
                        #ui.notify('No verses found!', type='negative')
                        continue
                    
                    # Prepend the original verse reference to the query for context
                    query = parser.bcvToVerseReference(b, c, v) + "; " + query
                    
                    if not query:
                        #ui.notify('Display cleared', type='positive', position='top')
                        continue

                    parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
                    verses = get_bible_content(query, bible=gui.get_area_1_bible_text(), sql_query=SQL_QUERY, parser=parser)

                    if not verses:
                        #ui.notify('No verses found!', type='negative')
                        continue

                    xref_verses_cache.extend(verses[1:])
                    if xref_verses_cache:
                        xref_expansion.set_visibility(True)
                        if xref_expansion.value:
                            update_xref_chart()

                    with verses_container:
                        
                        ui.label("Cross-References - " + verses[0]['ref']).classes('text-2xl font-serif text-secondary')
                        
                        for v in verses:
                            # Row setup
                            with ui.column().classes('w-full shadow-sm rounded-lg items-start no-wrap border border-gray-200 !gap-0') as row:
                                
                                row.verse_data = v # Store data for filter function

                                # --- Chip (Clickable & Removable) ---
                                with ui.element('div').classes('flex-none pt-1'): 
                                    with ui.chip(
                                        v['ref'], 
                                        removable=True, 
                                        icon='book',
                                        #on_click=partial(ui.notify, f'Clicked {v['ref']}'),
                                    ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm') as chip:
                                        with ui.menu():
                                            ui.menu_item('Open in Bible Area', on_click=partial(gui.change_area_1_bible_chapter, v['bible'], v['b'], v['c'], v['v']))
                                            ui.menu_item('Open Here', on_click=partial(gui.change_area_2_bible_chapter, v['bible'], v['b'], v['c'], v['v'], sync=False))
                                            ui.menu_item('Open in Next Tab', on_click=partial(open_chapter_next_area2_tab, v['bible'], v['b'], v['c'], v['v']))
                                            ui.menu_item('Open in New Tab', on_click=partial(open_chapter_empty_area2_tab, v['bible'], v['b'], v['c'], v['v']))
                                    chip.on('remove', lambda _, r=row, ref=v['ref']: remove_verse_row(r, ref))

                                # --- Content ---
                                ui.html(v['content'], sanitize=False).classes('grow min-w-0 leading-relaxed pl-2 text-base break-words')

                    # Clear input so user can start typing to filter immediately
                    input_field.value = ""
                    input_field.props(f'''placeholder="{get_translation('Type to filter')} {len(verses)} {get_translation('results')}..."''')
                    ui.notify(f"{len(verses)} {get_translation('result') if not verses or len(verses) == 1 else get_translation('results')}")

        except Exception as e:
            # Handle errors (e.g., network failure)
            ui.notify(f'Error: {e}', type='negative')

        finally:
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
            placeholder=get_translation("Enter bible verse reference(s) here...")
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        input_field.on('update:model-value', filter_verses)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        with ui.expansion(
            get_translation('Distribution Analysis'),
            icon='bar_chart',
            value=False,
            on_value_change=lambda e: update_xref_chart() if e.value else None,
        ).classes('w-full rounded-lg border border-gray-200') as xref_expansion:
            with ui.row().classes('w-full justify-end'):
                reset_xref_filter_btn = ui.button(
                    get_translation('Reset Filter'),
                    icon='filter_alt_off',
                    on_click=reset_xref_chart_filter,
                ).props('flat dense size=sm')
                reset_xref_filter_btn.set_visibility(False)
            xref_chart = ui.echart({}, on_point_click=handle_xref_chart_click).classes('w-full cursor-pointer')
        xref_expansion.set_visibility(False)

        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
    else:
        parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        input_field.value = parser.bcvToVerseReference(b,c,v)
    ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    input_field.run_method('focus')
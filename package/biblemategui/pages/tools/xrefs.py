from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from biblemategui import BIBLEMATEGUI_DATA
from biblemategui.fx.bible import get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from functools import partial
from nicegui import ui, app, run
import re, apsw, os

def fetch_xrefs(b, c, v):
    db = os.path.join(BIBLEMATEGUI_DATA, "cross-reference.sqlite")
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
        nonlocal SQL_QUERY
        query = input_field.value.strip()
        if not query:
            return
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

        input_field.disable()

        try:

            for ref in refs:
                for ref2 in parser.extractExhaustiveReferences([ref]):
                    b, c, v = ref2
                    query = ""
                    n = ui.notification('Loading ...', timeout=None, spinner=True)
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

                    verses = get_bible_content(query, bible=gui.get_area_1_bible_text(), sql_query=SQL_QUERY)

                    if not verses:
                        #ui.notify('No verses found!', type='negative')
                        continue

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
                    input_field.props(f'placeholder="Type to filter {len(verses)} results..."')
                    ui.notify(f"{len(verses)} {'result' if not verses or len(verses) == 1 else 'results'} found!")

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
            placeholder='Enter bible verse reference(s) here ...'
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
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
    else:
        parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        input_field.value = parser.bcvToVerseReference(b,c,v)
    ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    input_field.run_method('focus')
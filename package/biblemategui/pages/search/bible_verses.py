from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemategui.fx.bible import get_bible_content
from biblemategui import BIBLEMATEGUI_DATA, config, get_translation, resolve_verses_additional_options
from functools import partial
from nicegui import ui, app, run
import re, apsw, os


def search_bible_verses(gui=None, q='', **_):

    last_entry = q
    default_placeholder = get_translation("Search for words or refs")
    multiple_bibles = None

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
            
        search_term = text if text else ""
        if not app.storage.user['search_case_sensitivity']:
            search_term = search_term.lower()
        
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
            ref_text = data['ref']
            if not app.storage.user['search_case_sensitivity']:
                ref_text = ref_text.lower()
            clean_content = re.sub('<[^<]+?>', '', data['content'])
            if not app.storage.user['search_case_sensitivity']:
                clean_content = clean_content.lower()

            if not app.storage.user['search_mode'] == 2:
                is_match = (re.search(search_term, ref_text)) or (re.search(search_term, clean_content))
            else:
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
        nonlocal SQL_QUERY, last_entry
        query = input_field.value.strip()
    
        # Clear existing rows first
        verses_container.clear()

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
            if search_morphology := re.search(r"^([EG][0-9]+?)\|", query): # search morphology
                multiple_bibles.value = [app.storage.user["tool_book_text"]]
                lexical_entry = search_morphology.group(1) + ",%"
                suffix = ""
                for i in query.split("|")[1:]:
                    suffix += f"AND Morphology LIKE '{i}' "
                if books := re.search("WHERE (Book.*?) AND", SQL_QUERY):
                    suffix += f"AND {books.group(1)} " # limit morphology search in particular books
                db = os.path.join(BIBLEMATEGUI_DATA, "morphology.sqlite")
                with apsw.Connection(db) as connn:
                    query = f"SELECT Book, Chapter, Verse FROM morphology WHERE LexicalEntry LIKE ? {suffix}ORDER BY Book, Chapter, Verse"
                    cursor = connn.cursor()
                    cursor.execute(query, (lexical_entry,))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify('No verses found.', type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser)
            elif re.search("^BP[0-9]+?$", query): # bible characters entries
                db_file = os.path.join(BIBLEMATEGUI_DATA, "data", "biblePeople.data")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute("SELECT Book, Chapter, Verse FROM PEOPLE WHERE PersonID=? ORDER BY Book, Chapter, Verse", (int(query[2:]),))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify('No verses found.', type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser)
            elif re.search("^BL[0-9]+?$", query): # bible locatios entries
                db_file = os.path.join(BIBLEMATEGUI_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute('''SELECT Book, Chapter, Verse FROM exlbl WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify('No verses found.', type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser)
            elif re.search(f"^({"|".join(list(config.topics.keys()))})[0-9]+?$", query): # bible topics entries
                db_file = os.path.join(BIBLEMATEGUI_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute('''SELECT Book, Chapter, Verse FROM exlbt WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify('No verses found.', type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser)
            elif re.search(f"^({"|".join(list(config.dictionaries.keys()))})[0-9]+?$", query): # bible dictionaries entries
                db_file = os.path.join(BIBLEMATEGUI_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute('''SELECT Book, Chapter, Verse FROM dictionaries WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify('No verses found.', type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser)
            elif re.search(f"^(ISBE|{"|".join(list(config.encyclopedias.keys()))})[0-9]+?$", query): # bible encyclopedia entries
                db_file = os.path.join(BIBLEMATEGUI_DATA, "indexes2.sqlite")
                with apsw.Connection(db_file) as connn:
                    cursor = connn.cursor()
                    cursor.execute('''SELECT Book, Chapter, Verse FROM encyclopedia WHERE Information LIKE ? ORDER BY Book, Chapter, Verse''', (f"%'{query}'%",))
                    fetch = cursor.fetchall()
                if not fetch:
                    ui.notify('No verses found.', type='negative')
                    return
                verses = await run.io_bound(get_bible_content, bible=get_bibles(), sql_query=SQL_QUERY, refs=fetch, parser=parser)
            else: # regular search
                verses = await run.io_bound(get_bible_content, user_input=query, bible=get_bibles(), sql_query=SQL_QUERY, search_mode=app.storage.user['search_mode'], top_similar_verses=app.storage.user['top_similar_verses'], search_case_sensitivity=app.storage.user['search_case_sensitivity'], parser=parser)
                highlights = True

            if not verses:
                ui.notify('No verses found.', type='negative')
                return

            if not verses[-1]['ref']:
                ui.notify(verses[-1]['content'])
                verses = verses[:-1]
            with verses_container:
                for v in verses:
                    # Row setup
                    with ui.column().classes('w-full shadow-sm rounded-lg items-start no-wrap border border-gray-200 !gap-0') as row:
                        
                        row.verse_data = v # Store data for filter function

                        def get_verse_content(ref, content):
                            content = re.sub("<[^<>]+?>", "", content)
                            return f"[{ref}] {content}"
                        
                        def ask_biblemate(ref, content):
                            nonlocal gui
                            gui.ask_biblemate(f"# {ref}\n\n{re.sub("<[^<>]+?>", "", content)}\n\n# Query\n\n")

                        # --- Chip (Clickable & Removable) ---
                        with ui.element('div').classes('flex-none pt-1'): 
                            with ui.chip(
                                v['ref'], 
                                removable=True, 
                                icon='book',
                                #on_click=partial(ui.notify, f'Clicked {v['ref']}'),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm') as chip:
                                with ui.menu():
                                    ui.menu_item('📋 Copy', on_click=partial(gui.copy_text, get_verse_content(v['ref'], v['content'])))
                                    ui.separator()
                                    ui.menu_item('📜 Open in Bible Area', on_click=partial(gui.change_area_1_bible_chapter, v['bible'], v['b'], v['c'], v['v']))
                                    ui.menu_item('📜 Open Here', on_click=partial(gui.change_area_2_bible_chapter, v['bible'], v['b'], v['c'], v['v'], sync=False))
                                    ui.menu_item('📜 Open in Next Tab', on_click=partial(open_chapter_next_area2_tab, v['bible'], v['b'], v['c'], v['v']))
                                    ui.menu_item('📜 Open in New Tab', on_click=partial(open_chapter_empty_area2_tab, v['bible'], v['b'], v['c'], v['v']))
                                    ui.separator()
                                    ui.menu_item('💬 Ask BibleMate', on_click=partial(ask_biblemate, v['ref'], v['content']))
                            chip.on('remove', lambda _, r=row, ref=v['ref']: remove_verse_row(r, ref))

                        # --- Content ---
                        content = v['content']
                        # add tooltip
                        if "</heb>" in content:
                            content = re.sub('(<heb id=")(.*?)"', r'\1\2" data-word="\2" class="tooltip-word"', content)
                            content = content.replace("<heb> </heb>", "<heb>&nbsp;</heb>")
                            content = f"<div style='display: inline-block; direction: rtl;'>{content}</div>"
                        elif "</grk>" in content:
                            content = re.sub('(<grk id=")(.*?)"', r'\1\2" data-word="\2" class="tooltip-word"', content)
                        if highlights:
                            if app.storage.user["dark_mode"]:
                                content = re.sub(f"({query})", r"<font color='orange'>\1</font>", content, flags=0 if app.storage.user['search_case_sensitivity'] else re.IGNORECASE)
                            else:
                                content = re.sub(f"({query})", r"<span style='background-color: orange;'>\1</span>", content, flags=0 if app.storage.user['search_case_sensitivity'] else re.IGNORECASE)
                        ui.html(content, sanitize=False).classes('grow min-w-0 leading-relaxed pl-2 text-base break-words')

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
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        #handle_enter(None, keep=False) # RuntimeWarning: coroutine 'search_bible_verses.<locals>.handle_enter' was never awaited
        ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    else:
        input_field.run_method('focus')
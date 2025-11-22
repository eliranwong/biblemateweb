from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from biblemategui.fx.bible import get_bible_content
from functools import partial
from nicegui import ui, app
import re


def search_bible_verses(gui=None, q='', **_):

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
    initial_selection = ['All', 'OT', 'NT'] + BIBLE_BOOKS
    if q and ":::" in q:
        books, q = q.split(":::", 1)
        valid_books = [i.strip() for i in books.split(",") if i.strip() in initial_selection+["None"]]
        if "None" in valid_books:
            valid_books = ["None"]
        elif "All" in valid_books or ("OT" in valid_books and "NT" in valid_books):
            valid_books = initial_selection
        else:
            if "OT" in valid_books:
                valid_books += OT_BOOKS
                valid_books = list(set(valid_books))
            if "NT" in valid_books:
                valid_books += NT_BOOKS
                valid_books = list(set(valid_books))
        if valid_books:
            initial_selection = valid_books
    
    state = {'previous': initial_selection}

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
        ui.notify(f"{total_matches} {'match' if not total_matches or total_matches == 1 else 'matches'} found!")

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
    def handle_enter(e):
        nonlocal SQL_QUERY
        query = input_field.value.strip()
        
        # Clear existing rows first
        verses_container.clear()
        
        if not query:
            ui.notify('Display cleared', type='positive', position='top')
            return

        active_bible_tab = gui.get_active_area1_tab()
        verses = get_bible_content(query, bible=app.storage.user[active_bible_tab]["bt"] if active_bible_tab in app.storage.user else "NET", sql_query=SQL_QUERY)

        if not verses:
            ui.notify('No verses found.', type='negative')
            return

        with verses_container:
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
                        ).classes('cursor-pointer font-bold shadow-sm') as chip:
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

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            value=q,
            autocomplete=BIBLE_BOOKS,
            placeholder='Enter search item or refs (e.g. Deut 6:4; John 3:16-18)'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus')

        input_field.on('keydown.enter', handle_enter)
        input_field.on('update:model-value', filter_verses)

        # 2. Scope Dropdown
        # Options: All, None, OT, NT, then the books
        options = ['All', 'None', 'OT', 'NT'] + BIBLE_BOOKS
        
        scope_select = ui.select(
            options=options,
            label='Search',
            multiple=True,
            with_input=True
        ).classes('w-22')

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

        # --- Bindings ---
        scope_select.on_value_change(handle_scope_change)

        # Initialize
        scope_select.value = initial_selection

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        handle_enter(None)
from biblemategui import BIBLEMATEGUI_DATA, config
from biblemategui.fx.bible import get_bible_content
from functools import partial
from nicegui import ui, app
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
import numpy as np
import re, apsw, os, json


def search_bible_parallels(gui=None, q='', **_):

    # all entries
    all_entries = []
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "collection.db")
    with apsw.Connection(db_file) as connn:
        cursor = connn.cursor()
        sql_query = "SELECT entry FROM PARALLEL"
        cursor.execute(sql_query)
        all_entries = [i[0] for i in cursor.fetchall()]
    all_entries = list(set([i for i in all_entries if i]))

    SQL_QUERY = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"

    # --- Fuzzy Match Dialog ---
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label("Bible Parallels...").classes('text-xl font-bold text-primary mb-4')
        ui.label("We couldn't find an exact match. Please select one of these topics:").classes('text-secondary mb-4')
        
        # This container will hold the radio selection dynamically
        selection_container = ui.column().classes('w-full')
        
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat color=grey')

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

    def show_verses(path, keep=True):
        nonlocal SQL_QUERY, verses_container, gui, dialog, input_field, topic_label

        # update tab records
        if keep:
            gui.update_active_area2_tab_records(q=path)

        db = os.path.join(BIBLEMATEGUI_DATA, "collections3.sqlite")
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            if re.search(r"^[0-9]+?\.[0-9]+?$", path):
                sql_query = "SELECT Topic, Passages FROM PARALLEL WHERE Tool=? AND Number=? limit 1"
                tool, number = path.split(".")
                cursor.execute(sql_query, (int(tool), int(number)))
                if query := cursor.fetchone():
                    topic, query = query
            else:
                topic = path
                sql_query = "SELECT Passages FROM PARALLEL WHERE Topic=?"
                cursor.execute(sql_query, (path,))
                query = "; ".join([i[0] for i in cursor.fetchall()])
                if not query:
                    sql_query = "SELECT Passages FROM PARALLEL WHERE Topic LIKE ?"
                    cursor.execute(sql_query, (f"%{path}%",))
                    query = "; ".join([i[0] for i in cursor.fetchall()])
        # 2. Update the existing label's text
        topic_label.text = topic
        topic_label.classes(remove='hidden')
        if not query:
            ui.notify('No verses found!', type='negative')
            return

        # Clear existing rows first
        verses_container.clear()
        
        if not query:
            ui.notify('Display cleared', type='positive', position='top')
            return

        verses = get_bible_content(query, bible=gui.get_area_1_bible_text(), sql_query=SQL_QUERY)

        if not verses:
            ui.notify('No verses found!', type='negative')
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

    def handle_enter(e, keep=True):
        query = input_field.value.strip()

        if re.search(r"^[0-9]+?\.[0-9]+?$", query):
            show_verses(path, keep=keep)
            return
        
        db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "collection.db")
        sql_table = "PARALLEL"
        embedding_model="paraphrase-multilingual"
        options = []
        try:
            with apsw.Connection(db_file) as connection:
                # search for exact match first
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM {sql_table} WHERE entry = ?;", (query,))
                rows = cursor.fetchall()
                if not rows: # perform similarity search if no an exact match
                    # convert query to vector
                    query_vector = get_embeddings([query], embedding_model)[0]
                    # fetch all entries
                    cursor.execute(f"SELECT entry, entry_vector FROM {sql_table}")
                    all_rows = cursor.fetchall()
                    if not all_rows:
                        return []
                    # build a matrix
                    entries, entry_vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in all_rows if row[0] and row[1]])
                    document_matrix = np.vstack(entry_vectors)
                    # perform a similarity search
                    similarities = cosine_similarity_matrix(query_vector, document_matrix)
                    top_indices = np.argsort(similarities)[::-1][:app.storage.user["top_similar_entries"]]
                    # return top matches
                    options = [entries[i] for i in top_indices]
                elif len(rows) == 1: # single exact match
                    path = rows[0][0]
                    show_verses(path, keep=keep)
                else:
                    options = [row[0] for row in rows]
        except Exception as ex:
            print("Error during database operation:", ex)
            ui.notify('Error during database operation!', type='negative')
            return

        if options:
            options = list(set(options))
            def handle_selection(selected_option):
                nonlocal dialog
                if selected_option:
                    dialog.close()
                    if "+" in selected_option:
                        path, _ = selected_option.split("+", 1)
                    else:
                        path = selected_option
                    show_verses(path, keep=keep)

            selection_container.clear()
            with selection_container:
                # We use a radio button for selection
                radio = ui.radio(options).classes('w-full').props('color=primary')
                ui.button('Show Verses', on_click=lambda: handle_selection(radio.value)) \
                    .classes('w-full mt-4 bg-blue-500 text-white shadow-md')    
            dialog.open()

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=all_entries,
            placeholder='Search for parallel passages ...'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        input_field.on('update:model-value', filter_verses)

    topic_label = ui.label().classes('text-2xl font-serif hidden')

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        handle_enter(None, keep=False)
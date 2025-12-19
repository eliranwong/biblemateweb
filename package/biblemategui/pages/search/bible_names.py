from biblemategui import BIBLEMATEGUI_DATA, loading
from biblemategui.data.bible_names import bible_names
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
import numpy as np
from functools import partial
from nicegui import ui, app, run
import re, apsw, os, json, traceback, asyncio

def load_names_vectors_from_db(db_file, sql_table):
    entries = []
    entry_vectors = []
    
    with apsw.Connection(db_file) as connection:
        cursor = connection.cursor()
        # Note: This table uses 'path' as the main label, not 'entry'
        cursor.execute(f"SELECT path, entry_vector FROM {sql_table}")
        
        # Heavy CPU work: Parsing JSON
        for path, vector_json in cursor.fetchall():
            if path and vector_json:
                entries.append(path)
                entry_vectors.append(np.array(json.loads(vector_json)))

    if not entries:
        return [], None

    # Heavy CPU work: Stacking arrays
    document_matrix = np.vstack(entry_vectors)
    return entries, document_matrix

async def fetch_bible_names_matches_async(search_term, spin=True):
    if spin:
        n = ui.notification("Loading ...", timeout=None, spinner=True)
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
    sql_table = "exlbn"
    embedding_model = "paraphrase-multilingual"
    options = []
    
    try:
        # 1. Exact Match Check (Fast, run on main thread)
        exact_match_found = False
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT path FROM {sql_table} WHERE path = ?;", (search_term,))
            rows = cursor.fetchall()
            
            if len(rows) == 1:
                options = [rows[0][0]]
                exact_match_found = True
            elif len(rows) > 1:
                options = [row[0] for row in rows]
                exact_match_found = True

        # 2. Similarity Search (Offloaded to CPU bound thread)
        if not exact_match_found:
            # A. Get Query Vector (IO Bound)
            query_vector = await run.io_bound(get_embeddings, [search_term], embedding_model)
            query_vector = query_vector[0]

            # B. Load Vectors (The Fix: Run in separate process)
            # using the new helper function for names
            entries, document_matrix = await run.cpu_bound(load_names_vectors_from_db, db_file, sql_table)

            if not entries:
                return []

            # C. Compute Similarity
            similarities = await run.cpu_bound(cosine_similarity_matrix, query_vector, document_matrix)
            
            # D. Sort & Select Top Matches
            top_indices = np.argsort(similarities)[::-1][:app.storage.user["top_similar_entries"]]
            options = [entries[i] for i in top_indices]

    except Exception as ex:
        print("Error during database operation:", ex)
        traceback.print_exc()
        if spin:
            n.message = f'Error: {str(ex)}'
            n.type = 'negative'
        return []
    finally:
        if spin:
            n.dismiss()
        
    return options

def fetch_bible_names_matches(search_term):
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
    sql_table = "exlbn"
    embedding_model="paraphrase-multilingual"
    options = []
    try:
        with apsw.Connection(db_file) as connection:
            # search for exact match first
            cursor = connection.cursor()
            cursor.execute(f"SELECT path FROM {sql_table} WHERE path = ?;", (search_term,))
            rows = cursor.fetchall()
            if not rows: # perform similarity search if no an exact match
                # convert query to vector
                query_vector = get_embeddings([search_term], embedding_model)[0]
                # fetch all entries
                cursor.execute(f"SELECT path, entry_vector FROM {sql_table}")
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
                options = [rows[0][0]]
            else:
                options = [row[0] for row in rows]
    except Exception as ex:
        print("Error during database operation:", ex)
        traceback.print_exc()
        ui.notify('Error during database operation!', type='negative')
        return
    return options

def search_bible_names(gui=None, q='', **_):

    last_entry = q

    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    def show_all_names(e=None):
        """
        Filters visibility based on input.
        Iterates over default_slot.children to find rows.
        """
        # Robustly determine the search text
        text = input_field.value
        if len(text) == 1:
            for row in names_container.default_slot.children:
                if not hasattr(row, 'name_data'):
                    continue
                row.set_visibility(True)

    async def filter_names(e=None, keep=True, spin=True):
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

        input_field.disable()

        try:

            search_term = text
            # update tab records
            if keep:
                gui.update_active_area2_tab_records(q=search_term)

            # similarity search
            if search_term:
                options = await fetch_bible_names_matches_async(search_term, spin)

        except Exception as e:
            # Handle errors (e.g., network failure)
            ui.notify(f'Error: {e}', type='negative')

        finally:
            # ALWAYS re-enable the input, even if an error occurred above
            input_field.enable()
            # Optional: Refocus the cursor so the user can type the next query immediately
            input_field.run_method('focus')

        # Iterate over the actual children of the container
        for row in names_container.default_slot.children:
            # Skip elements that aren't our names rows (if any)
            if not hasattr(row, 'name_data'):
                continue

            # Explicitly show all if search is empty
            if not search_term:
                row.set_visibility(True)
                continue

            data = row.name_data

            is_match = (data in options)
            row.set_visibility(is_match)
            if is_match:
                total_matches += 1
        if total_matches:
            ui.notify(f"{total_matches} matches found!")

    # ----------------------------------------------------------
    # Helper: Remove Verse
    # ----------------------------------------------------------
    def remove_name_row(row_element, reference):
        try:
            names_container.remove(row_element)
            ui.notify(f'Removed: {reference}', type='warning', position='top')
        except Exception as e:
            print(f"Error removing row: {e}")

    # ----------------------------------------------------------
    # Helper: Open Chapter
    # ----------------------------------------------------------
    def search_tool(tool, query):
        nonlocal gui
        """Logic when 'Character' button is clicked"""
        app.storage.user["tool_query"] = query
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title=tool)

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------
    async def show_names():
        nonlocal q, input_field, names_container, last_entry

        n = ui.notification("Loading ...", timeout=None, spinner=True)

        with names_container:
            check = 0
            for name, meaning in bible_names.items():
                # Row setup
                with ui.row().classes('w-full shadow-sm rounded-lg items-center no-wrap border border-gray-200 !gap-0') as row:
                    
                    row.name_data = name # Store data for filter function

                    # --- Chip (Clickable & Removable) ---
                    with ui.element('div').classes('flex-none pt-1'): 
                        with ui.chip(
                            name, 
                            removable=True, 
                            icon='book',
                            #on_click=partial(ui.notify, f'Clicked {v['ref']}'),
                        ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm') as chip:
                            with ui.menu():
                                ui.menu_item('Search Characters', on_click=partial(search_tool, "Characters", name))
                                ui.menu_item('Search Locations', on_click=partial(search_tool, "Locations", name))
                                ui.menu_item('Search Dictionaries', on_click=partial(search_tool, "Dictionaries", name))
                                ui.menu_item('Search Encyclopedias', on_click=partial(search_tool, "Encyclopedias", name))
                        chip.on('remove', lambda _, r=row, name=name: remove_name_row(r, name))

                    # --- Content ---
                    meaning = re.sub("^<b>.*?</b> - ", "", meaning)
                    ui.html(meaning, sanitize=False).classes('grow min-w-0 leading-relaxed pl-2 text-base break-words')
            
                check += 1
                if check % 50 == 0:
                    n.message = f"{check} / {len(bible_names)}"
                    # Yield to the event loop so the spinner can spin and DOM can update
                    await asyncio.sleep(0)
        
        n.dismiss()

        if q:
            input_field.value = q
            await filter_names(None, keep=False, spin=False)
            q = ""

        # Clear input so user can start typing to filter immediately
        input_field.value = ""
        #input_field.props(f'placeholder="Type to filter {len(bible_names)} results..."')
        #ui.notify(f"{len(bible_names)} results found!")
        input_field.run_method('focus')

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=list(bible_names.keys()),
            placeholder='Search for a name or meaning'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', filter_names)
        input_field.on('update:model-value', show_all_names)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        names_container = ui.column().classes('w-full transition-all !gap-1')

    
    ui.timer(0.1, show_names, once=True)
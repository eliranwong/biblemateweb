from biblemategui import BIBLEMATEGUI_DATA, load_topic_vectors_from_db, get_translation
from biblemategui.fx.bible import get_bible_content
from functools import partial
from nicegui import ui, app, run
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
import numpy as np
import re, apsw, os, json, traceback


def fetch_promises_topic(path):
    db = os.path.join(BIBLEMATEGUI_DATA, "collections3.sqlite")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        if re.search(r"^[0-9]+?\.[0-9]+?$", path):
            sql_query = "SELECT Topic, Passages FROM PROMISES WHERE Tool=? AND Number=? limit 1"
            tool, number = path.split(".")
            cursor.execute(sql_query, (int(tool), int(number)))
            if query := cursor.fetchone():
                topic, query = query
        else:
            topic = path
            sql_query = "SELECT Passages FROM PROMISES WHERE Topic=?"
            cursor.execute(sql_query, (path,))
            query = "; ".join([i[0] for i in cursor.fetchall()])
            if not query:
                sql_query = "SELECT Passages FROM PROMISES WHERE Topic LIKE ?"
                cursor.execute(sql_query, (f"%{path}%",))
                query = "; ".join([i[0] for i in cursor.fetchall()])
    return topic, query

async def fetch_topic_matches_async(query):
    n = ui.notification("Loading ...", timeout=None, spinner=True)
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "collection.db")
    sql_table = "PROMISES"
    embedding_model = "paraphrase-multilingual"
    path = ""
    options = []
    
    try:
        # 1. Exact Match Check (Fast, safe on main thread)
        exact_match_found = False
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {sql_table} WHERE entry = ?;", (query,))
            rows = cursor.fetchall()
            
            if len(rows) == 1:
                path = rows[0][0]
                exact_match_found = True
            elif len(rows) > 1:
                options = [row[0] for row in rows]
                exact_match_found = True

        # 2. Similarity Search (Offloaded to CPU bound thread)
        if not exact_match_found:
            # A. Get Query Vector
            query_vector = await run.io_bound(get_embeddings, [query], embedding_model)
            query_vector = query_vector[0]

            # B. Load Vectors (The Fix: Run in separate process)
            # We reuse the helper that handles 'entry' and 'entry_vector' columns
            entries, document_matrix = await run.cpu_bound(load_topic_vectors_from_db, db_file, sql_table)

            if not entries:
                return path, []

            # C. Compute Similarity
            similarities = await run.cpu_bound(cosine_similarity_matrix, query_vector, document_matrix)
            
            # D. Sort & Select Top Matches
            top_indices = np.argsort(similarities)[::-1][:app.storage.user["top_similar_entries"]]
            options = [entries[i] for i in top_indices]

    except Exception as ex:
        print("Error during database operation:", ex)
        traceback.print_exc()
        n.message = f'Error: {str(ex)}'
        n.type = 'negative'
        return
    finally:
        n.dismiss()
        
    return path, options

def fetch_topic_matches(query):
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "collection.db")
    sql_table = "PROMISES"
    embedding_model="paraphrase-multilingual"
    path=""
    options=[]
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
            else:
                options = [row[0] for row in rows]
    except Exception as ex:
        print("Error during database operation:", ex)
        ui.notify('Error during database operation!', type='negative')
        return
    return path, options

def fetch_all_promises_topics():
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "collection.db")
    with apsw.Connection(db_file) as connn:
        cursor = connn.cursor()
        sql_query = "SELECT entry FROM PROMISES"
        cursor.execute(sql_query)
        all_entries = [i[0] for i in cursor.fetchall()]
    all_entries = list(set([i for i in all_entries if i]))
    return all_entries


def search_bible_promises(gui=None, q='', **_):

    last_entry = q
    SQL_QUERY = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"

    # --- Fuzzy Match Dialog ---
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label("Bible Promises ...").classes('text-xl font-bold text-secondary mb-4')
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

    async def show_verses(path, keep=True):
        nonlocal SQL_QUERY, verses_container, gui, dialog, input_field, topic_label, last_entry

        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        topic, query = await run.io_bound(fetch_promises_topic, path)
        n.dismiss()

        # update tab records
        if query and keep:
            gui.update_active_area2_tab_records(q=path)

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

        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        verses = await run.io_bound(get_bible_content, query, bible=gui.get_area_1_bible_text(), sql_query=SQL_QUERY, parser=parser)
        n.dismiss()

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
        last_entry = path
        input_field.value = ""
        input_field.props(f'''placeholder="{get_translation('Type to filter')} {len(verses)} {get_translation('results')}..."''')
        ui.notify(f"{len(verses)} {get_translation('result') if not verses or len(verses) == 1 else get_translation('results')}")

    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    async def handle_enter(e, keep=True):
        nonlocal input_field, dialog, selection_container, last_entry

        query = input_field.value.strip()
        if not query:
            return
        elif re.search(r"^[0-9]+?\.[0-9]+?$", query):
            await show_verses(query, keep=keep)
            return

        last_entry = query
        input_field.disable()

        try:
            path, options = await fetch_topic_matches_async(query)
        except Exception as e:
            # Handle errors (e.g., network failure)
            ui.notify(f'Error: {e}', type='negative')

        finally:
            # ALWAYS re-enable the input, even if an error occurred above
            input_field.enable()
            # Optional: Refocus the cursor so the user can type the next query immediately
            input_field.run_method('focus')

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
                    ui.timer(0, lambda: show_verses(path, keep=keep), once=True)

            selection_container.clear()
            with selection_container:
                # We use a radio button for selection
                radio = ui.radio(options).classes('w-full').props('color=primary')
                ui.button(get_translation('Show Verses'), on_click=lambda: handle_selection(radio.value)) \
                    .classes('w-full mt-4 bg-blue-500 text-white shadow-md')    
            dialog.open()
        else:
            await show_verses(path, keep=keep)

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=[],
            placeholder=f'{get_translation("Search for bible promises")}...'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        input_field.on('update:model-value', filter_verses)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

        async def get_all_promises_topics():
            all_topics = await run.io_bound(fetch_all_promises_topics)
            input_field.set_autocomplete(all_topics)
        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        ui.timer(0, get_all_promises_topics, once=True)
        n.dismiss()

    topic_label = ui.label().classes('text-2xl font-serif hidden')

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    else:
        input_field.run_method('focus')
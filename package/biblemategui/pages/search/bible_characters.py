from biblemategui import BIBLEMATEGUI_DATA, config
from functools import partial
from nicegui import ui, app
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
import numpy as np
import re, apsw, os, json, traceback
from biblemategui.data.cr_books import cr_books

def search_bible_characters(gui=None, q='', **_):

    def cr(event):
        nonlocal gui
        b, c, v, *_ = event.args
        b = cr_books.get(b, b)
        gui.change_area_1_bible_chapter(None, b, c, v)

    def bcv(event):
        nonlocal gui
        b, c, v, *_ = event.args
        gui.change_area_1_bible_chapter(None, b, c, v)

    ui.on('bcv', bcv)
    ui.on('cr', cr)

    # all characters
    all_characters = []
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
    with apsw.Connection(db_file) as connn:
        cursor = connn.cursor()
        sql_query = "SELECT entry FROM exlbp"
        cursor.execute(sql_query)
        all_characters = [i[0] for i in cursor.fetchall()]
    all_characters = list(set([i for i in all_characters if i]))

    # --- Fuzzy Match Dialog ---
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label("Bible Characters ...").classes('text-xl font-bold text-primary mb-4')
        ui.label("We couldn't find an exact match. Please select one of these topics:").classes('text-secondary mb-4')
        
        # This container will hold the radio selection dynamically
        selection_container = ui.column().classes('w-full')
        
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat color=grey')

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------

    def show_entry(path, keep=True):
        nonlocal content_container, gui, dialog, input_field

        db = os.path.join(BIBLEMATEGUI_DATA, "data", "exlb3.data")
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            topic = path
            sql_query = "SELECT content FROM exlbp WHERE path=? limit 1"
            cursor.execute(sql_query, (path,))
            fetch = cursor.fetchone()
            content = fetch[0] if fetch else ""

        # Clear existing rows first
        content_container.clear()

        with content_container:
            # html style
            ui.add_head_html(f"""
            <style>
                /* Main container for the content - LTR flow */
                .content-text {{
                    direction: ltr;
                    font-family: sans-serif;
                    padding: 0px;
                    margin: 0px;
                }}
                /* Verse ref */
                ref {{
                    color: {'#f2c522' if app.storage.user['dark_mode'] else 'navy'};
                    font-weight: bold;
                    cursor: pointer;
                }}
                /* CSS to target all h1 elements */
                h1 {{
                    font-size: 2.2rem;
                    color: {app.storage.user['primary_color']};
                }}
                /* CSS to target all h2 elements */
                h2 {{
                    font-size: 1.8rem;
                    color: {app.storage.user['secondary_color']};
                }}
            </style>
            """)
            # convert links, e.g. <ref onclick="bcv(3,19,26)">
            content = re.sub(r'''(onclick|ondblclick)="(cr|bcv)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
            content = re.sub(r"""(onclick|ondblclick)='(cr|bcv)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
            # convert colors for dark mode, e.g. <font color="brown">
            if app.storage.user['dark_mode']:
                content = content.replace('color="brown">', 'color="pink">')
                content = content.replace('color="navy">', 'color="lightskyblue">')
                content = content.replace('<table bgcolor="#BFBFBF"', '<table bgcolor="#424242"')
                content = content.replace('<td bgcolor="#FFFFFF">', '<td bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#FFFFFF">', '<tr bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#DFDFDF">', '<tr bgcolor="#303030">')
            # display
            ui.html(f'<div class="bible-text">{content}</div>', sanitize=False)

            # Handler
            def search_action(entry):
                nonlocal gui
                """Logic when 'Character' button is clicked"""
                app.storage.user["tool_query"] = entry
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Relationships')

            with ui.row().classes('w-full justify-center q-my-md'):
                ui.button('Show All Verses', icon='auto_stories', on_click=lambda: gui.show_all_verses(path)) \
                    .props('size=lg rounded color=primary')
                ui.button('Relationships', icon='search', on_click=lambda: search_action(path)) \
                    .props('size=lg rounded color=primary')

        # Clear input so user can start typing to filter immediately
        input_field.value = ""
        # update tab records
        if keep:
            gui.update_active_area2_tab_records(q=path)

    def handle_enter(e, keep=True):
        query = input_field.value.strip()
        if re.search("BP[0-9]+?$", query):
            show_entry(query, keep=keep)
            return
        db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
        sql_table = "exlbp"
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
                    cursor.execute(f"SELECT path, entry, entry_vector FROM {sql_table}")
                    all_rows = [(f"[{path}] {entry}", entry_vector) for path, entry, entry_vector in cursor.fetchall()]
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
                    show_entry(path, keep=keep)
                else:
                    options = [f"[{row[0]}] {row[1]}" for row in rows]
        except Exception as ex:
            print("Error during database operation:", ex)
            traceback.print_exc()
            ui.notify('Error during database operation!', type='negative')
            return

        if options:
            options = list(set(options))
            def handle_selection(selected_option):
                nonlocal dialog
                if selected_option:
                    dialog.close()
                    path, _ = selected_option.split(" ", 1)
                    show_entry(path[1:-1], keep=keep)

            selection_container.clear()
            with selection_container:
                # We use a radio button for selection
                radio = ui.radio(options).classes('w-full').props('color=primary')
                ui.button('Show Content', on_click=lambda: handle_selection(radio.value)) \
                    .classes('w-full mt-4 bg-blue-500 text-white shadow-md')    
            dialog.open()

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=all_characters,
            placeholder='Search for a bible character ...'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        #input_field.on('update:model-value', filter_verses)

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        content_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        handle_enter(None, keep=False)
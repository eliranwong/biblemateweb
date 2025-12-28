from biblemategui import BIBLEMATEGUI_DATA, load_vectors_from_db, get_translation
from nicegui import ui, app, run
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
import numpy as np
import re, apsw, os, json, traceback, asyncio
from biblemategui.data.cr_books import cr_books

def fetch_bible_locations_entry(path):
    db = os.path.join(BIBLEMATEGUI_DATA, "data", "exlb3.data")
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        sql_query = "SELECT content FROM exlbl WHERE path=? limit 1"
        cursor.execute(sql_query, (path,))
        fetch = cursor.fetchone()
        content = fetch[0] if fetch else ""
    vdb = os.path.join(BIBLEMATEGUI_DATA, "data", "exlb3.data")
    location, lat, lng = None, None, None
    with apsw.Connection(vdb) as connn:
        cursor = connn.cursor()
        sql_query = "SELECT location, lat, lng FROM exlbli WHERE path=?"
        cursor.execute(sql_query, (path,))
        if fetch := cursor.fetchone():
            location, lat, lng = fetch
            lat, lng = float(lat), float(lng)
    return content, location, lat, lng

async def fetch_bible_locations_matches_async(query):
    n = ui.notification("Loading ...", timeout=None, spinner=True)
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
    sql_table = "exlbl"
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
                options = [f"[{row[0]}] {row[1]}" for row in rows]
                exact_match_found = True

        # 2. Similarity Search (Offloaded to prevent blocking)
        if not exact_match_found:
            # A. Get Query Vector
            query_vector = await run.io_bound(get_embeddings, [query], embedding_model)
            query_vector = query_vector[0]

            # B. Load & Parse Vectors (Run in separate process)
            entries, document_matrix = await run.cpu_bound(load_vectors_from_db, db_file, sql_table)

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
        n.message = f'Error: {str(ex)}'
        n.type = 'negative'
        return
    finally:
        n.dismiss()
        
    return path, options

def fetch_bible_locations_matches(query):
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
    sql_table = "exlbl"
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
            else:
                options = [f"[{row[0]}] {row[1]}" for row in rows]
    except Exception as ex:
        print("Error during database operation:", ex)
        traceback.print_exc()
        ui.notify('Error during database operation!', type='negative')
        return
    return path, options

def fetch_all_locations():
    vdb = os.path.join(BIBLEMATEGUI_DATA, "data", "exlb3.data")
    with apsw.Connection(vdb) as connn:
        cursor = connn.cursor()
        sql_query = "SELECT location FROM exlbli" # SELECT lat, lng FROM exlbli WHERE path=?
        cursor.execute(sql_query)
        all_locations = [i[0] for i in cursor.fetchall()]
    return all_locations

def search_bible_locations(gui=None, q='', **_):

    last_entry = q

    def cr(event):
        nonlocal gui
        b, c, v, *_ = event.args
        b = cr_books.get(b, b)
        gui.change_area_1_bible_chapter(None, b, c, v)

    def bcv(event):
        nonlocal gui
        b, c, v, *_ = event.args
        gui.change_area_1_bible_chapter(None, b, c, v)
    
    def website(event):
        url, *_ = event.args
        ui.navigate.to(url, new_tab=True)

    ui.on('bcv', bcv)
    ui.on('cr', cr)
    ui.on('website', website)

    # --- Fuzzy Match Dialog ---
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label("Bible Locations ...").classes('text-xl font-bold text-secondary mb-4')
        ui.label("We couldn't find an exact match. Please select one of these topics:").classes('text-secondary mb-4')
        
        # This container will hold the radio selection dynamically
        selection_container = ui.column().classes('w-full')
        
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat color=grey')

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------

    async def show_entry(path, keep=True):
        nonlocal content_container, gui, dialog, input_field, last_entry

        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        content, location, lat, lng = await run.io_bound(fetch_bible_locations_entry, path)
        n.dismiss()

        # Clear existing rows first
        content_container.clear()

        with content_container:
            # Google Map links
            if "Click HERE for a Live Google Map" in content:
                googleEarthLink = f"""https://earth.google.com/web/@{lat},{lng},654.97002989a,1336.11415664d,35y,0h,76.22542174t,-0r"""
                content = content.replace("Click HERE for a Live Google Map</ref>]", f'''Google Map</ref>] [<ref onclick="website('{googleEarthLink}')">Google Earth</ref>]''')
            # convert links, e.g. <ref onclick="bcv(3,19,26)">
            content = re.sub(r'''(onclick|ondblclick)="(cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
            content = re.sub(r"""(onclick|ondblclick)='(cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
            # remove images
            content = re.sub('<ref onclick="openHtmlImage.*?</ref>', '', content)
            # remove map
            content = content.replace('<div id="map" style="width:100%;height:500px"></div>', "")
            content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
            # add a map
            if lat and lng:
                def restore_center():
                    m.set_center((lat, lng))
                    m.set_zoom(9)
                with ui.element('div').style('position: relative; width: 100%; height: 384px;'):
                    m = ui.leaflet(center=(lat, lng), zoom=9).classes('w-full h-96')
                    with ui.button(on_click=restore_center).props('fab-mini color=primary icon=center_focus_strong').style(
                        'position: absolute; top: 20px; right: 20px; z-index: 1000;'
                    ):
                        ui.tooltip("Restore Center")
                marker = m.marker(latlng=(lat, lng))
                # Wait until marker is ready; wait 0.1 seconds to let the JS layer catch up
                async def bind_marker():
                    # 1. Non-blocking Wait: Checks every 0.1s, but lets other app events happen
                    while marker.id is None:
                        await asyncio.sleep(0.1)
                    # 2. Add a tiny buffer for the JavaScript side to render the marker
                    await asyncio.sleep(0.1)
                    # 3. Bind
                    marker.run_method('bindPopup', f"<b>{location}</b><br>{path}")
                # Fire the safe async function
                ui.timer(0.1, bind_marker, once=True)
            # convert colors for dark mode, e.g. <font color="brown">
            if app.storage.user['dark_mode']:
                content = content.replace('color="brown">', 'color="pink">')
                content = content.replace('color="navy">', 'color="lightskyblue">')
                content = content.replace('<table bgcolor="#BFBFBF"', '<table bgcolor="#424242"')
                content = content.replace('<td bgcolor="#FFFFFF">', '<td bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#FFFFFF">', '<tr bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#DFDFDF">', '<tr bgcolor="#303030">')
            # display
            ui.html(f'<div class="content-text">{content}</div>', sanitize=False).classes('mt-10')

            # Handler
            def search_action(entry):
                nonlocal gui
                """Logic when 'Character' button is clicked"""
                app.storage.user["tool_query"] = entry
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Maps')

            with ui.row().classes('w-full justify-center q-my-md'):
                ui.button('Show All Verses', icon='auto_stories', on_click=lambda: gui.show_all_verses(path)) \
                    .props('size=lg rounded color=primary')
                ui.button('Maps', icon='search', on_click=lambda: search_action(path)) \
                    .props('size=lg rounded color=primary')

        # Clear input so user can start typing to filter immediately
        last_entry = path
        input_field.value = ""
        # update tab records
        if keep:
            gui.update_active_area2_tab_records(q=path)

    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    async def handle_enter(e, keep=True):
        nonlocal input_field, dialog, selection_container, last_entry
        query = input_field.value.strip()
        if not query:
            return
        elif re.search("BL[0-9]+?$", query):
            await show_entry(query, keep=keep)
            return
        last_entry = query

        input_field.disable()

        try:
            path, options = await fetch_bible_locations_matches_async(query)
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
                    path, _ = selected_option.split(" ", 1)
                    ui.timer(0, lambda: show_entry(path[1:-1], keep=keep), once=True)

            selection_container.clear()
            with selection_container:
                # We use a radio button for selection
                radio = ui.radio(options).classes('w-full').props('color=primary')
                ui.button('Show Content', on_click=lambda: handle_selection(radio.value)) \
                    .classes('w-full mt-4 bg-blue-500 text-white shadow-md')    
            dialog.open()
        else:
            await show_entry(path, keep=keep)

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=[], # set empty as initial autocomplete value
            placeholder=f'{get_translation("Search for a bible location")}...'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        #input_field.on('update:model-value', filter_verses)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

        # update autocomplete
        async def get_all_locations():
            all_locations = await run.io_bound(fetch_all_locations)
            input_field.set_autocomplete(all_locations)
        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        ui.timer(0, get_all_locations, once=True)
        n.dismiss()

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        content_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    else:
        input_field.run_method('focus')
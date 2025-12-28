import apsw
import re, os
from nicegui import ui, app
from biblemategui import BIBLEMATEGUI_DATA, get_translation
from functools import partial
from biblemategui.fx.bible import BibleSelector


def resource_indexes(gui=None, bt=None, b=1, c=1, v=1, area=2, **_):

    def exlbl(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Locations')
    ui.on('exlbl', exlbl)
    def exlbp(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Characters')
    ui.on('exlbp', exlbp)
    def exlbt(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Topics')
    ui.on('exlbt', exlbt)
    def bibleDict(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Dictionaries')
    ui.on('bibleDict', bibleDict)
    def encyclopedia(event):
        nonlocal gui
        app.storage.user['favorite_encyclopedia'], app.storage.user['tool_query'] = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Encyclopedias')
    ui.on('encyclopedia', encyclopedia)

    # --- CONFIGURATION ---
    DB_FILE = os.path.join(BIBLEMATEGUI_DATA, 'indexes2.sqlite')

    # Define your tables, their display titles, and their icons
    TABLE_CONFIG = {
        "Bible People": {
            "table": "exlbp", 
            "icon": "groups"        # Icon for people/groups
        },
        "Bible Locations": {
            "table": "exlbl", 
            "icon": "place"         # Icon for maps/locations
        },
        "Bible Topics": {
            "table": "exlbt", 
            "icon": "category"      # Icon for topics/categories
        },
        "Bible Dictionaries": {
            "table": "dictionaries", 
            "icon": "loyalty"     # Icon for definitions/books
        },
        "Bible Encyclopedia": {
            "table": "encyclopedia", 
            "icon": "diamond" # Icon for deep knowledge/library
        }
    }

    def fetch_data(table_name: str, book_id: int, chapter: int, verse: int):
        """
        Connects to SQLite and retrieves information for the specific verse.
        """
        try:
            with apsw.Connection(DB_FILE) as connection:
                cursor = connection.cursor()
                query = f"SELECT Information FROM {table_name} WHERE Book=? AND Chapter=? AND Verse=?"
                cursor.execute(query, (book_id, chapter, verse))
                rows = cursor.fetchall()
                return "\n\n".join([row[0].replace("</td><td>", "&nbsp;&nbsp;</td><td>") for row in rows]) if rows else None
        except Exception as e:
            return f"Error querying database: {str(e)}"

    # --- UI LAYOUT ---
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):

        # Bible Selection menu
        bible_selector = BibleSelector(version_options=["KJV"])
        def additional_items():
            nonlocal gui, bible_selector, area
            def change_indexes(selection):
                if area == 1:
                    app.storage.user['tool_book_text'], app.storage.user['bible_book_number'], app.storage.user['bible_chapter_number'], app.storage.user['bible_verse_number'] = selection
                    gui.load_area_1_content(title="Indexes")
                else:
                    app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
                    gui.load_area_2_content(title="Indexes", sync=False)
            ui.button(get_translation('Go'), on_click=lambda: change_indexes(bible_selector.get_selection()))
        bible_selector.create_ui("KJV", b, c, v, additional_items=additional_items, show_versions=False)

        # Results Container
        results_container = ui.column().classes('w-full gap-4')

    def search_action(book_id, chapter, verse):
        # Clear UI and show loading spinner
        results_container.clear()
        
        with results_container:
            
            # Run IO-bound DB operations
            results = {}
            for title, config in TABLE_CONFIG.items():
                data = fetch_data(config['table'], book_id, chapter, verse)
                results[title] = data
            
            #parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
            #ui.label(f"Resources for {parser.bcvToVerseReference(book_id, chapter, verse)}") \
            #    .classes('text-xl font-semibold text-secondary mb-2')

            # --- RENDER EXPANSIONS ---
            found_any = False
            
            for title, config in TABLE_CONFIG.items():
                content = results.get(title)
                
                # Check if this should be open by default
                is_open = (title == "Bible Topics")
                
                # Create the Expansion with specific icon
                with ui.expansion(title, icon=config['icon'], value=is_open) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    
                    if content:
                        # convert links, e.g. <ref onclick="bcv(3,19,26)">
                        content = content.replace("<table><tr>", "<tr>")
                        content = content.replace("<tr>", "<table><tr>")
                        content = content.replace("</tr></table>", "</tr>")
                        content = content.replace("</tr>", "</tr></table>")
                        content = re.sub(r'''<ref onclick="(searchEncyc|searchDict)\('.*?'\)">(.*?)</ref>''', r"\2", content)
                        content = re.sub(r'''(onclick|ondblclick)="(cr|bcv|website|exlbl|exlbp|exlbt|bibleDict|encyclopedia)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
                        content = re.sub(r"""(onclick|ondblclick)='(cr|bcv|website|exlbl|exlbp|exlbt|bibleDict|encyclopedia)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
                        ui.html(f'<div class="content-text">{content}</div>', sanitize=False).classes('p-4')
                        found_any = True
                    else:
                        ui.label('No entries found for this category.') \
                            .classes('p-4 italic')

            def open_collection(collection, tool, number):
                nonlocal gui
                app.storage.user['tool_query'] = f"{tool}.{number}"
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title=collection)

            for i in ("PROMISES_INDEXES", "PARALLEL_INDEXES"):

                # Create the Expansion with specific icon
                with ui.expansion("Bible Promises" if i == "PROMISES_INDEXES" else "Bible Parallels", icon="redeem" if i == "PROMISES_INDEXES" else "link", value=is_open) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):

                    DB_FILE2 = os.path.join(BIBLEMATEGUI_DATA, "collections3.sqlite")
                    sql_query = "SELECT Tool, Number, Topic FROM " + i + " WHERE Passages LIKE ?"
                    with apsw.Connection(DB_FILE2) as connn:
                        cursor = connn.cursor()
                        cursor.execute(sql_query, (f"%({book_id}, {chapter}, {verse})%",))
                        fetches = cursor.fetchall()
                    
                    if fetches:
                        for tool, number, topic in fetches:
                            ui.chip(
                                topic,
                                icon='book',
                                color='primary',
                                on_click=partial(open_collection, "Promises" if i == "PROMISES_INDEXES" else "Parallels", tool, number),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                    else:
                        ui.label('No entries found for this category.') \
                            .classes('p-4 italic')

            if not found_any:
                ui.notify('No data found in any index for this verse.', type='info')
        
    search_action(b,c,v)

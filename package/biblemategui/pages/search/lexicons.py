from biblemategui import config, getLexiconList
from nicegui import ui, app
import re, apsw
from biblemategui.data.cr_books import cr_books
from biblemategui.fx.shared import get_image_data_uri

def search_bible_lexicons(gui=None, q='', **_):

    client_lexicons = getLexiconList()

    if q:
        if q.startswith("E") and not app.storage.user['favorite_lexicon'] in ("Morphology", "ConcordanceMorphology", "ConcordanceBook"):
            app.storage.user['favorite_lexicon'] = "Morphology"
        elif q.startswith("BDB"):
            app.storage.user['favorite_lexicon'] = "BDB"
        elif q.startswith("H"):
            app.storage.user['favorite_lexicon'] = app.storage.user.get('hebrew_lexicon', 'Morphology')
        elif q.startswith("G"):
            app.storage.user['favorite_lexicon'] = app.storage.user.get('greek_lexicon', 'Morphology')

    def get_lexicon_path(lexicon_name):
        nonlocal client_lexicons
        if not lexicon_name in client_lexicons:
            return client_lexicons[app.storage.user.get('favorite_lexicon', 'Morphology')]
        if lexicon_name in config.lexicons_custom:
            return config.lexicons_custom[lexicon_name]
        elif lexicon_name in config.lexicons:
            return config.lexicons[lexicon_name]

    scope_select = None

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

    def bdbid(event):
        nonlocal input_field
        id, *_ = event.args
        input_field.value = bdbid
        handle_enter(None)

    def lex(event):
        nonlocal input_field
        id, *_ = event.args
        input_field.value = id
        handle_enter(None)

    ui.on('bcv', bcv)
    ui.on('cr', cr)
    ui.on('website', website)
    ui.on('bdbid', bdbid)
    ui.on('lex', lex)

    # all entries
    def get_all_entries(lexicon):
        all_entries = []
        db = get_lexicon_path(lexicon)
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            sql_query = f"SELECT Topic FROM Lexicon"
            cursor.execute(sql_query)
            all_entries = [i[0] for i in cursor.fetchall()]
        return list(set([i for i in all_entries if i]))
    lexicon_module = app.storage.user.get('favorite_lexicon', 'Morphology')
    if lexicon_module not in client_lexicons:
        lexicon_module = 'Morphology'
        app.storage.user['favorite_lexicon'] = lexicon_module
    all_entries = get_all_entries(lexicon_module)

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------

    def change_module(new_module):
        nonlocal input_field, lexicon_module
        lexicon_module = new_module
        app.storage.user['favorite_lexicon'] = new_module
        input_field.autocomplete = get_all_entries(new_module)
        input_field.props(f'placeholder="Search {new_module} ..."')
        if scope_select and scope_select.value != new_module:
            scope_select.value = new_module

    def handle_enter(_, keep=True):
        nonlocal content_container, gui, input_field, lexicon_module

        topic = input_field.value.strip()

        # update tab records
        if keep:
            gui.update_active_area2_tab_records(q=topic)

        if (topic.startswith("E") and not lexicon_module in ("Morphology", "ConcordanceMorphology", "ConcordanceBook")):
            change_module("Morphology")
        elif (topic.startswith("G") and lexicon_module == "BDB"):
            change_module(app.storage.user.get('greek_lexicon', 'Morphology'))
        elif topic.startswith("BDB") or (topic.startswith("H") and lexicon_module in ("Morphology", "ConcordanceMorphology", "ConcordanceBook")):
            change_module("BDB")

        db = get_lexicon_path(lexicon_module)
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            sql_query = f"SELECT Definition FROM Lexicon WHERE Topic=? limit 1"
            cursor.execute(sql_query, (topic,))
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
            content = re.sub(r'''(onclick|ondblclick)="(bdbid|lex|cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
            content = re.sub(r"""(onclick|ondblclick)='(bdbid|lex|cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
            # remove map
            content = content.replace('<div id="map" style="width:100%;height:500px"></div>', "")
            content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
            # convert colors for dark mode, e.g. <font color="brown">
            if app.storage.user['dark_mode']:
                content = content.replace('color="brown">', 'color="pink">')
                content = content.replace('color="navy">', 'color="lightskyblue">')
                content = content.replace('<table bgcolor="#BFBFBF"', '<table bgcolor="#424242"')
                content = content.replace('<td bgcolor="#FFFFFF">', '<td bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#FFFFFF">', '<tr bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#DFDFDF">', '<tr bgcolor="#303030">')
            # convert images to data URI
            def replace_img(match):
                img_module = match.group(1)
                img_src = match.group(2)
                img_src = f"{img_module}_{img_src}"
                data_uri = get_image_data_uri(img_module, img_src)
                if data_uri:
                    return f'<img style="display: inline-block;" src="{data_uri}"/>'
                else:
                    return match.group(0)  # return original if not found
            content = re.sub(r'<img src="getImage.php\?resource=([A-Z]+?)&id=(.+?)"/>', replace_img, content)

            ui.add_head_html(f"""
            <style>
                /* Hebrew Word Layer */
                wform, heb, bdbheb, bdbarc, hu {{
                    font-family: 'SBL Hebrew', 'Ezra SIL', serif;
                    font-size: 1.8rem;
                    direction: rtl;
                    display: inline-block;
                    line-height: 1.2em;
                    margin-top: 0;
                    margin-bottom: -2px;
                    cursor: pointer;
                }}
                /* Greek Word Layer (targets <grk> tag) */
                wform, grk, kgrk, gu {{
                    font-family: 'SBL Greek', 'Galatia SIL', 'Times New Roman', serif; /* CHANGED */
                    font-size: 1.6rem;
                    direction: ltr;
                    display: inline-block;
                    line-height: 1.2em;
                    margin-top: 0;
                    margin-bottom: -2px;
                    cursor: pointer;
                }}
            </style>
            """)

            # display
            ui.html(f'<div class="bible-text">{content}</div>', sanitize=False)

        # Clear input so user can start typing to filter immediately
        if not content:
            ui.notify("No entry found.", color='warning')

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    initial_module = ""
    if q and ":::" in q:
        initial_module, q = q.split(":::")
        if not initial_module in client_lexicons:
            q = ""

    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=all_entries,
            placeholder=f'Search {lexicon_module} ...'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)

        scope_select = ui.select(
            options=client_lexicons,
            value=app.storage.user.get('favorite_lexicon', 'Morphology'),
            with_input=True
        ).classes('w-22').props('dense')

        if initial_module:
            change_module(initial_module)

        def handle_scope_change(e):
            nonlocal lexicon_module
            new_module = e.value
            change_module(new_module)
            handle_enter(None)
        scope_select.on_value_change(handle_scope_change)

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        content_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        handle_enter(None, keep=False)
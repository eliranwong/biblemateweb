from biblemategui import config, getLexiconList, get_translation
from nicegui import ui, app, run
import re, apsw
from biblemategui.data.cr_books import cr_books
from biblemategui.fx.shared import get_image_data_uri

def fetch_bible_lexicons_entry(client_lexicons, lexicon, topic):
    db = get_lexicon_path(client_lexicons, lexicon)
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        sql_query = f"SELECT Definition FROM Lexicon WHERE Topic=? limit 1"
        cursor.execute(sql_query, (topic,))
        fetch = cursor.fetchone()
        content = fetch[0] if fetch else ""
    return content

def get_lexicon_path(client_lexicons, lexicon_name):
    if not lexicon_name in client_lexicons:
        return client_lexicons[app.storage.user.get('favorite_lexicon', 'Morphology')]
    if lexicon_name in config.lexicons_custom:
        return config.lexicons_custom[lexicon_name]
    elif lexicon_name in config.lexicons:
        return config.lexicons[lexicon_name]

def fetch_all_lexicons_entries(client_lexicons, lexicon):
    db = get_lexicon_path(client_lexicons, lexicon)
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        sql_query = f"SELECT Topic FROM Lexicon"
        cursor.execute(sql_query)
        all_entries = [i[0] for i in cursor.fetchall()]
    return list(set([i for i in all_entries if i]))

def search_bible_lexicons(gui=None, q='', **_):

    last_entry = q
    client_lexicons = getLexiconList(app.storage.client["custom"])

    if q:
        if q.startswith("E") and not app.storage.user['favorite_lexicon'] in ("Morphology", "ConcordanceMorphology", "ConcordanceBook"):
            app.storage.user['favorite_lexicon'] = "Morphology"
        elif q.startswith("BDB"):
            app.storage.user['favorite_lexicon'] = "BDB"
        elif q.startswith("H"):
            app.storage.user['favorite_lexicon'] = app.storage.user.get('hebrew_lexicon', 'Morphology')
        elif q.startswith("G"):
            app.storage.user['favorite_lexicon'] = app.storage.user.get('greek_lexicon', 'Morphology')

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

    async def bdbid(event):
        nonlocal input_field
        id, *_ = event.args
        input_field.value = id
        await handle_enter(None)

    async def lex(event):
        nonlocal input_field
        id, *_ = event.args
        input_field.value = id
        await handle_enter(None)

    ui.on('bcv', bcv)
    ui.on('cr', cr)
    ui.on('website', website)
    ui.on('bdbid', bdbid)
    ui.on('lex', lex)

    lexicon_module = app.storage.user.get('favorite_lexicon', 'Morphology')
    if lexicon_module not in client_lexicons:
        lexicon_module = 'Morphology'
        app.storage.user['favorite_lexicon'] = lexicon_module

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------

    async def change_module(new_module):
        nonlocal input_field, lexicon_module
        lexicon_module = new_module
        app.storage.user['favorite_lexicon'] = new_module
        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        all_entries = await run.io_bound(fetch_all_lexicons_entries, client_lexicons, new_module)
        n.dismiss()
        input_field.set_autocomplete(all_entries)
        input_field.props(f'''placeholder="{get_translation('Search')} {new_module} ..."''')
        if scope_select and scope_select.value != new_module:
            scope_select.value = new_module

    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    async def handle_enter(_, keep=True):
        nonlocal content_container, gui, input_field, lexicon_module, last_entry

        topic = input_field.value.strip()
        if not topic:
            return

        last_entry = topic
        input_field.disable()

        try:

            # update tab records
            if keep:
                gui.update_active_area2_tab_records(q=topic)

            if (topic.startswith("E") and not lexicon_module in ("Morphology", "ConcordanceMorphology", "ConcordanceBook")):
                await change_module("Morphology")
            elif (topic.startswith("G") and lexicon_module == "BDB"):
                await change_module(app.storage.user.get('greek_lexicon', 'Morphology'))
            elif topic.startswith("BDB") or (topic.startswith("H") and lexicon_module in ("Morphology", "ConcordanceMorphology", "ConcordanceBook")):
                await change_module("BDB")

            n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
            content = await run.io_bound(fetch_bible_lexicons_entry, client_lexicons, lexicon_module, topic)
            n.dismiss()

        except Exception as e:
            # Handle errors (e.g., network failure)
            ui.notify(f'Error: {e}', type='negative')

        finally:
            # ALWAYS re-enable the input, even if an error occurred above
            input_field.enable()
            # Optional: Refocus the cursor so the user can type the next query immediately
            input_field.run_method('focus')

        # Clear existing rows first
        content_container.clear()

        with content_container:
            # Morhology Lexicon
            if lexicon_module == "Morphology":
                content = re.sub(r'''\[<ref onclick="(searchBook|searchCode)\(.*?\)">search</ref>\]''', "", content)
                content = re.sub("(</[on]tgloss>)", r"\1<br>", content)

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

            # display
            ui.html(f'<div class="content-text">{content}</div>', sanitize=False)

        # Clear input so user can start typing to filter immediately
        if not content:
            ui.notify("No entry found.", color='warning')

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    if q and ":::" in q:
        additional_options, q = q.split(":::", 1)
        if additional_options.strip() in client_lexicons:
            app.storage.user['favorite_lexicon'] = additional_options.strip()

    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        scope_select = ui.select(
            options=client_lexicons,
            value=app.storage.user.get('favorite_lexicon', 'Morphology'),
            with_input=True
        ).classes('w-22').props('dense')

        input_field = ui.input(
            autocomplete=[],
            placeholder=f'Search {lexicon_module} ...'
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

        async def get_all_entries(lexicon):
            all_entries = await run.io_bound(fetch_all_lexicons_entries, client_lexicons, lexicon)
            input_field.set_autocomplete(all_entries)
        n = ui.notification(get_translation('Loading...'), timeout=None, spinner=True)
        ui.timer(0, get_all_entries, once=True)
        n.dismiss()

        async def handle_scope_change(e):
            nonlocal lexicon_module
            new_module = e.value
            await change_module(new_module)
            await handle_enter(None)
        scope_select.on_value_change(handle_scope_change)

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        content_container = ui.column().classes('w-full transition-all !gap-1')

    if q:
        input_field.value = q
        ui.timer(0, lambda: handle_enter(None, keep=False), once=True)
    else:
        input_field.run_method('focus')
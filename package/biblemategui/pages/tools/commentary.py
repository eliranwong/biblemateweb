from nicegui import ui, app
from biblemategui import BIBLEMATEGUI_DATA, getCommentaryVersionList, get_translation
from biblemategui.data.cr_books import cr_books
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from agentmake.plugins.uba.lib.RegexSearch import RegexSearch
import apsw, os, re, markdown2

def get_ai_commentary_content(references: str, module: str = "AIC", language: str ="eng"):
    def fetch_ai_commentary_verse(b,c,v):
        fetch = None
        db = os.path.join(BIBLEMATEGUI_DATA, "commentaries", f"c{module}.commentary")
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            sql_query = "SELECT Content FROM Commentary WHERE Book=? AND Chapter=? AND Verse=? limit 1"
            cursor.execute(sql_query, (b,c,v))
            fetch = cursor.fetchone()
        return fetch
    parser = BibleVerseParser(False, language=language)
    references = parser.extractAllReferences(references)
    if not references:
        return ""
    results = []
    for ref in references:
        for b, c, v in parser.extractExhaustiveReferences([ref]):
            fetch = fetch_ai_commentary_verse(b,c,v)
            content = fetch[0] if fetch else ""
            if content:
                # remove AI follow-up comment
                if module == "AIC":
                    pattern = r'\n---\s*\nIf you\’d like\,\s*.*$'
                elif module == "AICTC":
                    pattern = r'\n---\s*\n如果你願意，\s*.*$'
                elif module == "AICSC":
                    pattern = r'\n---\s*\n如果您愿意，\s*.*$'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
                # convert md to html
                content = markdown2.markdown(content, extras=["tables","fenced-code-blocks","toc","codelite"])
                content = content.replace("<h1>", "<h2>").replace("</h1>", "</h2>")
                results.append(content)
    return "<hr>".join(results) if results else ""

def fetch_commentary_content(references: str, module: str = "CBSC", language: str ="eng"):
    if module in ("AIC", "AICTC", "AICSC"):
        # redirect for AI commentaries
        return get_ai_commentary_content(references, module, language)
    def fetch_commentary_chapter(b,c):
        fetch = None
        db = os.path.join(BIBLEMATEGUI_DATA, "commentaries", f"c{module}.commentary")
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            sql_query = "SELECT Scripture FROM Commentary WHERE Book=? AND Chapter=? limit 1"
            cursor.execute(sql_query, (b,c))
            fetch = cursor.fetchone()
        return fetch
    parser = BibleVerseParser(False, language=language)
    references = parser.extractAllReferences(references)
    if not references:
        return ""
    results = []
    for ref in references:
        b,c,*_ = ref
        results.append(f"<h2>{parser.bcvToVerseReference(*ref)}</h2>")
        fetch = fetch_commentary_chapter(b,c)
        content = fetch[0] if fetch else ""
        if content:
            fullVerseList = [f'<vid id="v{b}.{c}.{v}"' for b, c, v in parser.extractExhaustiveReferences([ref])]
            pattern = '(<vid id="v[0-9]+?.[0-9]+?.[0-9]+?"></vid>)<hr>'
            searchReplaceItems = ((pattern, r"<hr>\1"),)
            chapterCommentary = RegexSearch.deepReplace(content, pattern, searchReplaceItems)
            verseCommentaries = chapterCommentary.split("<hr>")

            loaded = []
            for i in verseCommentaries:
                for ii in fullVerseList:
                    if i.strip() and not i in loaded and ii in i:
                        loaded.append(i)
            content = "<hr>".join(loaded)
            results.append(content)
    return "<hr>".join(results) if results else ""

def bible_commentary(gui=None, b=1, c=1, v=1, q='', **_):

    last_entry = q
    BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]
    client_commentaries = getCommentaryVersionList(app.storage.client["custom"])
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

    def change_module(new_module):
        nonlocal scope_select
        app.storage.user['favorite_commentary'] = new_module
        if scope_select and scope_select.value != new_module:
            scope_select.value = new_module

    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    def handle_enter(_, keep=True):
        nonlocal content_container, gui, input_field, last_entry

        references = input_field.value.strip()
        if not references:
            return

        last_entry = references
        input_field.disable()

        try:

            content = fetch_commentary_content(references, module=app.storage.user.get('favorite_commentary', 'AIC'), language=app.storage.user['ui_language'])

            # update tab records
            if content and keep:
                gui.update_active_area2_tab_records(q=references)

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
            # convert links, e.g. <ref onclick="bcv(3,19,26)">
            content = re.sub(r'''(onclick|ondblclick)="(bdbid|lex|cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
            content = re.sub(r"""(onclick|ondblclick)='(bdbid|lex|cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
            # convert colors for dark mode, e.g. <font color="brown">
            content = content.replace("<font color='3'>", "<font color='pink'>" if app.storage.user['dark_mode'] else "<font color='brown'>")
            content = content.replace("<font color='4'>", "<font color='lightskyblue'>" if app.storage.user['dark_mode'] else "<font color='navy'>")
            if app.storage.user['dark_mode']:
                content = content.replace('color="brown">', 'color="pink">')
                content = content.replace('color="navy">', 'color="lightskyblue">')
                content = content.replace('<table bgcolor="#BFBFBF"', '<table bgcolor="#424242"')
                content = content.replace('<td bgcolor="#FFFFFF">', '<td bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#FFFFFF">', '<tr bgcolor="#212121">')
                content = content.replace('<tr bgcolor="#DFDFDF">', '<tr bgcolor="#303030">')

            # display
            ui.html(f'<div class="content-text">{content}</div>', sanitize=False)

        # Clear input so user can start typing to filter immediately
        if not content:
            ui.notify("No entry found.", color='warning')

    # ==============================================================================
    # UI LAYOUT
    # ==============================================================================
    if q and ":::" in q:
        additional_options, q = q.split(":::", 1)
        if additional_options.strip() in client_commentaries:
            app.storage.user['favorite_commentary'] = additional_options.strip()

    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        scope_select = ui.select(
            options=client_commentaries,
            value=app.storage.user.get('favorite_commentary', 'AIC'),
            with_input=True
        ).classes('w-22').props('dense')

        input_field = ui.input(
            autocomplete=BIBLE_BOOKS,
            placeholder=get_translation("Enter bible verse reference(s) here...")
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

        def handle_scope_change(e):
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
    else:
        parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        input_field.value = parser.bcvToVerseReference(b,c,v)
    handle_enter(None, keep=False)
    input_field.run_method('focus')
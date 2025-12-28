from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from biblemategui import BIBLEMATEGUI_DATA, get_translation
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemategui.data.cr_books import cr_books
from nicegui import ui, app
import re, apsw, os

def fetch_tske(b, c, v):
    db = os.path.join(BIBLEMATEGUI_DATA, "cross-reference.sqlite")
    with apsw.Connection(db) as connn:
        sql_query = "SELECT Information FROM TSKe WHERE Book=? AND Chapter=? AND Verse=? limit 1"
        cursor = connn.cursor()
        cursor.execute(sql_query, (b, c, v))
        fetch = cursor.fetchone()
    return fetch[0] if fetch else ""

def treasury(gui=None, b=1, c=1, v=1, q='', **_):

    last_entry = q
    SQL_QUERY = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"

    # --- Data: 66 Bible Books & ID Mapping ---
    BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]

    def cr(event):
        nonlocal gui
        b, c, v, *_ = event.args
        b = cr_books.get(b, b)
        gui.change_area_1_bible_chapter(None, b, c, v)

    ui.on('cr', cr)

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------
    def handle_up_arrow():
        nonlocal last_entry, input_field
        if not input_field.value.strip():
            input_field.value = last_entry

    def handle_enter(e, keep=True):
        nonlocal gui, SQL_QUERY, input_field, last_entry, content_container

        query = input_field.value.strip()
        if not query:
            return
        last_entry = query
        parser = BibleVerseParser(False)
        refs = parser.extractAllReferences(query)
        if not refs:
            ui.notify('No verses found!', type='negative')
            return
        # update tab records
        if keep:
            gui.update_active_area2_tab_records(q=query)
        # Clear existing rows first
        content_container.clear()

        input_field.disable()

        try:

            results = []
            for ref in refs:
                results.append(f"<h2>{parser.bcvToVerseReference(*ref)}</h2>")
                for ref2 in parser.extractExhaustiveReferences([ref]):
                    b, c, v = ref2
                    query = ""
                    content = fetch_tske(b, c, v)
                    if content:
                        results.append(content)
                    else:
                        continue
            content = "<hr>".join(results) if results else ""
            if not content: return None

        except Exception as e:
            # Handle errors (e.g., network failure)
            ui.notify(f'Error: {e}', type='negative')

        finally:
            # ALWAYS re-enable the input, even if an error occurred above
            input_field.enable()
            # Optional: Refocus the cursor so the user can type the next query immediately
            input_field.run_method('focus')

        with content_container:
            # convert links, e.g. <ref onclick="bcv(3,19,26)">
            content = re.sub(r'''(onclick|ondblclick)="(bdbid|lex|cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
            content = re.sub(r"""(onclick|ondblclick)='(bdbid|lex|cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
            # convert colors for dark mode, e.g. <font color="brown">
            if app.storage.user['dark_mode']:
                content = re.sub("<red>|</red>", "", content)
            ui.html(f'<div class="content-text">{content}</div>', sanitize=False)
                    

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.row().classes('w-full max-w-3xl mx-auto m-0 py-0 px-4 items-center'):
        input_field = ui.input(
            autocomplete=BIBLE_BOOKS,
            placeholder=get_translation("Enter bible verse reference(s) here...")
        ).classes('flex-grow text-lg') \
        .props('outlined dense clearable autofocus enterkeyhint="search"')

        input_field.on('keydown.enter.prevent', handle_enter)
        #input_field.on('update:model-value', filter_verses)
        input_field.on('keydown.up', handle_up_arrow)
        with input_field.add_slot('append'):
            ui.icon('history') \
                .on('click', handle_up_arrow) \
                .classes('text-sm cursor-pointer text-secondary').tooltip('Restore last entry')

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
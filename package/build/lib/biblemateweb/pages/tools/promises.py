import apsw
import re, os
from nicegui import ui, app
from biblemateweb import BIBLEMATEWEB_DATA, get_translation
#from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemateweb.fx.bible import BibleSelector


def bible_promises_menu(gui=None, **_):

    def promise(event):
        nonlocal gui
        tool, number = event.args
        app.storage.user['tool_query'] = f"{tool}.{number}"
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Promises')
    ui.on('promise', promise)

    # --- CONFIGURATION ---
    DB_FILE = os.path.join(BIBLEMATEWEB_DATA, 'books', 'Bible_Promises.book')
    with apsw.Connection(DB_FILE) as connn:
        cursor = connn.cursor()
        cursor.execute("SELECT Chapter, Content FROM Reference")
        fetches = cursor.fetchall()

    # --- UI LAYOUT ---
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):

        # Results Container
        with ui.column().classes('w-full gap-4'):

            for chapter, content in fetches:
                # Create the Expansion with specific icon
                with ui.expansion(chapter, icon='auto_stories', value=False) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"'):
                    
                    # convert links, e.g. <ref onclick="bcv(3,19,26)">
                    content = re.sub(r'''(onclick|ondblclick)="(cr|bcv|promise)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
                    content = re.sub(r"""(onclick|ondblclick)='(cr|bcv|promise)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
                    ui.html(f'<div class="content-text">{content}</div>', sanitize=False).classes('p-4')

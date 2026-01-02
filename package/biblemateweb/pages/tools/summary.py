from nicegui import ui, app, run
import os, re, apsw, markdown2, asyncio
from biblemateweb import BIBLEMATEWEB_DATA, get_translation
from biblemateweb.fx.bible import BibleSelector

def fetch_summary(b, c, lang="eng"):
    if lang == "tc":
        db = os.path.join(BIBLEMATEWEB_DATA, "data", "chapter_summary_tc.data")
    elif lang == "sc":
        db = os.path.join(BIBLEMATEWEB_DATA, "data", "chapter_summary_sc.data")
    else:
        db = os.path.join(BIBLEMATEWEB_DATA, "data", "chapter_summary.data")
    fetch = None
    with apsw.Connection(db) as connn:
        query = "SELECT Content FROM Summary WHERE Book=? AND Chapter=? LIMIT 1"
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        fetch = cursor.fetchone()
    return fetch[0] if fetch else "No summary available."

def chapter_summary(gui=None, b=1, c=1, v=1, area=2, **_):

    # handle bcv events
    def bcv(event):
        nonlocal gui
        b, c, v, *_ = event.args
        gui.change_area_1_bible_chapter(None, b, c, v)
    ui.on('bcv', bcv)

    # Bible Selection menu
    bible_selector = BibleSelector(version_options=["KJV"])
    def additional_items():
        nonlocal gui, bible_selector, area
        def change_summary_chapter(selection):
            if area == 1:
                _, app.storage.user['bible_book_number'], app.storage.user['bible_chapter_number'], app.storage.user['bible_verse_number'] = selection
                gui.load_area_1_content(title="Summary")
            else:
                _, app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
                gui.load_area_2_content(title="Summary", sync=False)
        ui.button(get_translation('Go'), on_click=lambda: change_summary_chapter(bible_selector.get_selection()))
    bible_selector.create_ui("KJV", b, c, v, additional_items=additional_items, show_versions=False, show_verses=False)

    # Summary display
    async def load_summary(b, c):
        n = ui.notification("Loading ...", timeout=None, spinner=True)
        await asyncio.sleep(0)
        # fetch content
        content = await run.io_bound(fetch_summary, b, c, app.storage.user['ui_language'])
        # clean up content
        if app.storage.user['ui_language'] == "tc":
            pattern = r'^好的，我將為[你您]\s*.*?#'
            content = re.sub(pattern, '#', content, flags=re.DOTALL)
            pattern = r'\n---\s*\n如果[你您]願意，\s*.*$'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        elif app.storage.user['ui_language'] == "sc":
            pattern = r'^好的，我将为[你您]\s*.*?#'
            content = re.sub(pattern, '#', content, flags=re.DOTALL)
            pattern = r'\n---\s*\n如果[你您]愿意，\s*.*$'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        else:
            pattern = r'^Alright\s*.*?#'
            content = re.sub(pattern, '#', content, flags=re.DOTALL)
            pattern = r'\n---\s*\nIf you\’d like\,\s*.*$'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        # convert md to html
        content = markdown2.markdown(content, extras=["tables","fenced-code-blocks","toc","codelite"])
        content = content.replace("<h1>", "<h2>").replace("</h1>", "</h2>")
        # convert links
        content = re.sub(r'''(onclick|ondblclick)="(bcv)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
        # display content
        ui.html(f'<div class="content-text">{content}</div>', sanitize=False)
        # dismiss notification
        n.dismiss()

    
    ui.timer(0, lambda: load_summary(b, c), once=True)   
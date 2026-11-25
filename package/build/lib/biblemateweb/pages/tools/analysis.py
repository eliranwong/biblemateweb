from nicegui import ui, app, run
import os, asyncio, apsw
from biblemateweb import BIBLEMATEWEB_DATA, download_docx, download_txt, get_translation, html_to_plain_text
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks

def get_db_file(lang="eng"):
    if lang == "tc":
        basefile = "book_analysis_tc.data"
    elif lang == "sc":
        basefile = "book_analysis_sc.data"
    else:
        basefile = "book_analysis.data"
    return os.path.join(BIBLEMATEWEB_DATA, "data", basefile)

def get_contents(b, lang="eng"):
    fetches = None
    contents = []
    with apsw.Connection(get_db_file(lang)) as connn:
        query = "SELECT Content FROM Introduction WHERE Book=? ORDER BY Section"
        cursor = connn.cursor()
        cursor.execute(query, (b,))
        fetches = cursor.fetchall()
    if fetches:
        contents = [fetch[0] for fetch in fetches]
    return contents

def book_analysis(gui=None, b=1, q="", **_):

    # handle book change
    def on_book_change(event):
        nonlocal gui
        app.storage.user['tool_book_number'] = event.value
        gui.load_area_2_content(title="Analysis", sync=False)

    # handle bcv events
    def bcv(event):
        nonlocal gui
        b, c, v, *_ = event.args
        gui.change_area_1_bible_chapter(None, b, c, v)
    ui.on('bcv', bcv)

    # Summary display
    async def load_analysis(b):
        n = ui.notification("Loading ...", timeout=None, spinner=True)
        await asyncio.sleep(0)
        contents = await run.io_bound(get_contents, b, app.storage.user['ui_language'])

        sections = {
            "Overview": "info",
            "Structural Outline": "account_tree",
            "Logical Flow": "low_priority",
            "Historical Setting": "history_edu",
            "Themes": "style",
            "Keywords": "vpn_key",
            "Theology": "auto_stories",
            "Canonical Placement": "format_list_numbered",
            "Practical Living": "volunteer_activism",
            "Summary": "summarize",
        }
        book_options = {i: BibleBooks.abbrev[app.storage.user['ui_language']][str(i)][-1] for i in range(1,67)}

        def _build_export_md():
            if not contents:
                return ""
            parts = [f"# {book_options.get(b, '')}"]
            for idx, section in enumerate(sections.keys()):
                if idx < len(contents):
                    parts.append(f"## {get_translation(section)}\n\n{html_to_plain_text(contents[idx])}")
            return "\n\n".join(parts)

        with ui.row().classes('w-full items-center justify-between gap-2'):
            ui.select(
                options=book_options,
                value=b,
                on_change=on_book_change,
            )
            if contents:
                with ui.row().classes('items-center gap-2'):
                    ui.button("DOCX", icon='description', on_click=lambda: download_docx(_build_export_md())).props('outline size=sm color=secondary')
                    ui.button("TXT", icon='download', on_click=lambda: download_txt(_build_export_md())).props('outline size=sm color=primary')

        if contents:
            # display content
            index = 0
            for section, icon in sections.items():
                with ui.expansion(get_translation(section), icon=icon, value=(q.lower() == section.lower())) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"'):
                    ui.html(f'<div class="content-text">{contents[index]}</div>', sanitize=False)
                index += 1
        n.dismiss()

    ui.timer(0, lambda: load_analysis(b), once=True)    
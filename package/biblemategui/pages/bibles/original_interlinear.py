from nicegui import ui, app
from biblemategui import get_translation
from biblemategui import BIBLEMATEGUI_DATA
from biblemategui.fx.bible import *
from biblemategui.fx.original import *
from biblemategui.fx.cloud_index_manager import get_drive_service, CloudIndexManager
from biblemategui.js.sync_scrolling import *
import re, os


def original_interlinear(gui=None, b=1, c=1, v=1, area=1, tab1=None, tab2=None, **_):

    verses_with_notes = []
    token = app.storage.user.get('google_token', "")
    if token:
        service = get_drive_service(token)
        index_mgr = CloudIndexManager(service)
        verses_with_notes = index_mgr.get_chapter_notes_verselist(b, c)

    dummy_label1 = None
    dummy_label2 = None

    bible_selector = BibleSelector(on_version_changed=gui.change_area_1_bible_chapter if area == 1 else gui.change_area_2_bible_chapter, on_book_changed=gui.change_area_1_bible_chapter if area == 1 else gui.change_area_2_bible_chapter, on_chapter_changed=gui.change_area_1_bible_chapter if area == 1 else gui.change_area_2_bible_chapter, on_verse_changed=change_bible_chapter_verse)

    def open_tool(tool):
        nonlocal area, gui
        if area == 2:
            gui.select_empty_area2_tab()
        gui.load_area_2_content(title=tool, sync=False)

    def lex(event):
        nonlocal gui
        lexical_entry, *_ = event.args
        app.storage.user['tool_query'] = lexical_entry
        open_tool("Lexicons")

    def wd(event):
        nonlocal gui
        lexical_entry, *_ = event.args
        app.storage.user['tool_query'] = lexical_entry
        open_tool("Lexicons")

    def note(event):
        nonlocal gui, area
        app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'], *_ = event.args
        open_tool("Notes")

    def luV1(event):
        nonlocal bible_selector, gui, db, dummy_label1, area
        b, c, v = event.args
        bible_selector.verse_select.value = v
        gui.update_active_area1_tab_records(v=v)
        with dummy_label1:
            gui.open_verse_context_menu(db, b, c, v, (str(v) in verses_with_notes))

    def luV2(event):
        nonlocal bible_selector, gui, db, dummy_label2, area
        b, c, v = event.args
        bible_selector.verse_select.value = v
        gui.update_active_area2_tab_records(v=v)
        with dummy_label2:
            gui.open_verse_context_menu(db, b, c, v, (str(v) in verses_with_notes))

    ui.on('wd', wd)
    ui.on('luV1', luV1)
    ui.on('luV2', luV2)
    ui.on('note', note)
    #ui.on('luW', luW)
    #ui.on('lex', lex)
    #ui.on('bdbid', bdbid)
    #ui.on('etcbcmorph', etcbcmorph)
    #ui.on('rmac', rmac)
    #ui.on('searchWord', searchWord)
    #ui.on('searchLexicalEntry', searchLexicalEntry)

    db = os.path.join(BIBLEMATEGUI_DATA, "original", "OIB.bible")
    if not os.path.isfile(db):
        return None
    content = getBibleChapter(db, b, c)

    # Fix known issues
    content = content.replace("<br<", "<br><")
    content = content.replace("<heb> </heb>", "<heb>&nbsp;</heb>")

    # add tooltip
    if "</heb>" in content:
        content = re.sub('(<heb id=")(.*?)"(.*?)class="', r'\1\2" data-word="\2" \3class="tooltip-word ', content)
    else:
        content = re.sub('(<grk id=")(.*?)"(.*?)class="', r'\1\2" data-word="\2" \3class="tooltip-word ', content)

    # convert verse link, like '<vid id="v19.117.1" onclick="luV(1)">'
    content = re.sub(r'<vid id="v([0-9]+?)\.([0-9]+?)\.([0-9]+?)" onclick="luV\(([0-9]+?)\)">', r'<vid id="v\1.\2.\3" onclick="luV(\1, \2, \3)">', content)
    
    # add notes
    if app.storage.user["notes"]:
        content = re.sub(f">({'|'.join(verses_with_notes)})</vid>", rf'''>\1</vid> <ref onclick="note({b},{c},\1)">📝</ref>''', content)
    # Convert onclick and ondblclick links
    content = content.replace("luV(", "luV1(" if area == 1 else "luV2(")
    content = re.sub(r'''(onclick|ondblclick)="(note|luV1|luV2|luW|lex|bdbid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
    content = re.sub(r"""(onclick|ondblclick)='(note|luV1|luV2|luW|lex|bdbid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)

    # Bible Selection menu
    def additional_items():
        nonlocal gui, bible_selector, area
        def previous_chapter(selection):
            selected_text, selected_b, selected_c, _ = selection
            bookList = getBibleBookList(db)
            chapterList = getBibleChapterList(db, selected_b)
            if len(chapterList) == 1 or selected_c == chapterList[0]:
                if selected_b == bookList[0]:
                    new_b = bookList[-1]
                    new_c = getBibleChapterList(db, new_b)[-1]
                else:
                    new_b = selected_b - 1
                    for i in bookList:
                        previous_book = None
                        if i == selected_b and previous_book is not None:
                            new_b = previous_book
                            break
                        else:
                            previous_book = i
                    new_c = getBibleChapterList(db, new_b)[-1]
            else:
                new_b = selected_b
                new_c = selected_c - 1
                for i in chapterList:
                    previous_chapter = None
                    if i == selected_c and previous_chapter is not None:
                        new_c = previous_chapter
                        break
                    else:
                        previous_chapter = i
            if area == 1:
                gui.change_area_1_bible_chapter(selected_text, new_b, new_c, 1)
            else:
                gui.change_area_2_bible_chapter(selected_text, new_b, new_c, 1)

        def next_chapter(selection):
            selected_text, selected_b, selected_c, _ = selection
            bookList = getBibleBookList(db)
            chapterList = getBibleChapterList(db, selected_b)
            if len(chapterList) == 1 or selected_c == chapterList[-1]:
                if selected_b == bookList[-1]:
                    new_b = bookList[0]
                    new_c = getBibleChapterList(db, new_b)[0]
                else:
                    new_b = selected_b + 1
                    for i in bookList:
                        previous_book = None
                        if previous_book is not None:
                            new_b = i
                            break
                        elif i == selected_b:
                            previous_book = i
                    new_c = getBibleChapterList(db, new_b)[0]
            else:
                new_b = selected_b
                new_c = selected_c + 1
                for i in chapterList:
                    previous_chapter = None
                    if previous_chapter is not None:
                        new_c = i
                        break
                    elif i == selected_c:
                        previous_chapter = i
            if area == 1:
                gui.change_area_1_bible_chapter(selected_text, new_b, new_c, 1)
            else:
                gui.change_area_2_bible_chapter(selected_text, new_b, new_c, 1)
        def open_tool(selection, title=""):
            app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
            gui.select_empty_area2_tab()
            gui.load_area_2_content(title=title, sync=False)
        def search_bible(q=""):
            app.storage.user['tool_query'] = q
            gui.select_empty_area2_tab()
            gui.load_area_2_content(title="Verses")
        with ui.button(icon='more_vert').props(f'flat round color={"white" if app.storage.user["dark_mode"] else "black"}'):
            with ui.menu():
                ui.menu_item(f'◀️ {get_translation("Prev Chapter")}', on_click=lambda: previous_chapter(bible_selector.get_selection()))
                ui.menu_item(f'▶️ {get_translation("Next Chapter")}', on_click=lambda: next_chapter(bible_selector.get_selection()))
                if area == 1:
                    ui.separator()
                    ui.menu_item(f'🔍 {get_translation("Search")} {bible_selector.version_select.value}', on_click=lambda: search_bible())
                    ui.menu_item(f'🔍 {get_translation("Search")} {get_translation("OT")}', on_click=lambda: search_bible(q=f"OT:::{app.storage.user['tool_query']}"))
                    ui.menu_item(f'🔍 {get_translation("Search")} {get_translation("NT")}', on_click=lambda: search_bible(q=f"NT:::{app.storage.user['tool_query']}"))
                    ui.menu_item(f'🔍 {get_translation("Search")} {bible_selector.book_select.value}', on_click=lambda: search_bible(q=f"{bible_selector.book_select.value}:::{app.storage.user['tool_query']}"))
                ui.separator()
                ui.menu_item(f'⏳ {get_translation("Timelines")}', on_click=lambda: open_tool(bible_selector.get_selection(), title="Timelines"))
                ui.separator()
                ui.menu_item(f'📡 {get_translation("Bible Podcast")}', on_click=lambda: open_tool(bible_selector.get_selection(), title="Podcast"))
                ui.menu_item(f'🔊 {get_translation("Bible Audio")}', on_click=lambda: open_tool(bible_selector.get_selection(), title="Audio"))
                ui.separator()
                ui.menu_item(f'🔗 {get_translation("Cross-references")}', on_click=lambda: open_tool(bible_selector.get_selection(), title="Xrefs"))
                ui.menu_item(f'📑 {get_translation("Indexes")}', on_click=lambda: open_tool(bible_selector.get_selection(), title="Indexes"))
                if config.google_client_id and config.google_client_secret:
                    ui.separator()
                    ui.menu_item(f'📝 {get_translation("Book Note")}', on_click=lambda: open_tool((bible_selector.selected_version, bible_selector.selected_book, 0, 0), title="Notes"))
                    ui.menu_item(f'📝 {get_translation("Chapter Note")}', on_click=lambda: open_tool((bible_selector.selected_version, bible_selector.selected_book, bible_selector.selected_chapter, 0), title="Notes"))
                    ui.menu_item(f'📝 {get_translation("Verse Note")}', on_click=lambda: open_tool(bible_selector.get_selection(), title="Notes"))
    bible_selector.create_ui("OIB", b, c, v, additional_items=additional_items)

    # create a dummy label for being the parent of `open_verse_context_menu`, as ui.html can't take two context menus
    # without a parent, the context menu doesn't close automatically
    dummy_style = 'position: absolute; width: 0; height: 0; overflow: hidden;'
    if area == 1:
        dummy_label1 = ui.label().style(dummy_style)
    else:
        dummy_label2 = ui.label().style(dummy_style)
    # Render the HTML inside a styled container
    ui.html(f'''<div class="bible-text-{'heb' if "</heb>" in content else 'grk'}">{content}</div>''', sanitize=False).classes(f'w-full pb-[70vh] {(tab1+"_chapter") if area == 1 else (tab2+"_chapter")}')

    # After the page is built and ready, run our JavaScript
    if (not area == 1) and tab1 and tab2:
        ui.run_javascript(f"""
            {SYNC_JS}
            
            {get_sync_fx(tab1, tab2)}
        """)

    # scrolling, e.g.
    ui.run_javascript(f'scrollToVerse("v{b}.{c}.{v}")')
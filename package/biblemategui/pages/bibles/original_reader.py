from nicegui import ui, app
from biblemategui import BIBLEMATEGUI_DATA
from biblemategui.css.original import get_original_css
from biblemategui.fx.bible import *
from biblemategui.fx.original import *
from biblemategui.js.sync_scrolling import *
import re, os


def original_reader(gui=None, b=1, c=1, v=1, area=1, tab1=None, tab2=None, **_):

    bible_selector = BibleSelector(on_version_changed=gui.change_area_1_bible_chapter if area == 1 else gui.change_area_2_bible_chapter, on_book_changed=gui.change_area_1_bible_chapter if area == 1 else gui.change_area_2_bible_chapter, on_chapter_changed=gui.change_area_1_bible_chapter if area == 1 else gui.change_area_2_bible_chapter, on_verse_changed=change_bible_chapter_verse)
    
    def wd(event):
        nonlocal gui
        lexical_entry, *_ = event.args
        app.storage.user['tool_query'] = lexical_entry
        gui.load_area_2_content(title='Lexicons')

    def luV(event):
        nonlocal bible_selector
        b, c, v = event.args
        bible_selector.verse_select.value = v
        """
        # Create a context menu at the click position
        with ui.context_menu() as menu:
            ui.menu_item('Bible Commentaries', on_click=lambda: ...))
            ui.menu_item('Cross-references', on_click=lambda: ...))
        menu.open()"""

    ui.on('wd', wd)
    ui.on('luV', luV)
    #ui.on('luW', luW)
    #ui.on('lex', lex)
    #ui.on('bdbid', bdbid)
    #ui.on('etcbcmorph', etcbcmorph)
    #ui.on('rmac', rmac)
    #ui.on('searchWord', searchWord)
    #ui.on('searchLexicalEntry', searchLexicalEntry)

    db = os.path.join(BIBLEMATEGUI_DATA, "original", "ORB.bible")
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
    
    # Convert onclick and ondblclick links
    content = re.sub(r'''(onclick|ondblclick)="(luV|luW|lex|bdbid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
    content = re.sub(r"""(onclick|ondblclick)='(luV|luW|lex|bdbid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)

    # Inject CSS to handle the custom tags and layout
    if "</heb>" in content:
        ui.add_head_html(f"""
        <style>
            /* Main container for the Bible text - ensures RTL flow for verses */
            .bible-text-heb {{
                direction: rtl;
                font-family: sans-serif;
                padding: 0px;
                margin: 0px;
            }}
            /* Verse ID Number */
            vid {{
                color: {'#f2c522' if app.storage.user['dark_mode'] else 'navy'};
                font-weight: bold;
                font-size: 0.9rem;
                margin-left: 10px; /* appears on the right due to RTL */
                cursor: pointer;
            }}
            /* Hebrew Word Layer */
            wform, heb, bdbheb, bdbarc, hu {{
                font-family: 'SBL Hebrew', 'Ezra SIL', serif;
                font-size: 1.6rem;
                direction: rtl;
                display: inline-block;
                line-height: 1.2em;
                margin-top: 0;
                margin-bottom: -2px;
                cursor: pointer;
            }}
            /* Lexical Form & Strong's Number Layers */
            wlex {{
                display: block;
                font-family: 'SBL Hebrew', serif;
                font-size: 1rem;
                cursor: pointer;
            }}
        </style>
        """)
    else:
        ui.add_head_html(f"""
        <style>
            /* Main container for the Bible text - LTR flow for Greek */
            .bible-text-grk {{
                direction: ltr;
                font-family: sans-serif;
                padding: 0px;
                margin: 0px;
            }}
            /* Verse ID Number */
            vid {{
                color: {'#f2c522' if app.storage.user['dark_mode'] else 'navy'};
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 10px;
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
            /* Lexical Form (lemma) & Strong's Number Layers */
            wlex {{
                display: block;
                font-family: 'SBL Greek', 'Galatia SIL', 'Times New Roman', serif; /* CHANGED */
                font-size: 1rem;
                cursor: pointer;
            }}
        </style>
        """)

    ui.add_head_html(get_original_css(app.storage.user['dark_mode']))
    
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
        def change_audio_chapter(selection):
            app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
            gui.select_empty_area2_tab()
            gui.load_area_2_content(title="Audio", sync=False)
        def search_bible(q=""):
            app.storage.user['tool_query'] = q
            gui.select_empty_area2_tab()
            gui.load_area_2_content(title="Verses")
        with ui.button(icon='more_vert').props(f'flat round color={"white" if app.storage.user["dark_mode"] else "black"}'):
            with ui.menu():
                ui.menu_item('Prev Chapter', on_click=lambda: previous_chapter(bible_selector.get_selection()))
                ui.menu_item('Next Chapter', on_click=lambda: next_chapter(bible_selector.get_selection()))
                if area == 1:
                    ui.separator()
                    ui.menu_item('Search Bible', on_click=lambda: search_bible())
                    ui.menu_item('Search OT', on_click=lambda: search_bible(q="OT:::"))
                    ui.menu_item('Search NT', on_click=lambda: search_bible(q="NT:::"))
                    ui.menu_item(f'Search {bible_selector.book_select.value}', on_click=lambda: search_bible(q=f"{bible_selector.book_select.value}:::"))
                ui.separator()
                ui.menu_item('Bible Audio', on_click=lambda: change_audio_chapter(bible_selector.get_selection()))
    bible_selector.create_ui("ORB", b, c, v, additional_items=additional_items)

    # Render the HTML inside a styled container
    # REMEMBER: sanitize=False is required to keep your onclick/onmouseover attributes
    ui.html(f'''<div class="bible-text-{'heb' if "</heb>" in content else 'grk'}">{content}</div>''', sanitize=False).classes(f'w-full pb-[70vh] {(tab1+"_chapter") if area == 1 else (tab2+"_chapter")}')

    # After the page is built and ready, run our JavaScript
    if (not area == 1) and tab1 and tab2:
        ui.run_javascript(f"""
            {SYNC_JS}
            
            {get_sync_fx(tab1, tab2)}
        """)

    # scrolling, e.g.
    ui.run_javascript(f'scrollToVerse("v{b}.{c}.{v}")')
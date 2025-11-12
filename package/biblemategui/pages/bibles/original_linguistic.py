from nicegui import ui
from biblemategui import BIBLEMATEGUI_DATA
from biblemategui.css.original import ORIGINAL_CSS
from biblemategui.fx.bible import *
from biblemategui.fx.original import *
from biblemategui.js.sync_scrolling import *
import re, os


def original_linguistic(b=1, c=1, v=1, area=1, tab1=None, tab2=None, **_):

    ui.on('luW', luW)
    ui.on('luV', luV)
    ui.on('lex', lex)
    ui.on('bdbid', bdbid)
    ui.on('etcbcmorph', etcbcmorph)
    ui.on('rmac', rmac)
    ui.on('searchWord', searchWord)
    ui.on('searchLexicalEntry', searchLexicalEntry)

    db = os.path.join(BIBLEMATEGUI_DATA, "original", "OLB.bible")
    if not os.path.isfile(db):
        return None
    content = getBibleChapter(db, b, c)

    # Fix known issues
    content = content.replace("<br<", "<br><")

    # convert verse link, like '<vid id="v19.117.1" onclick="luV(1)">'
    content = re.sub(r'<vid id="v([0-9]+?)\.([0-9]+?)\.([0-9]+?)" onclick="luV\(([0-9]+?)\)">', r'<vid id="v\1.\2.\3" onclick="luV(\1, \2, \3)">', content)
    
    # Convert onclick and ondblclick links
    content = re.sub(r'''(onclick|ondblclick)="(luV|luW|lex|bdbid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
    content = re.sub(r"""(onclick|ondblclick)='(luV|luW|lex|bdbid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)

    # Inject CSS to handle the custom tags and layout
    if "</heb>" in content:
        ui.add_head_html("""
        <style>
            /* Main container for the Bible text - ensures RTL flow for verses */
            .bible-text {
                direction: rtl;
                font-family: sans-serif;
                padding: 20px;
                background-color: #fafafa;
            }
            /* Verse ID Number */
            vid {
                color: navy;
                font-weight: bold;
                font-size: 0.9rem;
                margin-left: 10px; /* appears on the right due to RTL */
                cursor: pointer;
            }
            /* Hebrew Word Layer */
            wform, heb, bdbheb, bdbarc, hu {
                font-family: 'SBL Hebrew', 'Ezra SIL', serif;
                font-size: 1.6rem;
                color: #2c3e50;
                direction: rtl;
                display: inline-block;
                line-height: 1.2em;
                margin-top: 0;
                margin-bottom: -2px;
                cursor: pointer;
            }
            /* Lexical Form & Strong's Number Layers */
            wlex {
                display: block;
                font-family: 'SBL Hebrew', serif;
                font-size: 1rem;
                color: #555;
                cursor: pointer;
            }
        </style>
        """)
    else:
        ui.add_head_html("""
        <style>
            /* Main container for the Bible text - LTR flow for Greek */
            .bible-text {
                direction: ltr;
                font-family: sans-serif;
                padding: 20px;
                background-color: #fafafa;
            }
            /* Verse ID Number */
            vid {
                color: navy;
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 10px;
                cursor: pointer;
            }
            /* Greek Word Layer (targets <grk> tag) */
            wform, grk, kgrk, gu {
                font-family: 'SBL Greek', 'Galatia SIL', 'Times New Roman', serif; /* CHANGED */
                font-size: 1.6rem;
                color: #2c3e50;
                direction: ltr;
                display: inline-block;
                line-height: 1.2em;
                margin-top: 0;
                margin-bottom: -2px;
                cursor: pointer;
            }
            /* Lexical Form (lemma) & Strong's Number Layers */
            wlex {
                display: block;
                font-family: 'SBL Greek', 'Galatia SIL', 'Times New Roman', serif; /* CHANGED */
                font-size: 1rem;
                color: #555;
                cursor: pointer;
            }
        </style>
        """)
    
    ui.add_head_html(ORIGINAL_CSS)

    # Bible Selection menu
    bible_selector = BibleSelector(on_chapter_changed=change_area_1_bible_chapter if area == 1 else change_area_2_bible_chapter, on_verse_changed=change_bible_chapter_verse)
    bible_selector.create_ui("OLB", b, c, v)

    # Render the HTML inside a styled container
    # REMEMBER: sanitize=False is required to keep your onclick/onmouseover attributes
    ui.html(f'<div class="bible-text">{content}</div>', sanitize=False).classes(f'w-full pb-[70vh] {(tab1+"_chapter") if area == 1 else (tab2+"_chapter")}')

    # After the page is built and ready, run our JavaScript
    if (not area == 1) and tab1 and tab2:
        ui.run_javascript(f"""
            {SYNC_JS}
            
            {get_sync_fx(tab1, tab2)}
        """)

    # scrolling, e.g.
    ui.run_javascript(f'scrollToVerse("v{b}.{c}.{v}")')
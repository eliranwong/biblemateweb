import io, os, re
from biblemateweb import download_xlsx, get_morphology_db, get_translation
import apsw
from nicegui import ui, app, run
from biblemateweb.fx.bible import BibleSelector
from functools import partial

def fetch_morphology(b, c, v, custom=None):
    results = []
    db = get_morphology_db(custom)
    with apsw.Connection(db) as connn:
        query = "SELECT WordID, ClauseID, Book, Chapter, Verse, Word, LexicalEntry, MorphologyCode, Morphology, Lexeme, Transliteration, Pronunciation, Interlinear, Translation, Gloss FROM morphology WHERE Book=? AND Chapter=? AND Verse=? ORDER BY WordID"
        cursor = connn.cursor()
        cursor.execute(query, (b,c,v))
        results = cursor.fetchall()
    return results

def build_export_morphology_xlsx(rows) -> bytes:
    """Build an .xlsx Excel workbook from morphology rows."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Morphology"

    headers = [
        "WordID", "ClauseID", "Book", "Chapter", "Verse",
        "Word", "LexicalEntry", "MorphologyCode", "Morphology",
        "Lexeme", "Transliteration", "Pronunciation",
        "Interlinear", "Translation", "Gloss",
    ]
    ws.append(headers)
    header_font = Font(bold=True)
    header_align = Alignment(vertical="top")
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.alignment = header_align

    wrap_align = Alignment(wrap_text=True, vertical="top")
    for row in rows:
        word_id, clause_id, book, chapter, verse, word, lexical_entry, morph_code, morph, lexeme, translit, pronunc, interlinear, translation, gloss = row
        ws.append([
            word_id, clause_id, book, chapter, verse,
            word, (lexical_entry or "").rstrip(","), morph_code, (morph or "").rstrip(","),
            lexeme, translit, pronunc, interlinear, translation, gloss,
        ])
        row_idx = ws.max_row
        for col_idx in range(1, len(headers) + 1):
            ws.cell(row=row_idx, column=col_idx).alignment = wrap_align

    ws.freeze_panes = "A2"
    widths = [10, 10, 8, 9, 8, 16, 18, 16, 26, 16, 18, 16, 22, 22, 24]
    for col_idx, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

def word_morphology(gui=None, b=1, c=1, v=1, area=2, **_):

    def add_tooltips(verse_text):
        if "</heb>" in verse_text:
            verse_text = re.sub('(<heb id=")(.*?)"', r'\1\2" data-word="\2" class="tooltip-word"', verse_text)
            verse_text = verse_text.replace("<heb> </heb>", "<heb>&nbsp;</heb>")
        elif "</grk>" in verse_text:
            verse_text = re.sub('(<grk id=")(.*?)"', r'\1\2" data-word="\2" class="tooltip-word"', verse_text)
        return verse_text

    # --- UI LAYOUT ---
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):

        results = fetch_morphology(b, c, v, custom=app.storage.client["custom"])

        # Bible Selection menu
        bible_selector = BibleSelector(version_options=["KJV"])
        async def export_morphology_xlsx():
            if not results:
                ui.notify(get_translation("Nothing to download"), type='warning')
                return
            xlsx_bytes = await run.io_bound(build_export_morphology_xlsx, results)
            await download_xlsx(xlsx_bytes)

        def additional_items():
            nonlocal gui, bible_selector, area
            def change_morphology(selection):
                if area == 1:
                    app.storage.user['tool_book_text'], app.storage.user['bible_book_number'], app.storage.user['bible_chapter_number'], app.storage.user['bible_verse_number'] = selection
                    gui.load_area_1_content(title="Morphology")
                else:
                    app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
                    gui.load_area_2_content(title="Morphology", sync=False)
            ui.button(get_translation('Go'), on_click=lambda: change_morphology(bible_selector.get_selection()))
            ui.button(
                get_translation('Export Table'),
                icon='table_chart',
                on_click=export_morphology_xlsx,
            ).props('outline size=sm color=secondary')
        bible_selector.create_ui("KJV", b, c, v, additional_items=additional_items, show_versions=False)

        def open_lexicon(module, entry):
            app.storage.user['favorite_lexicon'] = module
            app.storage.user['tool_query'] = entry
            gui.select_empty_area2_tab()
            gui.load_area_2_content(title='lexicons')
        
        # Results Container
        morphology_data = {}
        def update_morphology_data(wordID, index):
            nonlocal morphology_data
            morphology_data[wordID][index]["selected"] = not morphology_data[wordID][index]["selected"]
            #import pprint
            #pprint.pprint(morphology_data)
        def search_morphology(wordID, lexical_entry, bible):
            nonlocal gui, morphology_data
            app.storage.user["tool_book_text"] = bible
            queries = [lexical_entry]
            for i in morphology_data[wordID]:
                if i == 0 and morphology_data[wordID][i]["selected"]:
                    query = morphology_data[wordID][i]["element"] + ",%"
                elif morphology_data[wordID][i]["selected"]:
                    query = "%," + morphology_data[wordID][i]["element"] + ",%"
                queries.append(query)
            if len(queries) > 1:
                app.storage.user["tool_query"] = "|".join(queries)
                gui.select_empty_area2_tab()
                gui.load_area_2_content(title='Verses')
            else:
                ui.notify("Select morphology to search for first!")

        with ui.column().classes('w-full gap-4'):
            if results:
                for wordID, clauseID, book, chapter, verse, word, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronunciation, interlinear, translation, gloss in results:
                    morphology_data[wordID] ={}
                    lexicalEntries = lexicalEntry.split(",")[:-1]
                    with ui.card():
                        tag = "heb" if book < 40 else "grk"
                        html = f'''<{tag} id="{'wh' if book < 40 else 'w'}{wordID}">{word}</{tag}>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;<ref data-word="{lexicalEntries[-1]}" class="tooltip-word"><{tag}>{lexeme}</{tag}></ref>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;<inter>{interlinear}</inter>'''
                        ui.html(add_tooltips(html), sanitize=False).classes('w-full')
                        with ui.row().classes('w-full gap-0'):
                            for index, element in enumerate(morphology.split(",")[:-1]):
                                #ui.label(element).classes(
                                #    f"text-base px-2 py-0.5 rounded-full"+(" text-secondary" if index == 0 else "")
                                #)
                                if not element == "unknown":
                                    morphology_data[wordID][index] = {"element": element, "selected": True}
                                    ui.chip(element, selectable=True, selected=True, color='orange', on_selection_change=partial(update_morphology_data, wordID, index)).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                        with ui.row().classes('w-full gap-0'):
                            ui.chip(
                                "OHGB",
                                icon='search',
                                color='primary',
                                on_click=partial(search_morphology, wordID, lexicalEntries[0], "OHGB"),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            ui.chip(
                                "OHGBi",
                                icon='search',
                                color='primary',
                                on_click=partial(search_morphology, wordID, lexicalEntries[0], "OHGBi"),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            active_bible_text = gui.get_area_1_bible_text()
                            ui.chip(
                                active_bible_text,
                                icon='search',
                                color='primary',
                                on_click=partial(search_morphology, wordID, lexicalEntries[0], active_bible_text),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            if not active_bible_text == app.storage.user['primary_bible']:
                                ui.chip(
                                    app.storage.user['primary_bible'],
                                    icon='search',
                                    color='primary',
                                    on_click=partial(search_morphology, wordID, lexicalEntries[0], app.storage.user['primary_bible']),
                                ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            if not active_bible_text == app.storage.user['secondary_bible'] and not app.storage.user['primary_bible'] == app.storage.user['secondary_bible']:
                                ui.chip(
                                    app.storage.user['secondary_bible'],
                                    icon='search',
                                    color='primary',
                                    on_click=partial(search_morphology, wordID, lexicalEntries[0], app.storage.user['secondary_bible']),
                                ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                        with ui.row().classes('w-full gap-0'):
                            ui.chip(
                                "Forms",
                                icon='book',
                                color='primary',
                                on_click=partial(open_lexicon, "Morphology", lexicalEntries[0]),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            ui.chip(
                                "Concordance [Forms]",
                                icon='book',
                                color='primary',
                                on_click=partial(open_lexicon, "ConcordanceMorphology", lexicalEntries[0]),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            ui.chip(
                                "Concordance [Books]",
                                icon='book',
                                color='primary',
                                on_click=partial(open_lexicon, "ConcordanceBook", lexicalEntries[0]),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
                            ui.chip(
                                "Lexicon",
                                icon='book',
                                color='primary',
                                on_click=partial(open_lexicon, app.storage.user['hebrew_lexicon'] if b < 40 else app.storage.user['greek_lexicon'], lexicalEntries[-1]),
                            ).props('text-color=white').classes('cursor-pointer font-bold shadow-sm')
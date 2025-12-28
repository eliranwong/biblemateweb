import os, re
from biblemategui import BIBLEMATEGUI_DATA, get_translation
import apsw
from nicegui import ui, app
from biblemategui.fx.bible import BibleSelector
from functools import partial

def fetch_morphology(b, c, v):
    results = []
    db = os.path.join(BIBLEMATEGUI_DATA, "morphology.sqlite")
    with apsw.Connection(db) as connn:
        query = "SELECT * FROM morphology WHERE Book=? AND Chapter=? AND Verse=? ORDER BY WordID"
        cursor = connn.cursor()
        cursor.execute(query, (b,c,v))
        results = cursor.fetchall()
    return results

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

        # Bible Selection menu
        bible_selector = BibleSelector(version_options=["KJV"])
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
            if results := fetch_morphology(b,c,v):
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
import os, re
from biblemateweb import get_morphology_db, get_translation
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

def fetch_chapter_vocabulary(b, c, custom=None):
    db = get_morphology_db(custom)
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(
            """
            SELECT LexicalEntry, Lexeme, Gloss, COUNT(*) as cnt
            FROM morphology
            WHERE Book=? AND Chapter=? AND LexicalEntry != ''
            GROUP BY LexicalEntry
            ORDER BY cnt DESC
            """,
            (b, c),
        )
        chapter_rows = cursor.fetchall()
        if not chapter_rows:
            return [], []
        top_words = chapter_rows[:15]
        entries = [r[0] for r in chapter_rows]
        placeholders = ",".join("?" for _ in entries)
        cursor.execute(
            f"SELECT LexicalEntry, COUNT(*) as total_cnt FROM morphology WHERE LexicalEntry IN ({placeholders}) GROUP BY LexicalEntry HAVING total_cnt <= 3 ORDER BY total_cnt ASC",
            entries,
        )
        rare_map = dict(cursor.fetchall())
        rare_words = [(r[0], r[1], r[2], r[3], rare_map[r[0]]) for r in chapter_rows if r[0] in rare_map]
    return top_words, rare_words

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
            if results := fetch_morphology(b,c,v, custom=app.storage.client["custom"]):
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

        # Chapter Vocabulary & Rare Words (lazy-loaded on expand)
        vocab_loaded = {'done': False}
        async def load_vocab(e):
            if not e.value or vocab_loaded['done']:
                return
            vocab_loaded['done'] = True
            vocab_container.clear()
            with vocab_container:
                ui.spinner(size='sm')
            top_words, rare_words = await run.io_bound(fetch_chapter_vocabulary, b, c, app.storage.client["custom"])
            vocab_container.clear()
            with vocab_container:
                if not top_words:
                    ui.label(get_translation('No data found.'))
                    return
                ui.label(get_translation('Top Chapter Lemmas')).classes('font-bold text-sm mt-1')
                with ui.row().classes('w-full gap-2 flex-wrap'):
                    for entry, lexeme, gloss, cnt in top_words:
                        first_entry = entry.split(",")[0]
                        lex_entry = entry.split(",")[-2] if entry.endswith(",") and len(entry.split(",")) > 1 else first_entry
                        ui.chip(
                            f"{lexeme} ({cnt}) — {gloss}",
                            icon='search',
                            on_click=partial(open_lexicon, app.storage.user['hebrew_lexicon'] if b < 40 else app.storage.user['greek_lexicon'], lex_entry),
                        ).props('outline').classes('cursor-pointer')
                if rare_words:
                    ui.label(get_translation('Rare Words in Chapter (<= 3x in Bible)')).classes('font-bold text-sm mt-3')
                    with ui.row().classes('w-full gap-2 flex-wrap'):
                        for entry, lexeme, gloss, ch_cnt, total_cnt in rare_words:
                            lex_entry = entry.split(",")[-2] if entry.endswith(",") and len(entry.split(",")) > 1 else entry.split(",")[0]
                            badge_label = "1x (hapax)" if total_cnt == 1 else f"{total_cnt}x"
                            ui.chip(
                                f"{lexeme} [{badge_label}] — {gloss}",
                                color='deep-orange' if total_cnt == 1 else 'amber-8',
                                on_click=partial(open_lexicon, app.storage.user['hebrew_lexicon'] if b < 40 else app.storage.user['greek_lexicon'], lex_entry),
                            ).props('text-color=white').classes('cursor-pointer')

        with ui.expansion(get_translation('Chapter Vocabulary & Rare Words'), icon='analytics', value=False, on_value_change=load_vocab).classes('w-full rounded-lg border border-gray-200'):
            vocab_container = ui.column().classes('w-full gap-2')
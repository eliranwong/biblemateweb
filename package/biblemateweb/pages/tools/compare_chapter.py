from nicegui import ui, app
from biblemateweb import (
    apply_verse_highlights_html,
    download_docx,
    getBibleVersionList,
    get_chapter_comparison_bibles,
    get_translation,
)
from biblemateweb.data.cr_books import cr_books
from biblemateweb.data.lexical_data import lexical_data
from biblemateweb.fx.bible import (
    BibleSelector,
    formatHTMLverse,
    getBibleBookList,
    getBibleChapter,
    getBibleChapterList,
    getBibleChapterVerses,
    getBiblePath,
)
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
import difflib
import html as html_lib
import os
import re


def _strong_to_lex(match):
    lexical_entry = match.group(1)
    if lexical_entry in lexical_data:
        return rf'<ref data-word="{lexical_entry}" class="tooltip-word">{lexical_data[lexical_entry][0]}'
    if lexical_entry + "a" in lexical_data:
        return rf'<ref data-word="{lexical_entry}" class="tooltip-word">{lexical_data[lexical_entry + "a"][0]}'
    return match.group(0)


def _process_bible_html(content, version, b, c, area=2, dark_mode=False):
    """Apply mutual word highlighting, tooltips, links, and user verse highlights to Bible HTML."""
    if not content:
        return ""

    content = content.replace("<br<", "<br><")
    content = content.replace("<heb> </heb>", "<heb>&nbsp;</heb>")

    # Tooltips and mutual word highlighting (hl1 / hl0)
    content = re.sub(
        r'(<(?:heb|grk|en|zh) id=")(.*?)"',
        r'\1\2" data-word="\2" class="tooltip-word"',
        content,
    )
    content = re.sub(
        r'(<(?:heb|grk|en|zh)\b[^>]*\bid="w([^"]+)"(?![^>]*\bonmouseover=))',
        r'''\1 onmouseover="hl1('\2','','')" onmouseout="hl0('\2','','')"''',
        content,
    )

    # Study notes
    if "<ref onclick='bn(" in content:
        content = re.sub(
            rf'''<ref onclick='bn\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?"(.*?)"\)'>''',
            rf'<ref data-word="bn,{version},\1,\2,\3,\4" class="tooltip-word">',
            content,
        )
    elif '<ref onclick="bn(' in content:
        content = re.sub(
            rf'''<ref onclick="bn\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?'(.*?)'\)">''',
            rf'<ref data-word="bn,{version},\1,\2,\3,\4" class="tooltip-word">',
            content,
        )

    # Strong's numbers
    if "<ref onclick='lex(" in content:
        content = re.sub(r'''<ref onclick='lex\("(.*?)"\)'>\1''', _strong_to_lex, content)
    elif '<ref onclick="lex(' in content:
        content = re.sub(r'''<ref onclick="lex\('(.*?)'\)">\1''', _strong_to_lex, content)

    # Verse links
    content = re.sub(
        r'<vid id="v([0-9]+?)\.([0-9]+?)\.([0-9]+?)" onclick="luV\(([0-9]+?)\)">',
        r'<vid id="v\1.\2.\3" onclick="luV(\1, \2, \3)">',
        content,
    )

    # UBA bible links
    if '''<ref onclick='document.title="BIBLE:::''' in content:
        def convert_uba_bible_link(match):
            parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
            refs = parser.extractAllReferences(match.group(1))
            if refs:
                ref = parser.bcvToVerseReference(*refs[0])
                return f'''<ref onclick="bcv{refs[0]}">{ref}'''
            return match.group(0)

        content = re.sub(
            r'''<ref onclick='document.title="BIBLE:::([^<>]+?)"'>\1''',
            convert_uba_bible_link,
            content,
        )

    # Convert onclick and ondblclick handlers to NiceGUI emitEvent
    content = content.replace("luV(", "luV1(" if area == 1 else "luV2(")
    content = re.sub(
        r'''(onclick|ondblclick)="(note|cr|bcv|luV1|luV2|luW|lex|bdbid|bdbeid|bdagid|halotid|chalotid|lsjid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)"''',
        r'''\1="emitEvent('\2', [\3]); return false;"''',
        content,
    )
    content = re.sub(
        r"""(onclick|ondblclick)='(note|cr|bcv|luV1|luV2|luW|lex|bdbid|bdbeid|bdagid|halotid|chalotid|lsjid|etcbcmorph|rmac|searchLexicalEntry|searchWord)\((.*?)\)'""",
        r"""\1='emitEvent("\2", [\3]); return false;'""",
        content,
    )

    # Adjust spacing
    content = content.replace("</vid> <pb/><br>", "</vid> ")
    content = content.replace("<br>&emsp;&emsp;", "<br><br>&emsp;&emsp;")
    content = content.replace("<br><br><br>&emsp;&emsp;", "<br><br>&emsp;&emsp;")
    content = content.replace("<br><br>", "<hr>")
    content = content.replace("<br>", "")
    content = content.replace("<hr>", "<br>")

    content = apply_verse_highlights_html(
        content,
        b,
        c,
        highlights=app.storage.user.get('verse_highlights'),
        dark_mode=dark_mode,
    )
    return content


def _word_diff_html(base_html, other_html):
    """Highlight word differences in other_html relative to base_html."""
    base_plain = re.sub(r"<[^<>]+?>", "", base_html or "").strip()
    other_plain = re.sub(r"<[^<>]+?>", "", other_html or "").strip()
    base_words = base_plain.split()
    other_words = other_plain.split()
    matcher = difflib.SequenceMatcher(None, base_words, other_words)
    parts = []
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        segment = html_lib.escape(" ".join(other_words[j1:j2]))
        if not segment:
            continue
        if tag == 'equal':
            parts.append(segment)
        else:
            parts.append(
                f"<span style='background-color: rgba(245, 158, 11, 0.3); padding: 0 2px; border-radius: 3px;'>{segment}</span>"
            )
    return " ".join(parts)


def compare_chapter(gui=None, bt=None, b=1, c=1, v=1, area=2, q='', **_):
    """Standalone page for side-by-side Bible chapter comparison."""
    state = {
        'b': int(b or 1),
        'c': int(c or 1),
        'v': int(v or 1),
    }

    available_versions = getBibleVersionList(app.storage.client.get("custom", False))
    active_bible = bt or (gui.get_area_1_bible_text() if gui else app.storage.user.get("primary_bible", "NET"))

    if q:
        parsed_q = [ver.strip() for ver in q.split(",") if ver.strip() in available_versions]
    else:
        parsed_q = []
    initial_versions = parsed_q or get_chapter_comparison_bibles(active_bible=active_bible)
    if not initial_versions and available_versions:
        initial_versions = [available_versions[0]]

    # Ensure storage defaults exist
    if 'compare_chapter_verse_by_verse' not in app.storage.user:
        app.storage.user['compare_chapter_verse_by_verse'] = False
    if 'compare_chapter_diff' not in app.storage.user:
        app.storage.user['compare_chapter_diff'] = False

    dummy_label = None
    versions_select = None
    table_container = None

    def open_tool(tool):
        if area == 2:
            gui.select_empty_area2_tab()
        gui.load_area_2_content(title=tool, sync=False)

    def lex(event):
        lexical_entry, *_ = event.args
        app.storage.user['tool_query'] = lexical_entry
        open_tool("Lexicons")

    def wd(event):
        lexical_entry, *_ = event.args
        app.storage.user['tool_query'] = lexical_entry
        open_tool("Lexicons")

    def morph(event):
        morph_query, *_ = event.args
        app.storage.user['tool_book_text'] = gui.get_area_1_bible_text()
        app.storage.user['tool_query'] = morph_query
        open_tool("Verses")

    def note(event):
        app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'], *_ = event.args
        open_tool("Notes")

    def luV2(event):
        vb, vc, vv = event.args
        primary_ver = (versions_select.value[0] if versions_select and versions_select.value else active_bible)
        db_path = getBiblePath(primary_ver)
        if db_path and os.path.isfile(db_path) and dummy_label is not None:
            with dummy_label:
                gui.open_verse_context_menu(db_path, vb, vc, vv, False)

    def cr(event):
        rb, rc, rv, *_ = event.args
        rb = cr_books.get(rb, rb)
        gui.change_area_1_bible_chapter(None, rb, rc, rv)

    def bcv(event):
        rb, rc, rv, *_ = event.args
        gui.change_area_1_bible_chapter(None, rb, rc, rv)

    for event_name in ('lex', 'bdbid', 'bdbeid', 'bdagid', 'halotid', 'chalotid', 'lsjid'):
        ui.on(event_name, lex)
    ui.on('note', note)
    ui.on('luV2', luV2)
    ui.on('wd', wd)
    ui.on('morph', morph)
    ui.on('bcv', bcv)
    ui.on('cr', cr)

    # Navigation helpers
    def _nav_db():
        ver = (versions_select.value[0] if versions_select and versions_select.value else active_bible)
        return getBiblePath(ver)

    def _sync_selector_and_render(new_b, new_c, new_v=1):
        state['b'] = new_b
        state['c'] = new_c
        state['v'] = new_v
        app.storage.user['tool_book_number'] = new_b
        app.storage.user['tool_chapter_number'] = new_c
        app.storage.user['tool_verse_number'] = new_v

        lang = app.storage.user.get('ui_language', 'eng')
        if str(new_b) in BibleBooks.abbrev.get(lang, {}):
            book_name = BibleBooks.abbrev[lang][str(new_b)][0]
            bible_selector.selected_book = new_b
            bible_selector.book_select.value = book_name
            bible_selector.book_select.update()
        chapter_opts = getBibleChapterList(_nav_db(), new_b)
        bible_selector.chapter_options = chapter_opts
        bible_selector.chapter_select.options = chapter_opts
        bible_selector.selected_chapter = new_c
        bible_selector.chapter_select.value = new_c
        bible_selector.chapter_select.update()

        render_table()

    def go_to_selected():
        _, sel_b, sel_c, _ = bible_selector.get_selection()
        state['b'] = sel_b
        state['c'] = sel_c
        state['v'] = 1
        app.storage.user['tool_book_number'] = sel_b
        app.storage.user['tool_chapter_number'] = sel_c
        app.storage.user['tool_verse_number'] = 1
        render_table()

    def previous_chapter():
        db = _nav_db()
        cur_b, cur_c = state['b'], state['c']
        book_list = getBibleBookList(db)
        chapter_list = getBibleChapterList(db, cur_b)
        if not book_list or not chapter_list:
            return
        if len(chapter_list) == 1 or cur_c == chapter_list[0]:
            idx = book_list.index(cur_b) if cur_b in book_list else 0
            new_b = book_list[idx - 1]
            new_c = getBibleChapterList(db, new_b)[-1]
        else:
            new_b = cur_b
            idx = chapter_list.index(cur_c) if cur_c in chapter_list else 0
            new_c = chapter_list[idx - 1]
        _sync_selector_and_render(new_b, new_c, 1)

    def next_chapter():
        db = _nav_db()
        cur_b, cur_c = state['b'], state['c']
        book_list = getBibleBookList(db)
        chapter_list = getBibleChapterList(db, cur_b)
        if not book_list or not chapter_list:
            return
        if len(chapter_list) == 1 or cur_c == chapter_list[-1]:
            idx = book_list.index(cur_b) if cur_b in book_list else 0
            new_b = book_list[(idx + 1) % len(book_list)]
            new_c = getBibleChapterList(db, new_b)[0]
        else:
            new_b = cur_b
            idx = chapter_list.index(cur_c) if cur_c in chapter_list else 0
            new_c = chapter_list[(idx + 1) % len(chapter_list)]
        _sync_selector_and_render(new_b, new_c, 1)

    # --- Top Controls ---
    bible_selector = BibleSelector(version_options=available_versions)

    async def export_docx():
        selected = [ver for ver in (versions_select.value or []) if ver in available_versions]
        if not selected:
            ui.notify(get_translation("Nothing to download"), type='negative')
            return
        cur_b, cur_c = state['b'], state['c']
        verse_by_verse = bool(app.storage.user.get('compare_chapter_verse_by_verse', False))
        lang = app.storage.user.get('ui_language', 'eng')
        chapter_ref = BibleVerseParser(False, language=lang).bcvToVerseReference(cur_b, cur_c, 1, isChapter=True)

        def _clean_cell(text):
            plain = re.sub(r"<[^<>]+?>", " ", text or "")
            plain = html_lib.unescape(plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            return plain.replace("|", "\\|")

        lines = [f"# {chapter_ref}", ""]
        if not verse_by_verse:
            lines.append("| " + " | ".join(selected) + " |")
            lines.append("| " + " | ".join("---" for _ in selected) + " |")
            cells = []
            for ver in selected:
                db_path = getBiblePath(ver)
                verses = getBibleChapterVerses(db_path, cur_b, cur_c) if db_path else []
                if verses:
                    cell_text = " ".join(f"**{vv}** {_clean_cell(vtext)}" for _, _, vv, vtext in verses)
                else:
                    raw_html = getBibleChapter(db_path, cur_b, cur_c) if db_path else ""
                    cell_text = _clean_cell(raw_html)
                cells.append(cell_text)
            lines.append("| " + " | ".join(cells) + " |")
        else:
            version_verse_maps = []
            all_verse_nums = set()
            for ver in selected:
                db_path = getBiblePath(ver)
                vmap = {}
                if db_path:
                    try:
                        for _, _, vv, vtext in getBibleChapterVerses(db_path, cur_b, cur_c):
                            vmap[vv] = _clean_cell(vtext)
                            all_verse_nums.add(vv)
                    except Exception:
                        pass
                version_verse_maps.append(vmap)

            lines.append("| # | " + " | ".join(selected) + " |")
            lines.append("| --- | " + " | ".join("---" for _ in selected) + " |")
            for vv in sorted(all_verse_nums):
                cells = [vmap.get(vv, "") for vmap in version_verse_maps]
                lines.append(f"| {vv} | " + " | ".join(cells) + " |")

        await download_docx("\n".join(lines))

    def additional_items():
        ui.button(get_translation('Go'), on_click=go_to_selected)
        ui.switch(
            get_translation("Verse-by-Verse"),
            on_change=lambda _: render_table(),
        ).bind_value(app.storage.user, 'compare_chapter_verse_by_verse')
        ui.switch(
            get_translation("Diff"),
            on_change=lambda _: render_table(),
        ).bind_value(app.storage.user, 'compare_chapter_diff') \
         .bind_visibility_from(app.storage.user, 'compare_chapter_verse_by_verse')
        ui.button("📥 DOCX", on_click=export_docx).props('outline dense')

    bible_selector.create_ui(
        active_bible if active_bible in available_versions else available_versions[0],
        state['b'],
        state['c'],
        state['v'],
        additional_items=additional_items,
        show_versions=False,
        show_verses=False,
    )

    with ui.row().classes('w-full items-center px-2 py-1'):
        versions_select = ui.select(
            available_versions,
            value=initial_versions,
            multiple=True,
            with_input=True,
            on_change=lambda _: render_table(),
        ).classes('w-full').props('use-chips outlined dense clearable')

    dummy_label = ui.label().style('position: absolute; width: 0; height: 0; overflow: hidden;')
    table_container = ui.column().classes('w-full')

    def render_table():
        table_container.clear()
        selected = [ver for ver in (versions_select.value or []) if ver in available_versions]
        cur_b, cur_c, cur_v = state['b'], state['c'], state['v']
        dark_mode = bool(app.storage.user.get('dark_mode', False))
        verse_by_verse = bool(app.storage.user.get('compare_chapter_verse_by_verse', False))
        show_diff = bool(app.storage.user.get('compare_chapter_diff', False))

        border_color = '#374151' if dark_mode else '#e5e7eb'
        header_bg = '#1f2937' if dark_mode else '#f3f4f6'
        cell_bg = '#111827' if dark_mode else '#ffffff'
        hover_bg = 'rgba(255, 255, 255, 0.04)' if dark_mode else 'rgba(0, 0, 0, 0.03)'

        table_css = f"""
        <style>
            .compare-chapter-wrap {{
                width: 100%;
                overflow-x: auto;
            }}
            .compare-chapter-table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}
            .compare-chapter-table th,
            .compare-chapter-table td {{
                border: 1px solid {border_color};
                padding: 8px 10px;
                vertical-align: top;
                text-align: left;
                word-wrap: break-word;
            }}
            .compare-chapter-table thead th {{
                position: sticky;
                top: 0;
                z-index: 2;
                background-color: {header_bg};
                font-weight: 600;
            }}
            .compare-chapter-table th.verse-num-col,
            .compare-chapter-table td.verse-num-col {{
                width: 48px;
                min-width: 48px;
                max-width: 48px;
                text-align: center;
                font-weight: 600;
                position: sticky;
                left: 0;
                z-index: 1;
                background-color: {header_bg};
            }}
            .compare-chapter-table thead th.verse-num-col {{
                z-index: 3;
            }}
            .compare-chapter-table th.version-col,
            .compare-chapter-table td.version-col {{
                min-width: 240px;
            }}
            .compare-chapter-table tbody tr.verse-row:hover td:not(.verse-num-col) {{
                background-color: {hover_bg};
            }}
            .compare-chapter-table td.version-col {{
                background-color: {cell_bg};
            }}
        </style>
        """

        with table_container:
            if not selected:
                ui.label(get_translation('No verses found.')).classes('text-gray-500 p-4')
                return

            header_cells = []
            if verse_by_verse:
                header_cells.append('<th class="verse-num-col">#</th>')
            for ver in selected:
                header_cells.append(f'<th class="version-col">{html_lib.escape(ver)}</th>')
            thead_html = f"<thead><tr>{''.join(header_cells)}</tr></thead>"

            body_rows = []
            if not verse_by_verse:
                row_cells = []
                for ver in selected:
                    db_path = getBiblePath(ver)
                    raw_html = getBibleChapter(db_path, cur_b, cur_c) if db_path else ""
                    processed = _process_bible_html(raw_html, ver, cur_b, cur_c, area=area, dark_mode=dark_mode)
                    row_cells.append(f'<td class="version-col bible-text">{processed}</td>')
                body_rows.append(f"<tr>{''.join(row_cells)}</tr>")
            else:
                version_verse_maps = []
                all_verse_nums = set()
                for ver in selected:
                    db_path = getBiblePath(ver)
                    vmap = {}
                    if db_path:
                        try:
                            for vb, vc, vv, vtext in getBibleChapterVerses(db_path, cur_b, cur_c):
                                vmap[vv] = (vb, vc, vv, vtext)
                                all_verse_nums.add(vv)
                        except Exception:
                            pass
                    version_verse_maps.append(vmap)

                for vv in sorted(all_verse_nums):
                    row_cells = [f'<td id="v{cur_b}.{cur_c}.{vv}" class="verse-num-col">{vv}</td>']
                    base_raw = ""
                    for idx, ver in enumerate(selected):
                        verse_tuple = version_verse_maps[idx].get(vv)
                        if verse_tuple is None:
                            row_cells.append('<td class="version-col bible-text"></td>')
                            continue
                        _, _, _, vtext = verse_tuple
                        if idx == 0:
                            base_raw = vtext
                        if show_diff and idx > 0 and base_raw:
                            cell_html = _word_diff_html(base_raw, vtext)
                            cell_html = apply_verse_highlights_html(
                                cell_html,
                                cur_b,
                                cur_c,
                                highlights=app.storage.user.get('verse_highlights'),
                                dark_mode=dark_mode,
                            )
                        else:
                            formatted = formatHTMLverse(verse_tuple)
                            cell_html = _process_bible_html(formatted, ver, cur_b, cur_c, area=area, dark_mode=dark_mode)
                        row_cells.append(f'<td class="version-col bible-text">{cell_html}</td>')
                    body_rows.append(f'<tr class="verse-row">{"".join(row_cells)}</tr>')

            full_html = (
                f'{table_css}'
                f'<div class="compare-chapter-wrap">'
                f'<table class="compare-chapter-table">{thead_html}<tbody>{"".join(body_rows)}</tbody></table>'
                f'</div>'
            )
            ui.html(full_html, sanitize=False).classes('w-full')

            with ui.row().classes('w-full justify-center pb-[70vh] pt-4'):
                ui.button(f'◀️ {get_translation("Prev Chapter")}', on_click=previous_chapter)
                ui.button(f'{get_translation("Next Chapter")} ▶️', on_click=next_chapter)

        if cur_v and cur_v > 1:
            ui.run_javascript(f'scrollToVerse("v{cur_b}.{cur_c}.{cur_v}")')

    render_table()

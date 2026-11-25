from nicegui import ui, app
from biblemateweb import (
    BIBLEMATEWEB_DATA,
    build_xlsx_table,
    config,
    download_docx,
    download_txt,
    download_xlsx,
    getBibleVersionList,
    get_translation,
    html_to_plain_text,
)
from typing import List, Optional
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
import re, apsw, os, html as html_lib
from biblemate.api.bible import BibleVectorDatabase


def regexp(expr, item):
    reg = re.compile(expr, flags=0 if app.storage.user['search_case_sensitivity'] else re.IGNORECASE)
    return reg.search(item) is not None

def regexp_api(expr, item):
    reg = re.compile(expr, flags=re.IGNORECASE)
    return reg.search(item) is not None

def get_bible_content(user_input="", bible="NET", sql_query="", refs=[], search_mode=1, top_similar_verses=20, search_case_sensitivity=False, api=False, parser=None, html=True, book_counts: Optional[dict] = None, chapter_counts: Optional[dict] = None) -> list:
    verses_limit_reached = False
    dbs = []
    if isinstance(bible, str): # str; single bible
        if bible_path := getBiblePath(bible):
            dbs = [bible_path]
    else: # list; multiple bibles
        dbs = []
        for i in bible:
            if i_path := getBiblePath(i):
                if not i_path in dbs:
                    dbs.append(i_path)
    if not dbs:
        return []
    if parser is None:
        parser = BibleVerseParser(False)
    results = []
    if not refs and re.search(" [0-9]+?[:：][0-9]", user_input):
        refs = parser.extractAllReferences(user_input, tagged=(True if '<ref onclick="bcv(' in user_input else False))
    if not refs and search_mode == 3: # semantic search
        vector_db = BibleVectorDatabase(os.path.join(BIBLEMATEWEB_DATA, "vectors", "bible.db"))
        query = sql_query if sql_query else "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"
        if books := re.search("Book IN (.*?) AND ", query):
            book=books.group(1)
        elif books := re.search("Book=([0-9]+?) AND ", query):
            book=f"({books.group(1)})"
        else:
            book=0
        refs = [(b, c, v) for b, c, v, _ in vector_db.search_meaning(user_input, top_k=top_similar_verses, book=book)]
    if refs:
        distinct_refs = []
        for ref in refs:
            if ref not in distinct_refs:
                distinct_refs.append(ref)
        refs = distinct_refs
        if book_counts is not None or chapter_counts is not None:
            for ref in refs:
                b = ref[0]
                if book_counts is not None:
                    book_counts[b] = book_counts.get(b, 0) + len(dbs)
                if chapter_counts is not None:
                    key = (b, ref[1])
                    chapter_counts[key] = chapter_counts.get(key, 0) + len(dbs)
        if len(refs) > config.verses_limit:
            refs = refs[:config.verses_limit]
            verses_limit_reached = True
        query = "SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse =?"
        for db in dbs:
            this_bible = os.path.basename(db)[:-6]
            with apsw.Connection(db) as connn:
                cursor = connn.cursor()
                for ref in refs:
                    if len(ref) == 5:
                        content = ""
                        b1, c1, v1 = 1, 1, 1
                        for r in parser.extractExhaustiveReferences([ref]):
                            b, c, v = r
                            if not content:
                                b1, c1, v1 = r
                            cursor.execute(query, (b, c, v))
                            verse = cursor.fetchone()
                            if not verse: continue
                            verse_text = verse[0].strip()
                            if not html:
                                verse_text = re.sub("<.*?>", "", verse_text)
                            content += f"<vid>{v}</vid> {verse_text} "
                        ref = parser.bcvToVerseReference(*ref)
                        if len(dbs) > 1:
                            ref += f" [{this_bible}]"
                        results.append({'ref': ref, 'content': content.rstrip(), 'bible': this_bible, 'b': b1, 'c': c1, 'v': v1})
                    else:
                        b, c, v = ref
                        cursor.execute(query, (b, c, v))
                        verse = cursor.fetchone()
                        if not verse: continue
                        verse_text = verse[0].strip()
                        if not html:
                            verse_text = re.sub("<.*?>", "", verse_text)
                        ref = parser.bcvToVerseReference(b, c, v)
                        if len(dbs) > 1:
                            ref += f" [{this_bible}]"
                        results.append({'ref': ref, 'content': verse_text, 'bible': this_bible, 'b': b, 'c': c, 'v': v})
    else:
        # search the bible with regular expression
        query = sql_query if sql_query else "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"
        if search_case_sensitivity:
            query = query.replace("case_sensitive_like = false;", "case_sensitive_like = true;")
        if search_mode == 1:
            query = query.replace("Scripture REGEXP", "Scripture LIKE")
            user_input = "%"+user_input+"%"
        for db in dbs:
            this_bible = os.path.basename(db)[:-6]
            with apsw.Connection(db) as connn:
                connn.createscalarfunction("REGEXP", regexp_api if api else regexp)
                cursor = connn.cursor()
                cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='VersesPlain' LIMIT 1")
                has_verses_plain = cursor.fetchone() is not None
                db_query = re.sub(r"\bFROM\s+Verses\b", "FROM VersesPlain", query, count=1) if has_verses_plain else query
                cursor.execute(db_query, (user_input,))
                fetches = cursor.fetchall()
                if book_counts is not None or chapter_counts is not None:
                    for verse in fetches:
                        b = verse[0]
                        if book_counts is not None:
                            book_counts[b] = book_counts.get(b, 0) + 1
                        if chapter_counts is not None:
                            key = (b, verse[1])
                            chapter_counts[key] = chapter_counts.get(key, 0) + 1
                if fetches and len(fetches) > config.verses_limit:
                    fetches = fetches[:config.verses_limit]
                    verses_limit_reached = True
                for verse in fetches:
                    if has_verses_plain:
                        cursor.execute("SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse=?", (verse[0], verse[1], verse[2]))
                        row = cursor.fetchone()
                        verse_text = row[0].strip() if row else verse[3].strip()
                    else:
                        verse_text = verse[3].strip()
                    if not html:
                        verse_text = re.sub("<.*?>", "", verse_text)
                    ref = parser.bcvToVerseReference(verse[0], verse[1], verse[2])
                    if len(dbs) > 1:
                        ref += f" [{this_bible}]"
                    results.append({'ref': ref, 'content': verse_text, 'bible': this_bible, 'b': verse[0], 'c': verse[1], 'v': verse[2]})
    if verses_limit_reached:
        results.append({'ref': "", 'content': f"{config.verses_limit} verses limit reached!", 'bible': "", 'b': 0, 'c': 0, 'v': 0})
    return results

# Bible Selection

def getBiblePath(bible) -> str:
    if bible in ["ORB", "OPB", "ODB", "OLB", "BHS5", "OGNT"]:
        bible = "OHGB"
    elif bible == "OIB":
        bible = "OHGBi"
    return config.bibles_custom[bible][-1] if bible in config.bibles_custom else config.bibles[bible][-1] if bible in config.bibles else ""

def getBibleChapter(db, b, c) -> str: # html output
    query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
    content = ""
    try:
        with apsw.Connection(db) as connn:
            #connn.createscalarfunction("REGEXP", regexp)
            cursor = connn.cursor()
            cursor.execute(query, (b, c))
            if scripture := cursor.fetchone():
                content = scripture[0]
    except:
        try:
            verses = [formatHTMLverse(i) for i in getBibleChapterVerses(db, b, c)]
            content = "<br>".join(verses)
        except Exception as e:
            content = "Error: "+str(e)
    return content

def formatHTMLverse(verse) -> str:
    b, c, v, text = verse
    return f"""<verse><vid id="v{b}.{c}.{v}" onclick="luV({v})">{v}</vid> {text}</verse>"""

def getBibleChapterVerses(db, b, c) -> str:
    query = "SELECT * FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
    verses = []
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        verses = cursor.fetchall()
    return verses

def getBibleBookList(db) -> list:
    query = "SELECT DISTINCT Book FROM Verses ORDER BY Book"
    bookList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query)
        bookList = sorted([book[0] for book in cursor.fetchall() if book[0]])
    return bookList

def getBibleChapterList(db, b) -> list:
    query = "SELECT DISTINCT Chapter FROM Verses WHERE Book=? ORDER BY Chapter"
    chapterList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query, (b,))
        chapterList = sorted([chapter[0] for chapter in cursor.fetchall()])
    return chapterList

def getBibleVerseList(db, b, c) -> list:
    query = "SELECT DISTINCT Verse FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
    verseList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        verseList = sorted([verse[0] for verse in cursor.fetchall()])
    return verseList

def change_bible_chapter_verse(_, book, chapter, verse):
    ui.run_javascript(f'scrollToVerse("v{book}.{chapter}.{verse}")')

class BibleSelector:
    """Class to manage Bible verse selection with dynamic dropdowns"""
    
    def __init__(self, on_version_changed=None, on_book_changed=None, on_chapter_changed=None, on_verse_changed=None, version_options=[], chapter_zero=False, verse_zero=False):
        # Handlers that replace the default on_change functions
        self.on_version_changed, self.on_book_changed, self.on_chapter_changed, self.on_verse_changed = on_version_changed, on_book_changed, on_chapter_changed, on_verse_changed

        # Initialize selected values
        self.selected_version: Optional[str] = None
        self.selected_book: Optional[str] = None
        self.selected_chapter: Optional[int] = None
        self.selected_verse: Optional[int] = None
        self.show_verses: Optional[bool] = None
        
        # Initialize dropdown UI elements
        self.version_select: Optional[ui.select] = None
        self.book_select: Optional[ui.select] = None
        self.chapter_select: Optional[ui.select] = None
        self.verse_select: Optional[ui.select] = None
        
        # Initialize options
        self.version_options: List[str] = version_options
        self.book_options: List[str] = []
        self.chapter_options: List[int] = []
        self.verse_options: List[int] = []

        self.chapter_zero, self.verse_zero = chapter_zero, verse_zero
        
    def create_ui(self, bible, b, c, v, additional_items=None, show_versions=True, show_chapters=True, show_verses=True):
        self.selected_version = bible
        self.selected_book = b
        self.selected_chapter = c
        self.selected_verse = v
        self.show_chapters = show_chapters
        self.show_verses = show_verses

        if not self.version_options:
            self.version_options = getBibleVersionList(app.storage.client["custom"])
        bible_book_list = getBibleBookList(getBiblePath(self.selected_version))
        self.book_options = [BibleBooks.abbrev[app.storage.user['ui_language']][str(i)][0] for i in bible_book_list if str(i) in BibleBooks.abbrev[app.storage.user['ui_language']]]
        self.chapter_options = getBibleChapterList(getBiblePath(self.selected_version), self.selected_book)
        if self.chapter_zero:
            self.chapter_options.insert(0, 0)
        self.verse_options = [0] if self.chapter_zero and self.selected_chapter == 0 else getBibleVerseList(getBiblePath(self.selected_version), self.selected_book, self.selected_chapter)
        if self.verse_zero and not (self.chapter_zero and self.selected_chapter == 0):
            self.verse_options.insert(0, 0)
        try:
            default_book = BibleBooks.abbrev[app.storage.user['ui_language']][str(self.selected_book)][0]
        except:
            self.selected_book = bible_book_list[0]
            default_book = self.book_options[0]
            self.chapter_options = getBibleChapterList(getBiblePath(self.selected_version), self.selected_book)
            if self.chapter_zero:
                self.chapter_options.insert(0, 0)
            self.verse_options = [0] if self.chapter_zero and self.selected_chapter == 0 else getBibleVerseList(getBiblePath(self.selected_version), self.selected_book, self.selected_chapter)
            if self.verse_zero and not (self.chapter_zero and self.selected_chapter == 0):
                self.verse_options.insert(0, 0)
        with ui.row().classes('w-full justify-center items-center'):
            # Versions
            if show_versions:
                self.version_select = ui.select(
                    options=self.version_options,
                    #label='Bible',
                    value=bible if bible in self.version_options else self.version_options[0],
                    on_change=self.on_version_change
                )
            # Book
            self.book_select = ui.select(
                options=self.book_options,
                #label='Book',
                value=default_book if default_book in self.book_options else self.book_options[0], # b
                on_change=self.on_book_change
            )
            # Chapter
            if show_chapters:
                self.chapter_select = ui.select(
                    options=self.chapter_options,
                    #label='Chapter',
                    value=c if c in self.chapter_options else self.chapter_options[0],
                    on_change=self.on_chapter_change
                )
            # Verse
            if show_verses:
                self.verse_select = ui.select(
                    options=self.verse_options,
                    #label='Verse',
                    value=v if v in self.verse_options else self.verse_options[0],
                    on_change=self.on_verse_change
                )
            if additional_items:
                additional_items()
    
    def on_version_change(self, e):
        """Handle Bible version selection change"""
        self.selected_version = e.value

        # replace default action
        if self.on_version_changed is not None:
            return self.on_version_changed(self.selected_version)
        
        self.reset_book_dropdown()
        self.reset_chapter_dropdown()
        self.reset_verse_dropdown()
    
    def on_book_change(self, e):
        """Handle book selection change"""
        self.selected_book = BibleBooks.bookNameToNum(e.value)

        # replace default action
        if self.on_book_changed is not None:
            return self.on_book_changed(self.selected_version, self.selected_book)

        self.reset_chapter_dropdown()
        self.reset_verse_dropdown()
    
    def on_chapter_change(self, e):
        """Handle chapter selection change"""
        self.selected_chapter = e.value

        # replace default action
        if self.on_chapter_changed is not None:
            return self.on_chapter_changed(self.selected_version, self.selected_book, self.selected_chapter)

        # Reset verse dropdown
        self.reset_verse_dropdown()
    
    def on_verse_change(self, e):
        """Handle verse selection change"""
        self.selected_verse = e.value

        # replace default action
        if self.on_verse_changed is not None:
            return self.on_verse_changed(self.selected_version, self.selected_book, self.selected_chapter, self.selected_verse)

    def reset_book_dropdown(self):
        """Reset book dropdown to initial state"""
        book_list = getBibleBookList(getBiblePath(self.selected_version))
        self.book_options = [BibleBooks.abbrev[app.storage.user['ui_language']][str(i)][0] for i in book_list if str(i) in BibleBooks.abbrev[app.storage.user['ui_language']]]
        self.book_select.options = self.book_options
        self.book_select.value = self.book_options[0]
        self.selected_book = book_list[0]
        # refresh
        self.book_select.update()
    
    def reset_chapter_dropdown(self):
        """Reset chapter dropdown to initial state"""
        if not getattr(self, 'show_chapters', True):
            self.selected_chapter = 1
            return
        self.chapter_options = getBibleChapterList(getBiblePath(self.selected_version), self.selected_book)
        if self.chapter_zero:
            self.chapter_options.insert(0, 0)
        self.chapter_select.options = self.chapter_options
        self.chapter_select.value = self.chapter_options[0]
        self.selected_chapter = self.chapter_options[0]
        # refresh
        self.chapter_select.update()
    
    def reset_verse_dropdown(self):
        """Reset verse dropdown to initial state"""
        if not self.show_verses:
            return
        self.verse_options = [0] if self.chapter_zero and self.selected_chapter == 0 else getBibleVerseList(getBiblePath(self.selected_version), self.selected_book, self.selected_chapter)
        if self.verse_zero and not (self.chapter_zero and self.selected_chapter == 0):
            self.verse_options.insert(0, 0)
        self.verse_select.options = self.verse_options
        self.verse_select.value = self.verse_options[0]
        self.selected_verse = self.verse_options[0]
        # refresh
        self.verse_select.update()
    
    def get_selection(self):
        """Get the current selection and display it"""
        return (self.selected_version, self.selected_book, self.selected_chapter, self.selected_verse)


def _load_plain_verse_cache(verses):
    """Load VersesPlain text per Bible DB for the books referenced in verses."""
    plain_cache = {}
    by_bible = {}
    for item in verses:
        if item.get('bible') and item.get('b'):
            by_bible.setdefault(item['bible'], set()).add(item['b'])

    for bible_ver, books in by_bible.items():
        db_path = getBiblePath(bible_ver)
        if not db_path:
            continue
        try:
            with apsw.Connection(db_path) as connn:
                cur = connn.cursor()
                has_plain = cur.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='VersesPlain' LIMIT 1"
                ).fetchone()
                if not has_plain:
                    continue
                placeholders = ",".join("?" for _ in books)
                cur.execute(
                    f"SELECT Book, Chapter, Verse, Scripture FROM VersesPlain WHERE Book IN ({placeholders})",
                    list(books),
                )
                plain_cache[bible_ver] = {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}
        except Exception:
            pass
    return plain_cache, by_bible


def _clean_verse_item_text(item, plain_cache):
    """Extract plain verse text for an item, preferring VersesPlain when cached."""
    bible_ver = item.get('bible', '')
    plain_map = plain_cache.get(bible_ver)
    if plain_map is not None and (item['b'], item['c'], item['v']) in plain_map:
        text = plain_map[(item['b'], item['c'], item['v'])]
    else:
        text = item.get('content', '')
    return re.sub(r"<[^<>]+?>", "", str(text)).strip()


def _group_verses_for_table(verses, plain_cache):
    """Group verse items by (b, c, v) into ordered versions, references, and text map."""
    versions = []
    grouped = {}
    ref_map = {}
    for item in verses:
        ver = item.get('bible', '')
        if ver and ver not in versions:
            versions.append(ver)
        coord = (item.get('b'), item.get('c'), item.get('v'))
        if coord not in grouped:
            grouped[coord] = {}
            ref_map[coord] = item.get('ref', '')
        grouped[coord][ver] = _clean_verse_item_text(item, plain_cache)
    return versions, grouped, ref_map


def build_export_verses_text(verses, markdown_table: bool = False):
    """Format verse dicts for export, preferring VersesPlain when present in the .bible DB."""
    plain_cache, by_bible = _load_plain_verse_cache(verses)

    if markdown_table:
        versions, grouped, ref_map = _group_verses_for_table(verses, plain_cache)
        header = "| Reference | " + " | ".join(versions) + " |"
        sep = "| --- | " + " | ".join("---" for _ in versions) + " |"
        rows = [header, sep]
        for coord, ver_texts in grouped.items():
            cells = [ver_texts.get(ver, "").replace("|", "\\|").replace("\n", " ") for ver in versions]
            rows.append(f"| {ref_map[coord]} | " + " | ".join(cells) + " |")
        return "\n".join(rows)

    multi_bible = len(by_bible) > 1
    lines = []
    for item in verses:
        bible_ver = item.get('bible', '')
        clean_text = _clean_verse_item_text(item, plain_cache)
        prefix = f"[{item['ref']} {bible_ver}]" if multi_bible and bible_ver else f"[{item['ref']}]"
        lines.append(f"{prefix} {clean_text}")
    return "\n\n".join(lines)


def build_export_verses_xlsx(verses) -> bytes:
    """Build an .xlsx Excel workbook comparing verses across Bible versions."""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter

    plain_cache, _ = _load_plain_verse_cache(verses)
    versions, grouped, ref_map = _group_verses_for_table(verses, plain_cache)

    wb = Workbook()
    ws = wb.active
    ws.title = "Verses"

    headers = ["Reference", *versions]
    ws.append(headers)
    header_font = Font(bold=True)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.alignment = Alignment(vertical="top")

    wrap_align = Alignment(wrap_text=True, vertical="top")
    for coord, ver_texts in grouped.items():
        row = [ref_map[coord], *[ver_texts.get(ver, "") for ver in versions]]
        ws.append(row)
        row_idx = ws.max_row
        for col_idx in range(1, len(headers) + 1):
            ws.cell(row=row_idx, column=col_idx).alignment = wrap_align

    ws.freeze_panes = "A2"
    ws.column_dimensions["A"].width = 18
    for col_idx in range(2, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 50

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _clean_bible_verse_text(text: str) -> str:
    plain = re.sub(r"<[^<>]+?>", " ", text or "")
    plain = html_lib.unescape(plain)
    return re.sub(r"\s+", " ", plain).strip()


def chapter_html_to_markdown(chapter_html: str) -> str:
    """Convert Bible-table chapter HTML into Markdown preserving headings, paragraphs, and verse numbers."""
    if not chapter_html:
        return ""
    md = chapter_html
    md = re.sub(r"<script.*?>.*?</script>", "", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"<style.*?>.*?</style>", "", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"<vid\b[^>]*>(.*?)</vid>", r"**\1**", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"<h[1-6][^>]*>(.*?)</h[1-6]>", lambda m: f"\n\n## {re.sub(r'<[^<>]+?>', '', m.group(1)).strip()}\n\n", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"<u>\s*<b>(.*?)</b>\s*</u>", lambda m: f"\n\n### {re.sub(r'<[^<>]+?>', '', m.group(1)).strip()}\n\n", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"<(?:b|strong)\b[^>]*>(.*?)</(?:b|strong)>", r"**\1**", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"<(?:i|em)\b[^>]*>(.*?)</(?:i|em)>", r"*\1*", md, flags=re.DOTALL | re.IGNORECASE)
    md = re.sub(r"(?:<br\s*/?>\s*){2,}", "\n\n", md, flags=re.IGNORECASE)
    md = re.sub(r"<br\s*/?>", "\n", md, flags=re.IGNORECASE)
    md = re.sub(r"</(?:p|div|blockquote|li|tr)>", "\n\n", md, flags=re.IGNORECASE)
    md = re.sub(r"<p\b[^>]*>", "\n\n", md, flags=re.IGNORECASE)
    md = re.sub(r"<[^<>]+?>", "", md)
    md = html_lib.unescape(md)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in md.splitlines()]
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def build_export_chapter_xlsx(db: str, b: int, c: int, bible_name: str = "", lang: str = "eng") -> bytes:
    """Build a verse-by-verse .xlsx workbook for a Bible chapter."""
    chapter_ref = BibleVerseParser(False, language=lang).bcvToVerseReference(b, c, 1, isChapter=True)
    verses = getBibleChapterVerses(db, b, c) if db else []
    headers = ["Reference", bible_name or "Scripture"]
    rows = [[f"{chapter_ref}:{vv}", _clean_bible_verse_text(vtext)] for _, _, vv, vtext in verses]
    return build_xlsx_table(headers, rows, sheet_name=chapter_ref, widths=[18, 70])


def _get_bible_table_chapter(db: str, b: int, c: int) -> str:
    """Return raw Scripture HTML from the Bible table if present, else empty string."""
    if not db:
        return ""
    try:
        with apsw.Connection(db) as connn:
            cursor = connn.cursor()
            cursor.execute("SELECT Scripture FROM Bible WHERE Book=? AND Chapter=? LIMIT 1", (b, c))
            row = cursor.fetchone()
            return row[0] if row and row[0] else ""
    except Exception:
        return ""


def build_export_chapter_docx_md(db: str, b: int, c: int, bible_name: str = "", lang: str = "eng", fallback_html: str = "") -> str:
    """Build Markdown for chapter DOCX export, preferring the Bible table and falling back to Verses."""
    chapter_ref = BibleVerseParser(False, language=lang).bcvToVerseReference(b, c, 1, isChapter=True)
    chapter_html = _get_bible_table_chapter(db, b, c)
    if chapter_html:
        body = chapter_html_to_markdown(chapter_html)
        return f"# {chapter_ref} ({bible_name})\n\n{body}"
    verses = getBibleChapterVerses(db, b, c) if db else []
    if verses:
        body = "\n\n".join(f"**{vv}** {_clean_bible_verse_text(vtext)}" for _, _, vv, vtext in verses)
        return f"# {chapter_ref} ({bible_name})\n\n{body}"
    return html_to_plain_text(fallback_html)


def add_chapter_export_menu_items(get_selection, db: str, fallback_html: str = ""):
    """Add DOCX, Table (verse-by-verse Excel), and TXT chapter export items to a Bible page menu."""
    async def _export(fmt: str):
        sel_ver, cur_b, cur_c, _ = get_selection()
        bible_name = sel_ver or (os.path.basename(db)[:-6] if db else "")
        lang = app.storage.user.get('ui_language', 'eng')
        chapter_ref = BibleVerseParser(False, language=lang).bcvToVerseReference(cur_b, cur_c, 1, isChapter=True)
        if fmt == 'xlsx':
            verses = getBibleChapterVerses(db, cur_b, cur_c) if db else []
            if not verses:
                ui.notify(get_translation("Nothing to download"), type='warning')
                return
            await download_xlsx(build_export_chapter_xlsx(db, cur_b, cur_c, bible_name, lang=lang))
        elif fmt == 'docx':
            md = build_export_chapter_docx_md(db, cur_b, cur_c, bible_name, lang=lang, fallback_html=fallback_html)
            await download_docx(md)
        else:
            verses = getBibleChapterVerses(db, cur_b, cur_c) if db else []
            if verses:
                body = "\n".join(f"[{vv}] {_clean_bible_verse_text(vtext)}" for _, _, vv, vtext in verses)
                txt = f"# {chapter_ref} ({bible_name})\n\n{body}"
            else:
                txt = html_to_plain_text(fallback_html)
            await download_txt(txt)

    ui.separator()
    ui.menu_item(f'📄 {get_translation("Export")} DOCX', on_click=lambda: _export('docx'))
    ui.menu_item(f'📊 {get_translation("Export Table")}', on_click=lambda: _export('xlsx'))
    ui.menu_item(f'📥 {get_translation("Export")} TXT', on_click=lambda: _export('txt'))

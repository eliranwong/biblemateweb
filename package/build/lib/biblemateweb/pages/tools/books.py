import re
import apsw
from nicegui import ui, app
from biblemateweb import discover_books, get_translation
from biblemateweb.data.cr_books import cr_books

_READONLY = apsw.SQLITE_OPEN_READONLY
_SCRIPT_RE = re.compile(r"(?is)<script\b[^>]*>.*?</script>")
_BODY_RE = re.compile(r"(?is)<body[^>]*>(.*)</body>")
_STYLE_RE = re.compile(r"(?is)<style\b[^>]*>.*?</style>")
_CLICK_DQ = re.compile(r'''(onclick|ondblclick)="(bdbid|bdbeid|bdagid|halotid|chalotid|lsjid|lex|cr|bcv|website|promise|harmony)\((.*?)\)"''')
_CLICK_SQ = re.compile(r"""(onclick|ondblclick)='(bdbid|bdbeid|bdagid|halotid|chalotid|lsjid|lex|cr|bcv|website|promise|harmony)\((.*?)\)'""")
_STRAY_DQ = re.compile(r'''\son\w+="(?!emitEvent)[^"]*"''')
_STRAY_SQ = re.compile(r"""\son\w+='(?!emitEvent)[^']*'""")
_JS_URL = re.compile(r'''(?i)\s(?:href|src)\s*=\s*(['"])\s*javascript:[^'"]*\1''')


def read_book_chapters(path: str):
    """Return [(rowid, title), ...] in stored order."""
    with apsw.Connection(path, flags=_READONLY) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT rowid, Chapter FROM Reference ORDER BY rowid")
        return [(row[0], row[1] if row[1] else "") for row in cursor.fetchall()]


def read_book_chapter(path: str, row_id: int) -> str:
    with apsw.Connection(path, flags=_READONLY) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT Content FROM Reference WHERE rowid=? LIMIT 1", (int(row_id),))
        row = cursor.fetchone()
    return row[0] if row and row[0] else ""


def prepare_book_html(content: str, dark: bool = False) -> str:
    """Turn stored chapter HTML into a fragment that can sit in the reader."""
    if not content:
        return ""
    if isinstance(content, bytes):
        content = content.decode("utf-8", "replace")
    content = _SCRIPT_RE.sub("", content)
    styles = "".join(_STYLE_RE.findall(content))
    body = _BODY_RE.search(content)
    if body:
        content = styles + body.group(1)
    content = _CLICK_DQ.sub(r'''\1="emitEvent('\2', [\3]); return false;"''', content)
    content = _CLICK_SQ.sub(r"""\1='emitEvent("\2", [\3]); return false;'""", content)
    content = _STRAY_DQ.sub("", content)
    content = _STRAY_SQ.sub("", content)
    content = _JS_URL.sub("", content)
    content = content.replace("<font color='3'>", "<font color='pink'>" if dark else "<font color='brown'>")
    content = content.replace("<font color='4'>", "<font color='lightskyblue'>" if dark else "<font color='navy'>")
    if dark:
        content = content.replace('color="brown">', 'color="pink">')
        content = content.replace('color="navy">', 'color="lightskyblue">')
        content = content.replace('<table bgcolor="#BFBFBF"', '<table bgcolor="#424242"')
        content = content.replace('<td bgcolor="#FFFFFF">', '<td bgcolor="#212121">')
        content = content.replace('<tr bgcolor="#FFFFFF">', '<tr bgcolor="#212121">')
        content = content.replace('<tr bgcolor="#DFDFDF">', '<tr bgcolor="#303030">')
    return content


def bible_books(gui=None, q="", **_):
    """Reference-book reader. Book and chapter menus rescan on each open."""
    custom = bool(app.storage.client["custom"])
    scan_timer = {"timer": None}
    state = {
        "books": {},
        "chapters": [],
        "ignore": False,
        "book": "",
    }

    if gui:
        tab = gui.get_active_area2_tab()
        panel = gui.area2_tab_panels.get(tab)
        if panel is not None:
            panel.classes(add="book-fill")

    def bcv(event):
        if not gui:
            return
        book, chapter, verse, *_ = event.args
        gui.change_area_1_bible_chapter(None, book, chapter, verse)

    def cr(event):
        if not gui:
            return
        book, chapter, verse, *_ = event.args
        book = cr_books.get(book, book)
        gui.change_area_1_bible_chapter(None, book, chapter, verse)

    def website(event):
        url, *_ = event.args
        if url:
            ui.navigate.to(str(url), new_tab=True)

    def lex(event):
        if not gui:
            return
        word, *_ = event.args
        app.storage.user["tool_query"] = str(word)
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title="Lexicons", sync=False)

    def promise(event):
        if not gui:
            return
        tool, number = event.args
        app.storage.user["tool_query"] = f"{tool}.{number}"
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title="Promises")

    def harmony(event):
        if not gui:
            return
        tool, number = event.args
        app.storage.user["tool_query"] = f"{tool}.{number}"
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title="Parallels")

    ui.on("bcv", bcv)
    ui.on("cr", cr)
    ui.on("website", website)
    for event_name in ("bdbid", "bdbeid", "bdagid", "halotid", "chalotid", "lsjid"):
        ui.on(event_name, lex)
    ui.on("lex", lex)
    ui.on("promise", promise)
    ui.on("harmony", harmony)

    def remember(book_name, chapter_title):
        if book_name:
            app.storage.user["favorite_book"] = book_name
        if gui and book_name:
            query = f"{book_name}:::{chapter_title}" if chapter_title else book_name
            gui.update_active_area2_tab_records(q=query)

    def chapter_title(row_id):
        key = str(row_id) if row_id is not None else ""
        for stored_id, title in state["chapters"]:
            if str(stored_id) == key:
                return title
        return ""

    def show_message(message):
        content_container.clear()
        with content_container:
            ui.html(f'<div class="content-text book-reader">{message}</div>', sanitize=False)

    def render_chapter(path, row_id):
        try:
            raw = read_book_chapter(path, row_id)
        except Exception:
            ui.notify(get_translation("Unable to read this book."), type="negative")
            show_message("")
            return
        html = prepare_book_html(raw, dark=bool(app.storage.user.get("dark_mode")))
        content_container.clear()
        with content_container:
            ui.html(f'<div class="content-text book-reader">{html}</div>', sanitize=False)
        if gui:
            tab = gui.get_active_area2_tab()
            panel = gui.area2_tab_panels.get(tab)
            if panel is not None:
                try:
                    reader_scroll.scroll_to(percent=0)
                except Exception:
                    pass

    def update_nav():
        ids = [str(row_id) for row_id, _title in state["chapters"]]
        current = "" if chapter_select.value is None else str(chapter_select.value)
        index = ids.index(current) if current in ids else -1
        has_chapters = bool(ids)
        chapter_select.set_visibility(has_chapters)
        prev_btn.set_visibility(has_chapters)
        next_btn.set_visibility(has_chapters)
        if index > 0:
            prev_btn.enable()
        else:
            prev_btn.disable()
        if 0 <= index < len(ids) - 1:
            next_btn.enable()
        else:
            next_btn.disable()

    def load_chapters(path, preferred_title="", preferred_id=None):
        try:
            rows = read_book_chapters(path)
        except Exception:
            ui.notify(get_translation("Unable to read this book."), type="negative")
            rows = []
        state["chapters"] = rows
        options = {str(row_id): title or "—" for row_id, title in rows}
        chosen = None
        if preferred_id is not None and str(preferred_id) in options:
            chosen = str(preferred_id)
        elif preferred_title:
            for row_id, title in rows:
                if title == preferred_title:
                    chosen = str(row_id)
                    break
        if chosen is None and rows:
            chosen = str(rows[0][0])
        state["ignore"] = True
        chapter_select.options = options
        chapter_select.value = chosen
        chapter_select.update()
        state["ignore"] = False
        update_nav()
        return chosen

    def refresh_books(_=None):
        """Rescan book files so the menu matches the folders right now."""
        if getattr(book_select, "_deleted", False):
            if scan_timer["timer"] is not None:
                scan_timer["timer"].cancel()
            return
        books = discover_books(custom)
        state["books"] = books
        names = list(books)
        current = state["book"] if state["book"] in books else None
        if book_select.value in books:
            current = book_select.value
        previous_names = list(book_select.options or [])
        if previous_names != names or book_select.value != current:
            state["ignore"] = True
            book_select.options = names
            book_select.value = current
            book_select.update()
            state["ignore"] = False
        if state["book"] and state["book"] not in books:
            state["book"] = ""
            state["chapters"] = []
            state["ignore"] = True
            chapter_select.options = {}
            chapter_select.value = None
            chapter_select.update()
            state["ignore"] = False
            update_nav()
            show_message(get_translation("No books found.") if not books else "")
        return books

    def refresh_chapters(_=None):
        """Rescan the open book's chapter list."""
        book_name = state["book"]
        path = state["books"].get(book_name, "")
        if not path:
            return
        previous = chapter_select.value
        title = chapter_title(previous)
        chosen = load_chapters(path, title, preferred_id=previous)
        if chosen and str(chosen) != ("" if previous is None else str(previous)):
            render_chapter(path, chosen)

    def open_book(book_name, preferred_title="", persist=True):
        books = state["books"] or discover_books(custom)
        state["books"] = books
        if book_name not in books:
            state["book"] = ""
            show_message(get_translation("No books found.") if not books else "")
            update_nav()
            return
        state["book"] = book_name
        state["ignore"] = True
        book_select.options = list(books)
        book_select.value = book_name
        book_select.update()
        state["ignore"] = False
        chosen = load_chapters(books[book_name], preferred_title)
        if chosen is None:
            show_message("")
            return
        render_chapter(books[book_name], chosen)
        app.storage.user["favorite_book"] = book_name
        if persist:
            remember(book_name, chapter_title(chosen))

    def on_book_change(event):
        if state["ignore"]:
            return
        book_name = event.value
        if book_name == state["book"]:
            return
        if book_name not in state["books"]:
            refresh_books()
            if book_name not in state["books"]:
                return
        open_book(book_name, "", persist=True)

    def on_chapter_change(event):
        if state["ignore"]:
            return
        book_name = state["book"]
        path = state["books"].get(book_name, "")
        row_id = event.value
        if not path or row_id is None:
            return
        render_chapter(path, row_id)
        remember(book_name, chapter_title(row_id))
        update_nav()

    def step(delta):
        ids = [str(row_id) for row_id, _title in state["chapters"]]
        current = "" if chapter_select.value is None else str(chapter_select.value)
        if current not in ids:
            return
        index = ids.index(current) + delta
        if 0 <= index < len(ids):
            chapter_select.value = ids[index]

    with ui.column().classes("book-shell w-full"):
        with ui.row().classes("book-toolbar w-full items-center no-wrap"):
            book_select = ui.select(
                options=[],
                value=None,
                with_input=True,
                label=get_translation("Books"),
            ).props("dense options-dense").classes("flex-grow min-w-0")
            chapter_select = ui.select(
                options={},
                value=None,
                with_input=True,
                label=get_translation("Chapter"),
            ).props("dense options-dense").classes("flex-grow min-w-0")
            prev_btn = ui.button(icon="chevron_left", on_click=lambda: step(-1)).props("flat dense round size=sm")
            next_btn = ui.button(icon="chevron_right", on_click=lambda: step(1)).props("flat dense round size=sm")
        reader_scroll = ui.scroll_area().classes("book-reader-scroll w-full")
        with reader_scroll:
            content_container = ui.column().classes("w-full !p-0 !m-0 !gap-0")

    book_select.on_value_change(on_book_change)
    chapter_select.on_value_change(on_chapter_change)
    # Opening the menu rescans immediately. A short timer covers books added or
    # removed while this page stays open, so the menu is current before it is opened.
    book_select.on("click", refresh_books)
    book_select.on("popup-show", refresh_books)
    chapter_select.on("popup-show", refresh_chapters)
    scan_timer["timer"] = ui.timer(2.0, refresh_books, immediate=False)
    chapter_select.set_visibility(False)
    prev_btn.set_visibility(False)
    next_btn.set_visibility(False)

    books = refresh_books()
    requested_book, requested_chapter = "", ""
    text = (q or "").strip()
    if text and ":::" in text:
        requested_book, requested_chapter = text.rsplit(":::", 1)
        requested_book, requested_chapter = requested_book.strip(), requested_chapter.strip()
    elif text:
        requested_book = text
    if requested_book and requested_book not in books:
        requested_book, requested_chapter = "", ""
    if not requested_book:
        favorite = app.storage.user.get("favorite_book", "")
        if favorite in books and not text:
            requested_book = favorite
    if requested_book:
        open_book(requested_book, requested_chapter, persist=False)
    elif not books:
        show_message(get_translation("No books found."))

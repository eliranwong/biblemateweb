from nicegui import ui, app
from biblemategui import config
from typing import List, Dict, Optional
import re, apsw


def luV(event):
    b, c, v = event.args
    ui.notify(f"b: {b}, c: {c}, v: {v}")
    
    # Create a context menu at the click position
    with ui.context_menu() as menu:
        ui.menu_item('Bible Commentaries', on_click=lambda: ui.navigate.to('/tool/commentary'))
        ui.menu_item('Cross-references', on_click=lambda: ui.navigate.to('/tool/xref'))
        ui.menu_item('Treasury of Scripture Knowledge', on_click=lambda: ui.navigate.to('/tool/tske'))
        ui.menu_item('Discourse Analysis', on_click=lambda: ui.navigate.to('/tool/discourse'))
        ui.menu_item('Morphological Data', on_click=lambda: ui.navigate.to('/tool/morphology'))
        ui.menu_item('Translation Spectrum', on_click=lambda: ui.navigate.to('/tool/translations'))
    menu.open()

def regexp(expr, case_sensitive=False):
    reg = re.compile(expr, flags=0 if case_sensitive else re.IGNORECASE)
    return reg.search(item) is not None

# Bible Selection

def getBibleVersionList() -> List[str]:
    """Returns a list of available Bible versions"""
    return ["ORB", "OIB", "OPB", "ODB", "OLB"]+list(config.bibles.keys())+list(config.bibles_custom.keys())

def getBiblePath(bible) -> str:
    if bible in ["ORB", "OIB", "OPB", "ODB", "OLB"]:
        bible = "KJV"
    return config.bibles_custom[bible] if bible in config.bibles_custom else config.bibles[bible]

def getBibleChapter(db, b, c) -> str:
    query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
    content = ""
    with apsw.Connection(db) as connn:
        #connn.createscalarfunction("REGEXP", regexp)
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        if scripture := cursor.fetchone():
            content = scripture[0]
    return content

def getBibleBookList(db) -> list:
    query = "SELECT DISTINCT Book FROM Verses ORDER BY Book"
    bookList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query)
        bookList = sorted([book[0] for book in cursor.fetchall() if not book[0] == 0])
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

def getBibleVerseList(db, b, c) -> list:
    query = "SELECT DISTINCT Verse FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
    verseList = ""
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        cursor.execute(query, (b, c))
        verseList = sorted([verse[0] for verse in cursor.fetchall()])
    return verseList

def change_area_1_bible_chapter(version, book, chapter):
    app.storage.user['bible_book_number']= book
    app.storage.user['bible_chapter_number']= chapter
    app.storage.user['bible_verse_number']= 1
    if version == "ORB":
        config.load_area_1_content(config.original_reader, version)
    elif version == "OIB":
        config.load_area_1_content(config.original_interlinear, version)
    elif version == "OPB":
        config.load_area_1_content(config.original_parallel, version)
    elif version == "ODB":
        config.load_area_1_content(config.original_discourse, version)
    elif version == "OLB":
        config.load_area_1_content(config.original_linguistic, version)
    else:
        config.load_area_1_content(config.bible_translation, version)

def change_area_2_bible_chapter(version, book, chapter):
    app.storage.user['bible_book_number']= book
    app.storage.user['bible_chapter_number']= chapter
    app.storage.user['bible_verse_number']= 1
    if version == "ORB":
        config.load_area_2_content(config.original_reader, version)
    elif version == "OIB":
        config.load_area_2_content(config.original_interlinear, version)
    elif version == "OPB":
        config.load_area_2_content(config.original_parallel, version)
    elif version == "ODB":
        config.load_area_2_content(config.original_discourse, version)
    elif version == "OLB":
        config.load_area_2_content(config.original_linguistic, version)
    else:
        config.load_area_2_content(config.bible_translation, version)

def change_bible_chapter_verse(_, book, chapter, verse):
    ui.run_javascript(f'scrollToVerse("v{book}.{chapter}.{verse}")')

class BibleSelector:
    """Class to manage Bible verse selection with dynamic dropdowns"""
    
    def __init__(self, on_version_changed=None, on_book_changed=None, on_chapter_changed=None, on_verse_changed=None):
        # Handlers that replace the default on_change functions
        self.on_version_changed, self.on_book_changed, self.on_chapter_changed, self.on_verse_changed = on_version_changed, on_book_changed, on_chapter_changed, on_verse_changed

        # Initialize selected values
        self.selected_version: Optional[str] = None
        self.selected_book: Optional[str] = None
        self.selected_chapter: Optional[int] = None
        self.selected_verse: Optional[int] = None
        
        # Initialize dropdown UI elements
        self.version_select: Optional[ui.select] = None
        self.book_select: Optional[ui.select] = None
        self.chapter_select: Optional[ui.select] = None
        self.verse_select: Optional[ui.select] = None
        
        # Initialize options
        self.version_options: List[str] = []
        self.book_options: List[str] = []
        self.chapter_options: List[int] = []
        self.verse_options: List[int] = []
        
    def create_ui(self, bible, b, c, v):
        self.selected_version = bible
        self.selected_book = b
        self.selected_chapter = c
        self.selected_verse = v

        self.version_options = getBibleVersionList()
        self.book_options = getBibleBookList(getBiblePath(self.selected_version))
        self.chapter_options = getBibleChapterList(getBiblePath(self.selected_version), self.selected_book)
        self.verse_options = getBibleVerseList(getBiblePath(self.selected_version), self.selected_book, self.selected_chapter)
        with ui.row().classes('w-full'):
            # Bible
            self.version_select = ui.select(
                options=self.version_options,
                label='Bible',
                value=bible,
                on_change=self.on_version_change
            )
            # Book
            self.book_select = ui.select(
                options=self.book_options,
                label='Book',
                value=b,
                on_change=self.on_book_change
            )
            # Chapter
            self.chapter_select = ui.select(
                options=self.chapter_options,
                label='Chapter',
                value=c,
                on_change=self.on_chapter_change
            )
            # Verse
            self.verse_select = ui.select(
                options=self.verse_options,
                label='Verse',
                value=v,
                on_change=self.on_verse_change
            )
    
    def on_version_change(self, e):
        """Handle Bible version selection change"""
        self.selected_version = e.value

        # replace default action
        if self.on_version_changed is not None:
            return self.on_version_changed(self.selected_version)

        # Reset book dropdowns if no version selected
        self.reset_book_dropdown()
        
        if self.selected_version:
            # Update book list based on selected version
            self.book_options = getBibleBookList(getBiblePath(self.selected_version))
            self.book_select.options = self.book_options
            self.book_select.props(remove='disable')
            self.book_select.value = None
            
            # Reset and disable chapter and verse dropdowns
            self.reset_chapter_dropdown()
            self.reset_verse_dropdown()
            
            # Update reference display
            self.update_reference_display()
        else:
            # Reset chapter and verse dropdowns if no version selected
            self.reset_chapter_dropdown()
            self.reset_verse_dropdown()
    
    def on_book_change(self, e):
        """Handle book selection change"""
        self.selected_book = e.value

        # replace default action
        if self.on_book_changed is not None:
            return self.on_book_changed(self.selected_version, self.selected_book)

        # place reset chapter here
        self.reset_chapter_dropdown()
        
        if self.selected_book and self.selected_version:
            # Update chapter list based on selected book
            self.chapter_options = getBibleChapterList(getBiblePath(self.selected_version), self.selected_book)
            self.chapter_select.options = self.chapter_options
            self.chapter_select.props(remove='disable')
            self.chapter_select.value = None
            
            # Reset verse dropdown
            self.reset_verse_dropdown()
            
            # Update reference display
            self.update_reference_display()
        else:
            # Reset verse dropdowns
            self.reset_verse_dropdown()
    
    def on_chapter_change(self, e):
        """Handle chapter selection change"""
        self.selected_chapter = e.value

        # replace default action
        if self.on_chapter_changed is not None:
            return self.on_chapter_changed(self.selected_version, self.selected_book, self.selected_chapter)

        # Reset verse dropdown
        self.reset_verse_dropdown()
        
        if self.selected_chapter and self.selected_book and self.selected_version:
            # Update verse list based on selected chapter
            self.verse_options = getBibleVerseList(
                getBiblePath(self.selected_version), 
                self.selected_book, 
                self.selected_chapter
            )
            self.verse_select.options = self.verse_options
            self.verse_select.props(remove='disable')
            self.verse_select.value = None
            
            # Update reference display
            self.update_reference_display()
    
    def on_verse_change(self, e):
        """Handle verse selection change"""
        self.selected_verse = e.value

        # replace default action
        if self.on_verse_changed is not None:
            return self.on_verse_changed(self.selected_version, self.selected_book, self.selected_chapter, self.selected_verse)

        self.update_reference_display()
    
    def reset_book_dropdown(self):
        """Reset book dropdown to initial state"""
        self.book_select.options = []
        self.book_select.value = None
        self.book_select.props('disable')
        self.selected_book = None
    
    def reset_chapter_dropdown(self):
        """Reset chapter dropdown to initial state"""
        self.chapter_select.options = []
        self.chapter_select.value = None
        self.chapter_select.props('disable')
        self.selected_chapter = None
    
    def reset_verse_dropdown(self):
        """Reset verse dropdown to initial state"""
        self.verse_select.options = []
        self.verse_select.value = None
        self.verse_select.props('disable')
        self.selected_verse = None
    
    def update_reference_display(self):
        """Update the displayed Bible reference"""
        parts = []
        if self.selected_version:
            parts.append(self.selected_version)
        if self.selected_book:
            parts.append(self.selected_book)
        if self.selected_chapter:
            parts.append(f"{self.selected_chapter}")
        if self.selected_verse:
            parts[-1] = f"{self.selected_chapter}:{self.selected_verse}"
        
        if parts:
            if len(parts) > 1:
                # Format as "Version - Book Chapter:Verse"
                reference = f"{parts[0]} - {' '.join(parts[1:])}"
            else:
                reference = parts[0]
            self.reference_label.set_text(reference)
        else:
            self.reference_label.set_text('None selected')
    
    def get_selection(self):
        """Get the current selection and display it"""
        result = {
            'version': self.selected_version,
            'book': self.selected_book,
            'chapter': self.selected_chapter,
            'verse': self.selected_verse
        }
        
        # Show notification with selection
        if all(result.values()):
            ui.notify(
                f'Selected: {result["version"]} - {result["book"]} {result["chapter"]}:{result["verse"]}',
                type='positive'
            )
        else:
            ui.notify('Please complete all selections', type='warning')
        
        print(f"Current selection: {result}")
        return result
    
    def set_reference(self, version: str, book: str, chapter: int, verse: int):
        """Programmatically set a Bible reference"""
        # Set version
        if version in self.version_options:
            self.version_select.value = version
            self.on_version_change(type('Event', (), {'value': version})())
            
            # Set book
            if book in self.book_options:
                self.book_select.value = book
                self.on_book_change(type('Event', (), {'value': book})())
                
                # Set chapter
                if chapter in self.chapter_options:
                    self.chapter_select.value = chapter
                    self.on_chapter_change(type('Event', (), {'value': chapter})())
                    
                    # Set verse
                    if verse in self.verse_options:
                        self.verse_select.value = verse
                        self.on_verse_change(type('Event', (), {'value': verse})())
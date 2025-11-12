from nicegui import ui
from typing import List, Dict, Optional

# Your existing functions (placeholders - replace with actual implementations)
def getBibleVersionList() -> List[str]:
    """Returns a list of available Bible versions"""
    # This is a placeholder - replace with your actual implementation
    return ['KJV', 'NIV', 'ESV', 'NASB', 'NLT']

def getBibleBookList(bible_version: str) -> List[str]:
    """Returns list of books for the selected Bible version"""
    # This is a placeholder - replace with your actual implementation
    # Different versions might have different books (e.g., Catholic Bible has more books)
    if bible_version in ['KJV', 'NIV', 'ESV', 'NASB', 'NLT']:
        return ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 
                'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel',
                '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
                'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
                'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah',
                'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
                'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk',
                'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
                'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
                '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
                'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
                '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
                'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
                'Jude', 'Revelation']
    return []

def getBibleChapterList(bible_version: str, book: str) -> List[int]:
    """Returns list of chapters for the selected book"""
    # This is a placeholder - replace with your actual implementation
    # Different books have different numbers of chapters
    chapter_counts = {
        'Genesis': 50, 'Exodus': 40, 'Leviticus': 27, 'Numbers': 36,
        'Deuteronomy': 34, 'Psalms': 150, 'Proverbs': 31, 'Isaiah': 66,
        'Matthew': 28, 'Mark': 16, 'Luke': 24, 'John': 21,
        'Revelation': 22, 'Philemon': 1, '2 John': 1, '3 John': 1,
        'Jude': 1, 'Obadiah': 1
    }
    # Default to 10 chapters if not in our sample data
    num_chapters = chapter_counts.get(book, 10)
    return list(range(1, num_chapters + 1))

def getBibleVerseList(bible_version: str, book: str, chapter: int) -> List[int]:
    """Returns list of verses for the selected chapter"""
    # This is a placeholder - replace with your actual implementation
    # Different chapters have different numbers of verses
    # For demo purposes, return a default range
    if book == 'Psalms' and chapter == 119:
        return list(range(1, 177))  # Psalm 119 has 176 verses
    elif book == 'Psalms' and chapter == 117:
        return list(range(1, 3))  # Psalm 117 has only 2 verses
    else:
        # Default to 30 verses for demo
        return list(range(1, 31))


class BibleSelector:
    """Class to manage Bible verse selection with dynamic dropdowns"""
    
    def __init__(self):
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
        
    def create_ui(self):
        """Create the UI components"""
        with ui.card().classes('w-full max-w-4xl mx-auto p-4'):
            ui.label('Bible Verse Selector').classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4 flex-wrap'):
                # Bible Version Dropdown
                with ui.column().classes('flex-1 min-w-48'):
                    ui.label('Bible Version:').classes('text-sm font-semibold')
                    self.version_options = getBibleVersionList()
                    self.version_select = ui.select(
                        options=self.version_options,
                        label='Select Version',
                        value=None,
                        on_change=self.on_version_change
                    ).classes('w-full')
                
                # Bible Book Dropdown
                with ui.column().classes('flex-1 min-w-48'):
                    ui.label('Book:').classes('text-sm font-semibold')
                    self.book_select = ui.select(
                        options=[],
                        label='Select Book',
                        value=None,
                        on_change=self.on_book_change
                    ).classes('w-full').props('disable')
                
                # Bible Chapter Dropdown
                with ui.column().classes('flex-1 min-w-32'):
                    ui.label('Chapter:').classes('text-sm font-semibold')
                    self.chapter_select = ui.select(
                        options=[],
                        label='Select Chapter',
                        value=None,
                        on_change=self.on_chapter_change
                    ).classes('w-full').props('disable')
                
                # Bible Verse Dropdown
                with ui.column().classes('flex-1 min-w-32'):
                    ui.label('Verse:').classes('text-sm font-semibold')
                    self.verse_select = ui.select(
                        options=[],
                        label='Select Verse',
                        value=None,
                        on_change=self.on_verse_change
                    ).classes('w-full').props('disable')
            
            # Display selected reference
            ui.separator().classes('my-4')
            with ui.row().classes('items-center gap-2'):
                ui.label('Selected Reference:').classes('font-semibold')
                self.reference_label = ui.label('None selected').classes('text-lg')
            
            # Add a button to get the selection
            ui.button('Get Selected Reference', on_click=self.get_selection).classes('mt-4')
    
    def on_version_change(self, e):
        """Handle Bible version selection change"""
        self.selected_version = e.value
        # Reset book dropdowns if no version selected
        self.reset_book_dropdown()
        
        if self.selected_version:
            # Update book list based on selected version
            self.book_options = getBibleBookList(self.selected_version)
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
        # Reset chapter dropdowns
        self.reset_chapter_dropdown()
        
        if self.selected_book and self.selected_version:
            # Update chapter list based on selected book
            self.chapter_options = getBibleChapterList(self.selected_version, self.selected_book)
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
        # Reset verse dropdown
        self.reset_verse_dropdown()
        
        if self.selected_chapter and self.selected_book and self.selected_version:
            # Update verse list based on selected chapter
            self.verse_options = getBibleVerseList(
                self.selected_version, 
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


# Main application
def main():
    # Create the Bible selector
    bible_selector = BibleSelector()
    bible_selector.create_ui()
    
    # Add example buttons to demonstrate programmatic selection
    with ui.card().classes('w-full max-w-4xl mx-auto p-4 mt-4'):
        ui.label('Quick References:').classes('text-lg font-bold mb-2')
        with ui.row().classes('gap-2'):
            ui.button(
                'John 3:16',
                on_click=lambda: bible_selector.set_reference('KJV', 'John', 3, 16)
            )
            ui.button(
                'Psalm 23:1',
                on_click=lambda: bible_selector.set_reference('NIV', 'Psalms', 23, 1)
            )
            ui.button(
                'Genesis 1:1',
                on_click=lambda: bible_selector.set_reference('ESV', 'Genesis', 1, 1)
            )

main()
ui.run(title='BibleMate - Verse Selector', port=9999)
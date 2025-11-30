from nicegui import ui
import sqlite3
import re
from typing import List, Tuple, Optional

class VerseDisplay:
    def __init__(self, db_path: str = 'bible.db'):
        """Initialize the verse display with database connection"""
        self.db_path = db_path
        self.verse_container = None
        self.input_field = None
        
    def parse_verse_references(self, input_text: str) -> List[Tuple[str, int, int, Optional[int]]]:
        """
        Parse verse references from user input
        Returns list of tuples: (book, chapter, start_verse, end_verse)
        """
        references = []
        # Split by semicolon for multiple references
        parts = input_text.split(';')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Pattern to match references like "John 3:16-18" or "Rom 5:8"
            pattern = r'([1-3]?\s*\w+)\s+(\d+):(\d+)(?:-(\d+))?'
            match = re.match(pattern, part)
            
            if match:
                book = match.group(1).strip()
                chapter = int(match.group(2))
                start_verse = int(match.group(3))
                end_verse = int(match.group(4)) if match.group(4) else None
                references.append((book, chapter, start_verse, end_verse))
                
        return references
    
    def get_verse_from_db(self, book: str, chapter: int, verse_start: int, verse_end: Optional[int] = None) -> str:
        """
        Retrieve verse content from database
        This is a placeholder - adjust according to your actual database schema
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if verse_end:
                # Multiple verses
                cursor.execute("""
                    SELECT verse_number, verse_text 
                    FROM verses 
                    WHERE book_name = ? AND chapter = ? 
                    AND verse_number >= ? AND verse_number <= ?
                    ORDER BY verse_number
                """, (book, chapter, verse_start, verse_end))
            else:
                # Single verse
                cursor.execute("""
                    SELECT verse_number, verse_text 
                    FROM verses 
                    WHERE book_name = ? AND chapter = ? AND verse_number = ?
                """, (book, chapter, verse_start))
            
            results = cursor.fetchall()
            conn.close()
            
            if results:
                # Format the verses
                if len(results) > 1:
                    return ' '.join([f"({v[0]}) {v[1]}" for v in results])
                else:
                    return results[0][1] if results else "Verse not found"
            else:
                return "Verse not found in database"
                
        except sqlite3.Error as e:
            return f"Database error: {str(e)}"
        except Exception as e:
            return f"Error retrieving verse: {str(e)}"
    
    def open_chapter(self, book: str, chapter: int):
        """
        Function to open the whole chapter when chip is clicked
        """
        ui.notify(f'Opening {book} Chapter {chapter}', type='info')
        # Here you can implement navigation to a chapter view page
        # For example: ui.open(f'/chapter/{book}/{chapter}')
        # Or display the chapter in a dialog/expansion panel
        
        # Example: Show chapter in a dialog
        with ui.dialog() as dialog, ui.card():
            ui.label(f'{book} Chapter {chapter}').classes('text-h6')
            
            # Fetch all verses for the chapter
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT verse_number, verse_text 
                    FROM verses 
                    WHERE book_name = ? AND chapter = ?
                    ORDER BY verse_number
                """, (book, chapter))
                verses = cursor.fetchall()
                conn.close()
                
                with ui.scroll_area().classes('w-96 h-96'):
                    for verse_num, verse_text in verses:
                        ui.label(f'{verse_num}. {verse_text}').classes('mb-2')
                        
            except Exception as e:
                ui.label(f'Error loading chapter: {str(e)}')
            
            ui.button('Close', on_click=dialog.close).classes('mt-4')
        
        dialog.open()
    
    def display_verses(self):
        """
        Process user input and display verses
        """
        if not self.input_field.value:
            ui.notify('Please enter verse references', type='warning')
            return
        
        # Clear previous results
        self.verse_container.clear()
        
        # Parse references
        references = self.parse_verse_references(self.input_field.value)
        
        if not references:
            with self.verse_container:
                ui.label('No valid verse references found. Please use format like: John 3:16 or Rom 5:8-10').classes('text-negative')
            return
        
        # Display each verse
        with self.verse_container:
            for book, chapter, start_verse, end_verse in references:
                # Create a card for each verse reference
                with ui.card().classes('w-full mb-4 p-4'):
                    # Reference as clickable chip
                    with ui.row().classes('items-center gap-2 mb-2'):
                        ref_text = f"{book} {chapter}:{start_verse}"
                        if end_verse:
                            ref_text += f"-{end_verse}"
                        
                        ui.chip(
                            ref_text, 
                            icon='menu_book',
                            color='primary',
                            on_click=lambda b=book, c=chapter: self.open_chapter(b, c)
                        ).classes('cursor-pointer').tooltip('Click to open chapter')
                    
                    # Verse content
                    verse_content = self.get_verse_from_db(book, chapter, start_verse, end_verse)
                    ui.label(verse_content).classes('text-body1')
    
    def create_page(self):
        """
        Create the main verse display page
        """
        with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
            # Title
            ui.label('Bible Verse Display').classes('text-h4 mb-4')
            
            # Input section
            with ui.row().classes('w-full gap-2 items-center'):
                self.input_field = ui.input(
                    label='Enter verse references',
                    placeholder='e.g., Deut 6:4; John 3:16-18; Rom 5:8'
                ).classes('flex-grow').on('keydown.enter.prevent', self.display_verses)
                
                ui.button(
                    'Display',
                    icon='search',
                    on_click=self.display_verses
                ).classes('h-14')
            
            # Help text
            ui.label('Separate multiple references with semicolons (;)').classes('text-caption text-gray-600 mt-1')
            
            # Verse display container
            with ui.column().classes('w-full mt-6 gap-2'):
                self.verse_container = ui.column().classes('w-full')


# Example usage and database setup
def create_sample_database():
    """
    Create a sample SQLite database with Bible verses
    This is for demonstration - replace with your actual database
    """
    conn = sqlite3.connect('bible.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_name TEXT,
            chapter INTEGER,
            verse_number INTEGER,
            verse_text TEXT
        )
    ''')
    
    # Insert sample verses
    sample_verses = [
        ('Deut', 6, 4, 'Hear, O Israel: The LORD our God, the LORD is one.'),
        ('John', 3, 16, 'For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.'),
        ('John', 3, 17, 'For God did not send his Son into the world to condemn the world, but to save the world through him.'),
        ('John', 3, 18, 'Whoever believes in him is not condemned, but whoever does not believe stands condemned already because they have not believed in the name of God\'s one and only Son.'),
        ('Rom', 5, 8, 'But God demonstrates his own love for us in this: While we were still sinners, Christ died for us.'),
        # Add more verses for complete chapters...
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO verses (book_name, chapter, verse_number, verse_text) VALUES (?, ?, ?, ?)', sample_verses)
    conn.commit()
    conn.close()


# Main app
def main():
    # Create sample database (run once)
    create_sample_database()
    
    # Initialize the verse display
    verse_display = VerseDisplay('bible.db')
    
    # Create the UI
    verse_display.create_page()
    
main()

# Run the app
ui.run(port=9999, reload=False, title='BibleMate AI - Verse Display')
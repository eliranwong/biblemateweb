import sqlite3
import re, os
from nicegui import ui, run

# --- CONFIGURATION ---
DB_FILE = os.path.expanduser("~/UniqueBible/marvelData/indexes2.sqlite")

# Map standard English book names to Integer IDs. 
# NOTE: Adjust these IDs to match your specific sqlite database schema.
# This assumes a standard Protestant 66-book order.
BOOK_MAPPING = {
    'genesis': 1, 'exodus': 2, 'leviticus': 3, 'numbers': 4, 'deuteronomy': 5,
    'joshua': 6, 'judges': 7, 'ruth': 8, '1 samuel': 9, '2 samuel': 10,
    '1 kings': 11, '2 kings': 12, '1 chronicles': 13, '2 chronicles': 14,
    'ezra': 15, 'nehemiah': 16, 'esther': 17, 'job': 18, 'psalms': 19, 'psalm': 19,
    'proverbs': 20, 'ecclesiastes': 21, 'song of solomon': 22, 'isaiah': 23,
    'jeremiah': 24, 'lamentations': 25, 'ezekiel': 26, 'daniel': 27,
    'hosea': 28, 'joel': 29, 'amos': 30, 'obadiah': 31, 'jonah': 32,
    'micah': 33, 'nahum': 34, 'habakkuk': 35, 'zephaniah': 36, 'haggai': 37,
    'zechariah': 38, 'malachi': 39,
    'matthew': 40, 'mark': 41, 'luke': 42, 'john': 43, 'acts': 44,
    'romans': 45, '1 corinthians': 46, '2 corinthians': 47, 'galatians': 48,
    'ephesians': 49, 'philippians': 50, 'colossians': 51,
    '1 thessalonians': 52, '2 thessalonians': 53, '1 timothy': 54,
    '2 timothy': 55, 'titus': 56, 'philemon': 57, 'hebrews': 58, 'james': 59,
    '1 peter': 60, '2 peter': 61, '1 john': 62, '2 john': 63, '3 john': 64,
    'jude': 65, 'revelation': 66
}

# Define your tables, their display titles, and their icons
TABLE_CONFIG = {
    "Bible People": {
        "table": "exlbp", 
        "icon": "groups"        # Icon for people/groups
    },
    "Bible Locations": {
        "table": "exlbl", 
        "icon": "place"         # Icon for maps/locations
    },
    "Bible Topics": {
        "table": "exlbt", 
        "icon": "category"      # Icon for topics/categories
    },
    "Dictionaries": {
        "table": "dictionaries", 
        "icon": "menu_book"     # Icon for definitions/books
    },
    "Encyclopedia": {
        "table": "encyclopedia", 
        "icon": "local_library" # Icon for deep knowledge/library
    }
}

def parse_reference(ref_text: str):
    """
    Parses a string like 'John 3:16' or '1 Kings 2:5'.
    Returns (book_id, chapter, verse) or None.
    """
    pattern = r"^(\d?\s*[a-zA-Z\s]+)\s+(\d+):(\d+)$"
    match = re.match(pattern, ref_text.strip())
    
    if not match:
        return None
        
    book_name = match.group(1).lower().strip()
    chapter = int(match.group(2))
    verse = int(match.group(3))
    
    book_id = BOOK_MAPPING.get(book_name)
    
    if not book_id:
        return None
        
    return (book_id, chapter, verse)

def fetch_data(table_name: str, book_id: int, chapter: int, verse: int):
    """
    Connects to SQLite and retrieves information for the specific verse.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            query = f"SELECT Information FROM {table_name} WHERE Book=? AND Chapter=? AND Verse=?"
            cursor.execute(query, (book_id, chapter, verse))
            rows = cursor.fetchall()
            return "\n\n".join([row[0] for row in rows]) if rows else None
    except Exception as e:
        return f"Error querying database: {str(e)}"

@ui.page('/')
def main_page():
    # --- UI LAYOUT ---
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):
        
        # Header
        with ui.row().classes('items-center gap-2'):
            ui.icon('auto_stories', size='3em', color='primary')
            ui.label('BibleMate AI Resource Index').classes('text-3xl font-bold text-slate-700')

        # Search Area
        with ui.card().classes('w-full p-6 bg-slate-50'):
            ui.label('Search a Verse').classes('text-sm font-bold text-slate-500 uppercase')
            
            with ui.row().classes('w-full items-start gap-2'):
                ref_input = ui.input(placeholder='e.g. John 3:16') \
                    .classes('w-full text-lg') \
                    .props('outlined clearable') \
                    .on('keydown.enter', lambda: search_action())
                
                search_btn = ui.button(icon='search', on_click=lambda: search_action()) \
                    .classes('h-14 aspect-square')

        # Results Container
        results_container = ui.column().classes('w-full gap-4')

    async def search_action():
        """
        Orchestrates the search logic: 
        1. Validate input
        2. Clear previous results
        3. Query DB
        4. Render Expansion panels
        """
        query_text = ref_input.value
        parsed = parse_reference(query_text)
        
        if not parsed:
            ui.notify('Invalid format. Use "Book Chapter:Verse" (e.g., John 3:16)', type='warning')
            return

        book_id, chapter, verse = parsed
        
        # Clear UI and show loading spinner
        results_container.clear()
        
        with results_container:
            spinner = ui.spinner('dots', size='lg').classes('self-center')
            
            # Run IO-bound DB operations
            results = {}
            for title, config in TABLE_CONFIG.items():
                n = ui.notification('Loading ...', timeout=None, spinner=True)
                data = await run.io_bound(fetch_data, config['table'], book_id, chapter, verse)
                n.dismiss()
                results[title] = data

            spinner.delete()
            
            ui.label(f"Resources for {query_text.title()}") \
                .classes('text-xl font-semibold text-slate-600 mb-2')

            # --- RENDER EXPANSIONS ---
            found_any = False
            
            for title, config in TABLE_CONFIG.items():
                content = results.get(title)
                
                # Check if this should be open by default
                is_open = (title == "Bible Topics")
                
                # Create the Expansion with specific icon
                with ui.expansion(title, icon=config['icon'], value=is_open) \
                        .classes('w-full bg-white border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-primary"'):
                    
                    if content:
                        ui.html(content, sanitize=False).classes('p-4 text-slate-800')
                        found_any = True
                    else:
                        ui.label('No entries found for this category.') \
                            .classes('p-4 text-slate-400 italic')

            if not found_any:
                ui.notify('No data found in any index for this verse.', type='info')

ui.run(title='BibleMate AI Indexer', port=9999)
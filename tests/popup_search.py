from nicegui import ui, app

# --------------------------------------------------------------------------
# 1. Mock Data: This represents your documentation pages or app content
# --------------------------------------------------------------------------
search_index = [
    {"title": "Introduction to BibleMate", "desc": "Getting started with the app.", "icon": "menu_book"},
    {"title": "Reading Plans", "desc": "How to set up daily reading schedules.", "icon": "calendar_today"},
    {"title": "Verse Analysis", "desc": "Using AI to analyze specific verses.", "icon": "analytics"},
    {"title": "Hebrew & Greek Dictionary", "desc": "Lookup original text meanings.", "icon": "translate"},
    {"title": "User Settings", "desc": "Manage theme and font preferences.", "icon": "settings"},
    {"title": "Exporting Notes", "desc": "How to export your study notes to PDF.", "icon": "download"},
    {"title": "Community Features", "desc": "Sharing insights with other users.", "icon": "groups"},
]

# --------------------------------------------------------------------------
# 2. Search Component Logic
# --------------------------------------------------------------------------
class SearchModal:
    def __init__(self):
        # The dialog object
        self.dialog = ui.dialog()
        self.results_container = None
        self.search_input = None
        
        # Create the UI structure inside the dialog once
        with self.dialog, ui.card().classes('w-[600px] max-w-full h-[500px] no-shadow border-[1px] border-gray-200'):
            # Header / Input Area
            with ui.row().classes('w-full items-center border-b border-gray-200 pb-2'):
                ui.icon('search', size='md').classes('text-gray-400 ml-2')
                self.search_input = ui.input(
                    placeholder='Search documentation...', 
                    on_change=self.update_results
                ).props('autofocus borderless input-class="text-lg"').classes('flex-grow ml-2')
                
                # Close button (Esc also works)
                ui.button(icon='close', on_click=self.close).props('flat round dense color=gray')

            # Results Area
            with ui.scroll_area().classes('w-full flex-grow p-2'):
                self.results_container = ui.column().classes('w-full gap-1')

    def open(self):
        """Opens the dialog and resets the search."""
        self.search_input.value = ''  # Reset input
        self.update_results(None)     # Show all or empty
        self.dialog.open()

    def close(self):
        self.dialog.close()

    def navigate(self, item):
        """Simulate navigation."""
        ui.notify(f"Navigating to: {item['title']}", type='positive')
        self.close()

    def update_results(self, e):
        """Filter the list based on input."""
        query = self.search_input.value.lower()
        self.results_container.clear() # Clear previous results

        if not query:
            # Optional: Show nothing, or show 'Recent' items when empty
            with self.results_container:
                ui.label('Type to start searching...').classes('text-gray-400 italic mx-auto mt-4')
            return

        # Filter logic
        matches = [item for item in search_index if query in item['title'].lower() or query in item['desc'].lower()]

        # Render results
        with self.results_container:
            if not matches:
                ui.label('No results found.').classes('text-gray-500 mx-auto mt-4')
            
            for item in matches:
                # Create a clickable card for each result
                with ui.card().classes('w-full p-3 cursor-pointer hover:bg-blue-50 transition-colors') \
                        .on('click', lambda i=item: self.navigate(i)):
                    with ui.row().classes('items-center no-wrap gap-4'):
                        ui.icon(item['icon'], size='md').classes('text-blue-500')
                        with ui.column().classes('gap-0'):
                            ui.label(item['title']).classes('font-bold text-gray-800')
                            ui.label(item['desc']).classes('text-sm text-gray-500')

# --------------------------------------------------------------------------
# 3. Main Application UI
# --------------------------------------------------------------------------
def main():
    # Initialize the search modal
    search = SearchModal()

    # Global Keyboard Shortcut (Ctrl+K or Cmd+K)
    # We use a hidden keyboard listener to trigger the open function
    def handle_key(e):
        if (e.key == 'k' and (e.modifiers.ctrl or e.modifiers.meta)):
            search.open()

    keyboard = ui.keyboard(on_key=handle_key)

    # -- App Content --
    with ui.header().classes(replace='row items-center') as header:
        header.classes('bg-blue-900 text-white p-4')
        ui.icon('menu_book', size='lg')
        ui.label('BibleMate AI').classes('text-xl font-bold mr-auto')
        
        # Trigger button in header (Visual cue)
        with ui.button(on_click=search.open).props('flat color=white icon=search').classes('bg-blue-800/50 rounded-full px-4 py-1'):
            ui.label('Search...').classes('ml-2 text-sm opacity-80 hidden sm:block')
            with ui.row().classes('ml-4 gap-1 hidden sm:flex'):
                # FIX: ui.element does not have a .text() method.
                # We use a context manager to add the text label inside the kbd element.
                with ui.element('kbd').classes('bg-black/20 px-1 rounded text-xs'):
                    ui.label('Ctrl')
                with ui.element('kbd').classes('bg-black/20 px-1 rounded text-xs'):
                    ui.label('K')

    with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-6'):
        ui.label('Welcome to BibleMate Development').classes('text-3xl font-light')
        ui.markdown("""
        This is a demo of a **Spotlight Search** (Command Palette) similar to documentation sites.
        
        - Click the **Search** button in the top right.
        - Or press **Ctrl + K** (or Cmd + K on Mac).
        - Type terms like "User", "Export", or "Greek".
        """)
        
        with ui.row().classes('gap-4'):
            ui.card().classes('w-64 h-32 bg-gray-100').props('flat')
            ui.card().classes('w-64 h-32 bg-gray-100').props('flat')


main()
ui.run(title="BibleMate Search Demo", port=9999, reload=False)

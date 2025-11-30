from functools import partial
from nicegui import ui
import re

# ==============================================================================
# 1. MOCK BACKEND
# ==============================================================================
def get_bible_content(ref_string):
    results = []
    raw_refs = [r.strip() for r in ref_string.split(';') if r.strip()]

    for ref in raw_refs:
        content = "<i>Content not found in mock DB.</i>"
        if "John 3:16" in ref:
            content = "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."
        elif "John 3:17" in ref:
            content = "For God did not send his Son into the world to condemn the world, but to save the world through him."
        elif "John 3:18" in ref:
            content = "Whoever believes in him is not condemned, but whoever does not believe stands condemned already because they have not believed in the name of God’s one and only Son."
        elif "Deut 6:4" in ref:
            content = "Hear, O Israel: The <span class='text-primary font-bold'>LORD</span> our God, the <span class='text-primary font-bold'>LORD</span> is one."
        elif "Rom 5:8" in ref:
            content = "But God demonstrates his own love for us in this: While we were still sinners, Christ died for us."
        else:
            content = f"Mock content for <b>{ref}</b>. Lorem ipsum dolor sit amet, consectetur adipiscing elit."

        results.append({'ref': ref, 'content': content})
    return results

# ==============================================================================
# 2. APP LOGIC
# ==============================================================================
@ui.page('/')
def main_page():
    ui.add_head_html('<style>body { background-color: #f8fafc; }</style>')

    # ----------------------------------------------------------
    # Helper: Filter Logic
    # ----------------------------------------------------------
    def filter_verses(e=None):
        """
        Filters visibility based on input.
        Iterates over default_slot.children to find rows.
        """
        # Robustly determine the search text
        text = ""
        if e is not None and hasattr(e, 'value'):
            text = e.value 
        else:
            text = input_field.value 
            
        search_term = text.lower() if text else ""
        
        # Iterate over the actual children of the container
        for row in verses_container.default_slot.children:
            # Skip elements that aren't our verse rows (if any)
            if not hasattr(row, 'verse_data'):
                continue

            # Explicitly show all if search is empty
            if not search_term:
                row.set_visibility(True)
                continue

            data = row.verse_data
            ref_text = data['ref'].lower()
            clean_content = re.sub('<[^<]+?>', '', data['content']).lower()

            is_match = (search_term in ref_text) or (search_term in clean_content)
            row.set_visibility(is_match)

    # ----------------------------------------------------------
    # Helper: Remove Verse
    # ----------------------------------------------------------
    def remove_verse_row(row_element, reference):
        try:
            verses_container.remove(row_element)
            ui.notify(f'Removed: {reference}', type='warning', position='top')
        except Exception as e:
            print(f"Error removing row: {e}")

    # ----------------------------------------------------------
    # Helper: Open Chapter
    # ----------------------------------------------------------
    def open_chapter(reference):
        ui.notify(f'Opening Chapter for {reference}...', type='info')

    # ----------------------------------------------------------
    # Core: Fetch and Display
    # ----------------------------------------------------------
    def handle_enter(e):
        query = input_field.value.strip()
        
        # Clear existing rows first
        verses_container.clear()
        
        if not query:
            ui.notify('Display cleared', type='positive', position='top')
            return

        verses = get_bible_content(query)

        if not verses:
            ui.notify('No verses found.', type='negative')
            return

        # CRITICAL FIX: Use 'with verses_container:' so rows become children of the container
        with verses_container:
            for v in verses:
                # Row setup
                with ui.row().classes('w-full bg-white shadow-sm rounded-lg p-3 items-start no-wrap border border-gray-200') as row:
                    
                    row.verse_data = v # Store data for filter function

                    # --- Chip (Clickable & Removable) ---
                    with ui.element('div').classes('flex-none pt-1'): 
                        chip = ui.chip(
                            v['ref'], 
                            removable=True, 
                            icon='book',
                            color='blue-1',
                            text_color='blue-9',
                            on_click=partial(ui.notify, f'Clicked {v['ref']}'),
                        ).classes('cursor-pointer font-bold shadow-sm')
                        
                        #chip.on('click', lambda _, ref=v['ref']: open_chapter(ref))
                        chip.on('remove', lambda _, r=row, ref=v['ref']: remove_verse_row(r, ref))

                    # --- Content ---
                    ui.html(v['content'], sanitize=False).classes('grow min-w-0 text-gray-800 leading-relaxed pt-2 pl-2 text-base break-words')

        # Clear input so user can start typing to filter immediately
        input_field.value = ""
        input_field.props('placeholder="Type to filter results..."')

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    
    # --- Header ---
    with ui.header(elevated=True).classes('bg-white text-gray-800 border-b border-gray-200'):
        with ui.column().classes('w-full max-w-3xl mx-auto py-2 px-4'):
            ui.label('BibleMate AI Reader').classes('text-lg font-bold text-blue-600')
            
            input_field = ui.input(
                placeholder='Enter refs (e.g. John 3:16; Deut 6:4)'
            ).classes('w-full text-lg') \
             .props('outlined dense clearable autofocus enterkeyhint="search"')

            input_field.on('keydown.enter.prevent', handle_enter)
            input_field.on('update:model-value', filter_verses)

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center pt-4 pb-20 px-2'):
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full gap-2 p-2 max-w-3xl mx-auto transition-all')

ui.run(title='BibleMate AI', port=9999)
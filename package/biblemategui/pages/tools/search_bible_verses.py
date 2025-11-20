from biblemategui.fx.bible import get_bible_content
from functools import partial
from nicegui import ui, app
import re


def search_bible_verses(gui=None, **_):

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

        active_bible_tab = gui.get_active_area1_tab()
        verses = get_bible_content(query, bible=app.storage.user[active_bible_tab]["bt"] if active_bible_tab in app.storage.user else "NET")

        if not verses:
            ui.notify('No verses found.', type='negative')
            return

        with verses_container:
            for v in verses:
                # Row setup
                with ui.column().classes('w-full shadow-sm rounded-lg items-start no-wrap border border-gray-200 !gap-0') as row:
                    
                    row.verse_data = v # Store data for filter function

                    # --- Chip (Clickable & Removable) ---
                    with ui.element('div').classes('flex-none pt-1'): 
                        chip = ui.chip(
                            v['ref'], 
                            removable=True, 
                            icon='book',
                            on_click=partial(ui.notify, f'Clicked {v['ref']}'),
                        ).classes('cursor-pointer font-bold shadow-sm')
                        chip.on('remove', lambda _, r=row, ref=v['ref']: remove_verse_row(r, ref))

                    # --- Content ---
                    ui.html(v['content'], sanitize=False).classes('grow min-w-0 leading-relaxed pl-2 text-base break-words')

        # Clear input so user can start typing to filter immediately
        input_field.value = ""
        input_field.props('placeholder="Type to filter results..."')

    # ==============================================================================
    # 3. UI LAYOUT
    # ==============================================================================
    with ui.column().classes('w-full max-w-3xl mx-auto py-2 px-4'):
        input_field = ui.input(
            placeholder='Enter refs (e.g. Deut 6:4; John 3:16-18) or a search item'
        ).classes('w-full text-lg') \
        .props('outlined dense clearable autofocus')

        input_field.on('keydown.enter', handle_enter)
        input_field.on('update:model-value', filter_verses)

    # --- Main Content Area ---
    with ui.column().classes('w-full items-center'):
        # Define the container HERE within the layout structure
        verses_container = ui.column().classes('w-full transition-all !gap-1')

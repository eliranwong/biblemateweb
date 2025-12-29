from nicegui import ui, app
from biblemategui.data.bible_events import bible_events
from biblemategui import get_translation

def bible_chronology(gui=None, **_):
    #ui.page_title('Bible Chronology')

    # Function to be triggered when the link is clicked
    def open_verse_reference(reference: str):
        """Updates the output label with information about the clicked reference."""
        nonlocal gui
        app.storage.user['tool_query'] = reference
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Verses')

    # Function to create the clickable link component
    def create_internal_link(reference: str):
        # 1. Create the ui.link component (it looks like a link)
        link_component = ui.link(
            text=reference,
            target='#' # Set target to '#' or omit it since we are not opening a URL
        ).classes('text-secondary hover:text-primary underline')
        # 2. Attach the Python function to the 'click' event
        # We use a lambda to pass the specific 'reference' string argument to the function
        link_component.on('click', lambda: open_verse_reference(reference))
        
        return link_component

    with ui.card().classes('w-full'):
        ui.label('📜 Bible Chronology').classes('text-2xl font-bold mb-4')
        with ui.timeline(side='right'):
            for item in bible_events:
                # Create the interactive link
                ref_link = create_internal_link(item['reference'])
                
                with ui.timeline_entry(
                    title=item['event'],
                    subtitle=item['year'],
                    icon='menu_book'
                ):
                    with ui.row():
                        ref_link
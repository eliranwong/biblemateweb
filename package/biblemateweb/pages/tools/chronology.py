from nicegui import ui, app
from biblemateweb.data.bible_events import bible_events
from biblemateweb import build_xlsx_table, download_txt, download_xlsx, get_translation

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

    async def export_chronology(as_xlsx=False):
        if as_xlsx:
            rows = [[item['year'], item['event'], item['reference']] for item in bible_events]
            await download_xlsx(build_xlsx_table(["Year", "Event", "Reference"], rows, sheet_name="Chronology", widths=[18, 50, 24]))
        else:
            lines = ["# Bible Chronology", ""]
            for item in bible_events:
                lines.append(f"- **{item['year']}** — {item['event']} ({item['reference']})")
            await download_txt("\n".join(lines))

    with ui.card().classes('w-full'):
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('📜 Bible Chronology').classes('text-2xl font-bold')
            with ui.row().classes('items-center gap-2'):
                ui.button(get_translation('Export Table'), icon='table_chart', on_click=lambda: export_chronology(True)).props('outline size=sm color=secondary')
                ui.button('TXT', icon='download', on_click=lambda: export_chronology(False)).props('outline size=sm color=primary')
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
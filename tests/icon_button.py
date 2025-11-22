from nicegui import ui

def handle_action(action):
    ui.notify(f'Action: {action}')

with ui.row().classes('items-center gap-4'):
    
    # --- Option 1: Vertical Dots (Standard for Lists/Cards) ---
    # .props('flat round') removes the background and makes the hover effect circular
    with ui.button(icon='more_vert').props('flat round color=black'):
        with ui.menu():
            ui.menu_item('Share Verse', on_click=lambda: handle_action('Share'))
            ui.menu_item('Copy', on_click=lambda: handle_action('Copy'))
            ui.separator()
            ui.menu_item('Delete', on_click=lambda: handle_action('Delete'))

    # --- Option 2: Horizontal Dots (Standard for Tables/Toolbars) ---
    # .props('dense') makes the button smaller/compact
    with ui.button(icon='more_horiz').props('flat round dense color=primary'):
        with ui.menu():
            ui.menu_item('Quick View', on_click=lambda: handle_action('Quick View'))
            ui.menu_item('Details', on_click=lambda: handle_action('Details'))

ui.run(port=9999)
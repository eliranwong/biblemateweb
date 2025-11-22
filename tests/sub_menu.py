from nicegui import ui

def handle(action):
    ui.notify(f'Selected: {action}')

with ui.row().classes('w-full justify-center q-mt-xl'):

    # Main Trigger Button
    with ui.button(icon='more_vert').props('flat round color=black'):
        with ui.menu():
            
            # Standard Action (Use menu_item so it closes after clicking)
            ui.menu_item('Copy Text', on_click=lambda: handle('Copy'))
            
            ui.separator()

            # --- THE FIX IS HERE ---
            # Use ui.item instead of ui.menu_item.
            # We add .props('clickable') so it looks interactive (hover effect).
            with ui.item().props('clickable'): 
                
                # We need to define the text manually inside ui.item
                with ui.item_section():
                    ui.label('Export As...')
                
                # The arrow icon
                with ui.item_section().props('side'):
                    ui.icon('arrow_right')

                # The Sub-Menu
                # anchor="top right" self="top left" makes it pop to the side
                with ui.menu().props('anchor="top right" self="top left"'):
                    ui.menu_item('PDF File', on_click=lambda: handle('PDF'))
                    ui.menu_item('Word Doc', on_click=lambda: handle('DOCX'))

            # Standard Action
            ui.menu_item('Delete', on_click=lambda: handle('Delete'))

ui.run(port=9999)
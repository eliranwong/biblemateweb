from nicegui import ui

def main():
    # 1. Logic to Swap Layout
    def swap_layout():
        ui.notify('Layout Swapped!', type='positive')

    # 2. Logic to Handle Drag Drop (Snap to position)
    def handle_drag_end(e):
        # Get the drop coordinates from the event arguments
        x = e.args['clientX']
        y = e.args['clientY']
        
        # Update the container style to fix it at the new coordinates.
        # We subtract 20px to center the button on the mouse pointer (approx half size).
        # We must set bottom/right to 'auto' to let top/left take precedence.
        fab_container.style(f'top: {y - 20}px; left: {x - 20}px; bottom: auto; right: auto')

    # --- UI LAYOUT ---

    # 3. The Visibility Toggle
    with ui.row().classes('w-full items-center gap-4 p-4'):
        ui.label('Main Page Content')
        toggle = ui.switch('Show Floating Button', value=True)

    # 4. The Draggable Container
    # - 'draggable="true"': Enables the native browser drag behavior.
    # - 'cursor: grab': Shows the user it is movable.
    # - 'dragend': Triggered when you release the mouse. We explicitly ask for X/Y coordinates.
    with ui.column().classes('fixed bottom-6 right-6 z-50 touch-none') \
            .props('draggable="true"') \
            .style('cursor: grab') as fab_container:
        
        fab_container.bind_visibility_from(toggle, 'value')
        
        # We request 'clientX' and 'clientY' to know where the mouse was released
        fab_container.on('dragend', handle_drag_end, ['clientX', 'clientY'])

        # 5. The Button (Smaller Size)
        # - 'fab-mini': Quasar's specific prop for a smaller floating action button.
        ui.button(icon='swap_horiz', on_click=swap_layout) \
            .props('fab-mini color=primary') \
            .tooltip('Drag to move')

    # Dummy content
    for i in range(20):
        ui.label(f'BibleMate AI Content Line {i+1}').classes('ml-4 text-gray-400')

main()

ui.run(title='BibleMate AI - Movable FAB', port=9999)
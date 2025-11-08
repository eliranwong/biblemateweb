from nicegui import ui

# Initialize the dark mode controller
dark_mode = ui.dark_mode()

with ui.header().classes('justify-between items-center'):
    ui.label('My App')
    # Bind a switch to the dark mode controller
    ui.switch('Dark Mode', on_change=dark_mode.toggle)

# Content demonstrates automatic theme switching
with ui.card().classes('m-4'):
    ui.label('Try toggling the switch in the header.')
    ui.button('Standard Button')

ui.run(port=12345)
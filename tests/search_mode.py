from nicegui import app, ui
from biblemateweb import config

@ui.page('/')
def index():
    # 1. Initialize default values in user storage if they don't exist
    # 1=Literal, 2=Regex, 3=Semantic
    app.storage.user.setdefault('search_mode', 1) 
    app.storage.user.setdefault('search_case_sensitivity', False)

    # 2. Define the callback function
    def handle_change(e):
        # Access the current state from storage
        mode_map = {1: 'Literal', 2: 'Regex', 3: 'Semantic'}
        current_mode = app.storage.user.get('search_mode')
        is_case_sensitive = app.storage.user.get('search_case_sensitivity')
        
        mode_label = mode_map.get(current_mode, 'Unknown')
        
        # Notify the user (simulating the trigger)
        ui.notify(f"Changed configuration: Mode='{mode_label}', Case Sensitive={is_case_sensitive}")

    # 3. UI Layout
    with ui.card().classes('w-full max-w-3xl mx-auto p-4'):
        ui.markdown('### Search Settings')
        
        # Container for the horizontal row
        with ui.row().classes('items-center'):
            
            # Radio Buttons
            # options: dictionary maps the stored value (keys) to the display label (values)
            # props('inline'): makes the radio buttons layout horizontally
            modes = ui.radio(
                options={1: 'Literal', 2: 'Regex', 3: 'Semantic'},
            ).bind_value(
                app.storage.user, 'search_mode'
            ).props('inline color=primary').on_value_change(handle_change)
            modes.tooltip = ui.tooltip('I like this')

            # Vertical separator (optional visual aid)
            ui.separator().props('vertical')

            # Checkbox
            ui.checkbox(
                'Case-sensitive'
            ).bind_value(
                app.storage.user, 'search_case_sensitivity'
            ).on_value_change(handle_change)

    # Display current state (for debugging/visualization purposes)
    with ui.row().classes('mt-4 ml-4'):
        ui.label().bind_text_from(app.storage.user, 'search_mode', backward=lambda x: f"Current Mode ID: {x}")
        ui.label().bind_text_from(app.storage.user, 'search_case_sensitivity', backward=lambda x: f" | Case Sensitive: {x}")

ui.run(title="BibleMate AI - Search Config", port=9998, storage_secret=config.storage_secret)
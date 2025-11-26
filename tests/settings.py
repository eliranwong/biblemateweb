#!/usr/bin/env python3
from nicegui import app, ui
from biblemategui import USER_DEFAULT_SETTINGS


@ui.page('/')
def index_page():
    """A simple main page to link to the settings."""

    # --- Default Settings ---
    # We define our default settings structure.
    # This function ensures that all necessary keys exist in app.storage.user
    def set_default_settings():
        """Sets the default settings in app.storage.user if they don't already exist."""
        for key, value in USER_DEFAULT_SETTINGS.items():
            if key not in app.storage.user:
                app.storage.user[key] = value

    # Call this once on startup to populate the storage
    set_default_settings()

    # Bind app state to user storage
    ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
    ui.fullscreen().bind_value(app.storage.user, 'fullscreen')
    
    with ui.column().classes('items-center w-full mt-10'):
        ui.label('BibleMate AI').classes('text-3xl font-bold')
        ui.link('Go to Settings', '/settings').classes('text-lg text-blue-600')
        
        # This label will update in real-time if you change the setting
        ui.label().bind_text_from(app.storage.user, 'favorite_bible',
                                  lambda v: f'Your current default Bible is: {v}') \
            .classes('mt-4 p-2 bg-gray-100 rounded')

@ui.page('/settings')
def settings_page():
    """The main settings page for the BibleMate AI app."""

    def set_default_settings():
        """Sets the default settings in app.storage.user if they don't already exist."""
        for key, value in USER_DEFAULT_SETTINGS.items():
            if key not in app.storage.user:
                app.storage.user[key] = value

    # We can call this again to be safe, especially if new settings are added in updates.
    set_default_settings()

    # Bind app state to user storage
    ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
    ui.fullscreen().bind_value(app.storage.user, 'fullscreen')

    with ui.card().classes('w-full max-w-2xl mx-auto p-6 shadow-xl rounded-lg'):
        ui.label('BibleMate AI Settings').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # --- Appearance Section ---
        with ui.expansion('Appearance', icon='palette').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4'):
                ui.color_input(label='Primary Color') \
                    .bind_value(app.storage.user, 'primary_color') \
                    .tooltip('Manual hex code or color picker for app theme.')
                
                ui.switch('Dark Mode') \
                    .bind_value(app.storage.user, 'dark_mode') \
                    .tooltip('Toggle dark mode for the app.')

                ui.switch('Fullscreen') \
                    .bind_value(app.storage.user, 'fullscreen') \
                    .tooltip('Toggle fullscreen mode for the app.')

        # --- User & Custom Data Section ---
        with ui.expansion('User & Custom Data', icon='person').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4 gap-4'):
                ui.input(label='Avatar URL', placeholder='https://example.com/avatar.png') \
                    .bind_value(app.storage.user, 'avatar') \
                    .classes('w-full') \
                    .tooltip('URL for your profile picture (leave blank for default).')
                
                ui.input(label='Custom Token', password=True, password_toggle_button=True) \
                    .bind_value(app.storage.user, 'custom_token') \
                    .classes('w-full') \
                    .tooltip('Token for using custom data sources or personal APIs.')

        # --- Default Resources Section ---
        with ui.expansion('Default Resources', icon='book', value=True).classes('w-full rounded-lg'):
            # Use a grid for a more compact layout
            with ui.grid(columns=2).classes('w-full p-4 gap-4'):
                ui.select(label='Default Bible',
                          options=['NET', 'NIV', 'ESV', 'KJV']) \
                    .bind_value(app.storage.user, 'favorite_bible')

                ui.select(label='Default Commentary',
                          options=['Cambridge', 'CBC', 'Calvin']) \
                    .bind_value(app.storage.user, 'favorite_commentary')

                ui.select(label='Default Encyclopedia',
                          options=['ISBE', 'Hasting', 'Kitto']) \
                    .bind_value(app.storage.user, 'favorite_encyclopedia')

                ui.select(label='Default Lexicon',
                          options=['Strong', 'HALOT', 'BDAG']) \
                    .bind_value(app.storage.user, 'favorite_lexicon')

        # --- AI Backend Section ---
        with ui.expansion('AI Backend', icon='memory').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4 gap-4'):
                ui.select(label='AI Backend',
                          options=['googleai', 'openai', 'azure', 'xai']) \
                    .bind_value(app.storage.user, 'ai_backend') \
                    .tooltip('Select the AI service provider.')

                ui.input(label='API Endpoint', placeholder='(Optional) Custom API endpoint') \
                    .bind_value(app.storage.user, 'api_endpoint') \
                    .classes('w-full') \
                    .tooltip('The custom API endpoint URL (if not using default).')

                ui.input(label='API Key', password=True, password_toggle_button=True) \
                    .bind_value(app.storage.user, 'api_key') \
                    .classes('w-full') \
                    .tooltip('Your API key for the selected backend.')

        # --- Localization Section ---
        with ui.expansion('Language', icon='language').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4'):
                ui.select(label='Language',
                          options=['English', 'Traditional Chinese', 'Simplified Chinese']) \
                    .bind_value(app.storage.user, 'language')

        # --- Save Feedback ---
        ui.button('Save Confirmation', on_click=lambda: ui.notify('Settings saved!', color='positive')) \
            .classes('mt-6 w-full py-3 bg-blue-600 text-white rounded-lg font-semibold') \
            .tooltip('All settings are saved automatically as you change them. Click this to confirm.')

# Run the app
ui.run(
    title='BibleMate AI - Settings',
    storage_secret='your-secret-key-here',  # Change this to a secure secret
    dark=False,
    port=8899,
    reload=False,
)
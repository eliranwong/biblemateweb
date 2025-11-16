#!/usr/bin/env python3
from nicegui import ui
from biblemategui import config, BIBLEMATEGUI_APP_DIR, USER_DEFAULT_SETTINGS
from biblemategui.pages.home import *
import os

# Home Page

@ui.page('/')
def page_home(
    d: bool | None = None, # dark mode
    f: bool | None = None, # fullscreen # TODO
    t: str | None = None, # Token for using custom data: allow users to pass a custom token, which won't be stored, via a parameter when using public devices. For personal devices, enable persistent settings using `custom_token`.
    k: bool | None = True, # keep valid specified parameters in history
    m: bool | None = True, # display menu
    l: int | None = None, # layout; either: 1 (bible area only) or 2 (bible & tool areas) or 3 (tool area only)
    bbt: str | None = None, # bible bible text
    bb: int | None = None, # bible book
    bc: int | None = None, # bible chapter
    bv: int | None = None, # bible verse
    tbt: str | None = None, # tool bible text
    tb: int | None = None, # tool book
    tc: int | None = None, # tool chapter
    tv: int | None = None, # tool verse
    tool: str | None = None, # supported options: bible, ...
):
    """
    Home page that accepts optional parameters.
    Example: /?bb=1&bc=1&bv=1
    """

    def set_default_settings():
        """Sets the default settings in app.storage.user if they don't already exist."""
        for key, value in USER_DEFAULT_SETTINGS.items():
            if key not in app.storage.user:
                app.storage.user[key] = value

    # Call this once on startup to populate the default user storage
    set_default_settings()

    # Bind app state to user storage
    ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
    ui.fullscreen().bind_value(app.storage.user, 'fullscreen')

    if d is not None:
        app.storage.user['dark_mode'] = d
    if f is not None:
        app.storage.user['fullscreen'] = f

    # manage custom resources
    if not config.custom_token or (t and t == config.custom_token) or (app.storage.user.setdefault('custom_token', "") == config.custom_token):
        app.storage.client["custom"] = True # short-term memory (single page visit)
    else:
        app.storage.client["custom"] = False

    if l is not None and l in (1, 2, 3):
        app.storage.user['layout'] = l
    else:
        l = app.storage.user.setdefault('layout', 2)

    if bbt is not None:
        app.storage.user['bible_book_text'] = bbt
    else:
        bbt = app.storage.user.setdefault('bible_book_text', "NET")
    if bb is not None:
        app.storage.user['bible_book_number'] = bb
    else:
        bb = app.storage.user.setdefault('bible_book_number', 1)
    if bc is not None:
        app.storage.user['bible_chapter_number'] = bc
    else:
        bc = app.storage.user.setdefault('bible_chapter_number', 1)
    if bv is not None:
        app.storage.user['bible_verse_number'] = bv
    else:
        bv = app.storage.user.setdefault('bible_verse_number', 1)
    if tbt is not None:
        app.storage.user['tool_book_text'] = tbt
    else:
        tbt = app.storage.user.setdefault('tool_book_text', "KJV")
    if tb is not None:
        app.storage.user['tool_book_number'] = tb
    else:
        tb = app.storage.user.setdefault('tool_book_number', 1)
    if tc is not None:
        app.storage.user['tool_chapter_number'] = tc
    else:
        tc = app.storage.user.setdefault('tool_chapter_number', 1)
    if tv is not None:
        app.storage.user['tool_verse_number'] = tv
    else:
        tv = app.storage.user.setdefault('tool_verse_number', 1)
        
    gui = BibleMateGUI()
    
    # navigation menu
    if m:
        gui.create_menu() # Add the shared menu
    # main content
    gui.create_home_layout()

    # load bible content at start
    if bb and bc and bv:
        next_tab_num = gui.area1_tab_loaded + 1
        if next_tab_num > gui.area1_tab_counter:
            gui.add_tab_area1()
        gui.load_area_1_content(title=bbt, keep=k)
    elif not gui.area1_tab_loaded: # when nothing is loaded
        gui.load_area_1_content(title="NET")
    
    # load tool content at start
    if tool:
        next_tab_num = gui.area2_tab_loaded + 1
        if next_tab_num > gui.area2_tab_counter:
            gui.add_tab_area2()
        gui.load_area_2_content(title=tbt if tool == "bible" else tool, keep=k)
    elif not gui.area2_tab_loaded: # when nothing is loaded
        ... # TODO - decides later

# Settings

"""
@ui.page('/settings')
def page_Settings(q: str | None = None, m: bool = True):
    if m:
        BibleMateGUI().create_menu()
    ...
"""

@ui.page('/settings')
def page_Settings():
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
                    .bind_value(app.storage.user, 'default_bible')

                ui.select(label='Default Commentary',
                          options=['CBSC', 'CBC', 'Calvin']) \
                    .bind_value(app.storage.user, 'default_commentary')

                ui.select(label='Default Encyclopedia',
                          options=['ISBE', 'Hasting', 'Kitto']) \
                    .bind_value(app.storage.user, 'default_encyclopedia')

                ui.select(label='Default Lexicon',
                          options=['Morphology', 'Strong', 'HALOT', 'BDAG']) \
                    .bind_value(app.storage.user, 'default_lexicon')

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
        ui.button('Home', on_click=lambda: ui.navigate.to('/')) \
            .classes('mt-6 w-full py-3 bg-blue-600 text-white rounded-lg font-semibold') \
            .tooltip('All settings are saved automatically as you change them. Click this to open the home page.')

# Entry_point

def main():
    # --- Run the App ---
    # Make sure to replace the secret!
    ui.run(
        reload=config.hot_reload,
        storage_secret=config.storage_secret, # e.g. generate one by running `openssl rand -hex 32` or `openssl rand -base64 32`
        port=config.port,
        title='BibleMate AI',
        favicon=os.path.expanduser(config.avatar) if config.avatar else os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')
    )

main()
#!/usr/bin/env python3
from nicegui import ui, app
from biblemategui import config, BIBLEMATEGUI_APP_DIR, USER_DEFAULT_SETTINGS, getBibleVersionList, getLexiconList
from biblemategui.pages.home import *
from biblemategui.js.tooltip import TOOLTIP_JS
from biblemategui.css.original import get_original_css
from biblemategui.css.tooltip import get_tooltip_css
from biblemategui.fx.tooltips import get_tooltip_data
from biblemategui.api.api import get_api_content
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os

# --- 2. OAUTH SETUP ---
app.add_middleware(SessionMiddleware, secret_key=config.storage_secret)
oauth = OAuth()
oauth.register(
    name='google',
    client_id=config.google_client_id,
    client_secret=config.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/drive.appdata openid email profile',
        'prompt': 'consent',      # <--- FORCE new refresh token
    }, 
    # This is critical for the error you saw:
    authorize_params={'access_type': 'offline'}
)

@app.get('/api/data')
def api_data(query: str, language: str = 'eng', token: Optional[str] = None):
    """
    Endpoint for BibleMate AI.
    - query: Required (automatically required because no default value is provided)
    - token: Optional (defaults to None)
    """
    custom = True if token == config.custom_token else False
    result = {
        "query": query,
        "custom": custom,
        "content": get_api_content(query, language, custom)
    }
    return result

# API endpoint for tooltip data
@app.get('/api/tooltip/{word}')
async def tooltip_api(word: str):
    data = get_tooltip_data(word)
    if data:
        return data
    return {'error': 'Not found'}, 404

@ui.page('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@ui.page('/auth')
async def auth(request: Request):
    try:
        # access_type='offline' in config ensures we get a refresh_token here
        token = await oauth.google.authorize_access_token(request)
        app.storage.user['google_token'] = token
        return RedirectResponse('/')
    except Exception as e:
        ui.notify(f"Login failed: {e}")
        return RedirectResponse('/')

# Home Page
@ui.page('/')
def page_home(
    pc: str | None = None, # primary color
    sc: str | None = None, # secondary color
    nc: str | None = None, # negative color
    fs: int | None = None, # font size in %
    s: bool | None = None, # sync
    d: bool | None = None, # dark mode
    t: str | None = None, # Token for using custom data: allow users to pass a custom token, which won't be stored, via a parameter when using public devices. For personal devices, enable persistent settings using `custom_token`.
    k: bool | None = True, # keep valid specified parameters in history
    m: bool | None = True, # display menu
    l: int | None = None, # layout; either: 1 (bible area only) or 2 (bible & tool areas) or 3 (tool area only)
    lang: str | None = None, # language
    bbt: str | None = None, # bible bible text
    bb: int | None = None, # bible book
    bc: int | None = None, # bible chapter
    bv: int | None = None, # bible verse
    tbt: str | None = None, # tool bible text
    tb: int | None = None, # tool book
    tc: int | None = None, # tool chapter
    tv: int | None = None, # tool verse
    tool: str | None = None, # supported options: bible, audio, chronology, search ...
    bq: str | None = None, # bible query; currently not in use
    tq: str | None = None, # tool query
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

    # spacing
    ui.query('.nicegui-content').classes('w-full h-full !p-0 !b-0 !m-0 !gap-0')

    # language
    if lang and lang in ('eng', 'tc', 'sc'):
        app.storage.user["ui_language"] = lang

    # font-size
    if fs:
        app.storage.user["font_size"] = fs
    ui.add_css(f"""
        /* This targets the root HTML element and sets its font size */
        html {{
            font-size: {app.storage.user['font_size']}%;
        }}
        .full-height-textarea .q-field__control,
        .full-height-textarea .q-field__native {{
            height: 100%;
            max-height: 100%;
        }}
    """)

    # colors
    if pc:
        app.storage.user["primary_color"] = pc
    if sc:
        app.storage.user["secondary_color"] = sc
    if nc:
        app.storage.user["negative_color"] = nc
    ui.colors(primary=app.storage.user["primary_color"], secondary=app.storage.user["secondary_color"], negative=app.storage.user["negative_color"])

    # sync
    if s is not None:
        app.storage.user['sync'] = s
    else:
        s = app.storage.user.setdefault('sync', True)

    # Bind app state to user storage
    app.storage.user["fullscreen"] = False
    ui.fullscreen().bind_value(app.storage.user, 'fullscreen')
    ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
    if d is not None:
        app.storage.user['dark_mode'] = d

    # manage custom resources
    if not config.custom_token or (t and t == config.custom_token) or (app.storage.user.setdefault('custom_token', "") == config.custom_token):
        app.storage.client["custom"] = True # short-term memory (single page visit)
    else:
        app.storage.client["custom"] = False

    if l is not None and l in (1, 2, 3):
        app.storage.user['layout'] = l
    else:
        l = app.storage.user.setdefault('layout', 2)

    if bq is not None:
        app.storage.user['bible_query'] = bq
    else:
        app.storage.user['bible_query'] = bq = "" # reset bible query
    if tq is not None:
        app.storage.user['tool_query'] = tq
    else:
        app.storage.user['tool_query'] = tq = "" # reset tool query

    load_bible_at_start = False
    if bbt is not None:
        load_bible_at_start = True
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

    ui.add_head_html(f'''
        <style>
            /* Define the font family */
            @font-face {{
                font-family: 'Ezra SIL';
                src: url('/fonts/sileot.ttf') format('truetype');
            }}
            @font-face {{
                font-family: 'KoineGreek';
                src: url('/fonts/KoineGreek.ttf') format('truetype');
            }}
            /* Hebrew Word Layer */
            heb, bdbheb, bdbarc, hu {{
                font-family: 'Ezra SIL', serif;
                font-size: 1.6rem;
                direction: rtl;
                display: inline-block;
                line-height: 1.2em;
                margin-top: 0;
                margin-bottom: -2px;
                cursor: pointer;
            }}
            /* Greek Word Layer (targets <grk> tag) */
            grk, gu {{
                font-family: 'SBL Greek', 'Galatia SIL', 'Times New Roman', serif;
                font-size: 1.6rem;
                direction: ltr;
                display: inline-block;
                line-height: 1.2em;
                margin-top: 0;
                margin-bottom: -2px;
                cursor: pointer;
            }}
            /* Greek Word Layer (targets <kgrk> tag) */
            kgrk {{
                font-family: 'KoineGreek', serif;
                font-size: 1.6rem;
                direction: ltr;
                display: inline-block;
                line-height: 1.2em;
                margin-top: 0;
                margin-bottom: -2px;
                cursor: pointer;
            }}
            /* Lexical Form (lemma) & Strong's Number Layers */
            wlex {{
                display: block;
                font-size: 1rem;
                cursor: pointer;
            }}
            h1 {{
                font-size: 2.0rem;
                color: {app.storage.user['primary_color']};
            }}
            h2 {{
                font-size: 1.7rem;
                color: {app.storage.user['secondary_color']};
            }}
            h3 {{
                font-size: 1.5rem;
            }}
            /* Main container for the Bible text - ensures RTL flow for verses */
            .bible-text-heb {{
                direction: rtl;
                font-family: sans-serif;
                padding: 0px;
                margin: 0px;
            }}
            /* Main container for the Bible text - LTR flow for Greek */
            .bible-text-grk {{
                direction: ltr;
                font-family: sans-serif;
                padding: 0px;
                margin: 0px;
            }}
            /* Main container for the Bible text - LTR flow for General Text */
            .bible-text {{
                direction: ltr;
                font-family: sans-serif;
                font-size: 1.3rem;
                padding: 0px;
                margin: 0px;
            }}
            /* Main container for the Tool text - ensures RTL flow for verses */
            .content-text {{
                direction: ltr;
                font-family: sans-serif;
                font-size: 1.1rem;
                padding: 0px;
                margin: 0px;
            }}
            /* Verse ID Number */
            vid {{
                color: {'#f2c522' if app.storage.user['dark_mode'] else 'navy'};
                font-weight: bold;
                font-size: 0.9rem;
                cursor: pointer;
                vertical-align: top;
            }}
        </style>
    ''')
    ui.add_head_html(get_original_css(app.storage.user['dark_mode']))
    ui.add_head_html(get_tooltip_css(app.storage.user["dark_mode"]))
    ui.add_body_html(TOOLTIP_JS)

    # GUI object
    gui = BibleMateGUI()
    # navigation menu
    if m:
        gui.create_menu() # Add the shared menu
    # main content
    gui.create_home_layout()

    # load bible content at start
    if load_bible_at_start:
        #gui.select_empty_area1_tab()
        gui.load_area_1_content(title=bbt, keep=k, update_url=False)
    elif not gui.area1_tab_loaded: # when nothing is loaded
        gui.load_area_1_content(title=app.storage.user["primary_bible"], update_url=False)

    # load tool content at start
    if tool:
        #gui.select_empty_area2_tab()
        gui.load_area_2_content(title=tbt if tool == "bible" else tool, keep=k, sync=s, update_url=False)
    elif not gui.area2_tab_loaded: # when nothing is loaded
        gui.load_area_2_content(title="Audio", sync=True, update_url=False)

    if k:
        # update storage based on latest loaded content
        active_area1_tab = gui.get_active_area1_tab()
        if active_area1_tab in app.storage.user:
            args = app.storage.user[active_area1_tab]
            app.storage.user['bible_book_text'] = args.get('bt', app.storage.user["primary_bible"])
            app.storage.user['bible_book_number'] = args.get('b', 1)
            app.storage.user['bible_chapter_number'] = args.get('c', 1)
            app.storage.user['bible_verse_number'] = args.get('v', 1)
            app.storage.user['bible_query'] = args.get('q', '')

        active_area2_tab = gui.get_active_area2_tab()
        if active_area2_tab in app.storage.user:
            args = app.storage.user[active_area2_tab]
            app.storage.user['tool_book_text'] = args.get('bt', app.storage.user["primary_bible"])
            app.storage.user['tool_book_number'] = args.get('b', 1)
            app.storage.user['tool_chapter_number'] = args.get('c', 1)
            app.storage.user['tool_verse_number'] = args.get('v', 1)
            app.storage.user['tool_query'] = args.get('q', '')
    
    gui.swap_layout(l)

    # capture text selection changes
    ui.add_body_html('''
    <script>
    document.addEventListener('selectionchange', () => {
        const selection = window.getSelection().toString();
        if (selection) {
            emitEvent('selection_changed', { text: selection });
        }
    });
    </script>
    ''')

    async def on_selection(e):
        app.storage.user['tool_query'] = e.args['text']
        #print(f"Selected: {app.storage.user['tool_query']}")

    ui.on('selection_changed', on_selection)

    # update url
    ui.timer(0, gui.replace_url, once=True)
    # Add a JavaScript listener for the 'popstate' event (Back/Forward button)
    ui.add_head_html('''
        <script>
            window.addEventListener('popstate', () => {
                window.location.reload();
            });
        </script>
    ''')

# Settings
@ui.page('/settings')
def page_Settings(
    t: str | None = None, # Token for using custom data: allow users to pass a custom token, which won't be stored, via a parameter when using public devices. For personal devices, enable persistent settings using `custom_token`.
):
    """The main settings page for the BibleMate AI app."""
    def set_default_settings():
        """Sets the default settings in app.storage.user if they don't already exist."""
        for key, value in USER_DEFAULT_SETTINGS.items():
            if key not in app.storage.user:
                app.storage.user[key] = value
    # We can call this again to be safe, especially if new settings are added in updates.
    set_default_settings()

    # Adjust font-size
    ui.run_javascript(f"document.documentElement.style.fontSize = '{app.storage.user['font_size']}%'")
    def set_font_size(value):
        # Update the storage (automatic via bind, but good for explicit logic if needed later)
        app.storage.user['font_size'] = value
        # Update the HTML root element immediately via JS
        ui.run_javascript(f"document.documentElement.style.fontSize = '{value}%'")

    # primary color
    ui.colors(primary=app.storage.user["primary_color"], secondary=app.storage.user["secondary_color"], negative=app.storage.user["negative_color"])

    # manage custom resources
    if not config.custom_token or (t and t == config.custom_token) or (app.storage.user.setdefault('custom_token', "") == config.custom_token):
        app.storage.client["custom"] = True # short-term memory (single page visit)
    else:
        app.storage.client["custom"] = False

    # Bind app state to user storage
    ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
    app.storage.user["fullscreen"] = False
    ui.fullscreen().bind_value(app.storage.user, 'fullscreen')

    with ui.card().classes('w-full max-w-2xl mx-auto p-6 shadow-xl rounded-lg'):
        ui.label('BibleMate AI Settings').classes('text-3xl font-bold text-secondary mb-6')
        
        # --- Appearance Section ---
        with ui.expansion('Appearance', icon='palette').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4'):
                # font-size
                with ui.row().classes('w-full items-center'):
                    ui.label("Font Size").classes('flex items-center font-bold mr-4')
                    # We display the current % value next to the label for clarity
                    ui.label().bind_text_from(app.storage.user, 'font_size', backward=lambda v: f'{int(v)}%').classes('text-sm text-gray-500')
                ui.slider(min=50, max=200, step=5, value=app.storage.user['font_size']) \
                    .bind_value(app.storage.user, 'font_size') \
                    .on_value_change(lambda e: set_font_size(e.value)) \
                    .props('label-always color=primary') \
                    .classes('w-full mb-4') \
                    .tooltip('Adjust the global font size (50% to 200%)')
                # colors
                ui.color_input(label='Primary Color') \
                    .bind_value(app.storage.user, 'primary_color') \
                    .tooltip('Manual hex code or color picker for app theme.') \
                    .on_value_change(lambda e: ui.colors(primary=e.value))
                ui.color_input(label='Secondary Color') \
                    .bind_value(app.storage.user, 'secondary_color') \
                    .tooltip('Manual hex code or color picker for app theme.') \
                    .on_value_change(lambda e: ui.colors(secondary=e.value))
                ui.color_input(label='Negative Color') \
                    .bind_value(app.storage.user, 'negative_color') \
                    .tooltip('Manual hex code or color picker for app theme.') \
                    .on_value_change(lambda e: ui.colors(negative=e.value))
                # dark mode
                with ui.row().classes('w-full'):
                    ui.label("Dark Mode").classes('flex items-center')
                    ui.space()
                    ui.switch().bind_value(app.storage.user, 'dark_mode').tooltip('Toggle dark mode for the app.').on_value_change(lambda: ui.run_javascript('location.reload()'))
                # fullscreen
                with ui.row().classes('w-full'):
                    ui.label("Fullscreen").classes('flex items-center')
                    ui.space()
                    ui.switch().bind_value(app.storage.user, 'fullscreen').tooltip('Toggle fullscreen mode for the app.')

        # --- tab management ---
        with ui.expansion('Tabs Management', icon='tab').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4'):
                # Bible Tabs
                with ui.row().classes('w-full items-center'):
                    ui.label("Bible Tabs").classes('flex items-center font-bold mr-4')
                    # We display the current % value next to the label for clarity
                    ui.label().bind_text_from(app.storage.user, 'default_number_of_tabs1', backward=lambda v: str(v)).classes('text-sm text-gray-500')
                ui.slider(min=1, max=10, step=1, value=app.storage.user['default_number_of_tabs1']) \
                    .bind_value(app.storage.user, 'default_number_of_tabs1') \
                    .props('label-always color=primary') \
                    .classes('w-full mb-4') \
                    .tooltip('Adjust the number of bible tabs to be opened by default (3 to 10)')
                # Tools Tabs
                with ui.row().classes('w-full items-center'):
                    ui.label("Tool Tabs").classes('flex items-center font-bold mr-4')
                    # We display the current % value next to the label for clarity
                    ui.label().bind_text_from(app.storage.user, 'default_number_of_tabs2', backward=lambda v: str(v)).classes('text-sm text-gray-500')
                ui.slider(min=1, max=10, step=1, value=app.storage.user['default_number_of_tabs2']) \
                    .bind_value(app.storage.user, 'default_number_of_tabs2') \
                    .props('label-always color=primary') \
                    .classes('w-full mb-4') \
                    .tooltip('Adjust the number of tool tabs to be opened by default (3 to 10)')

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
        with ui.expansion('Frequently Used Resources', icon='book', value=True).classes('w-full rounded-lg'):
            # Use a grid for a more compact layout
            with ui.grid(columns=2).classes('w-full p-4 gap-4'):
                ui.select(label='Primary Bible',
                          options=getBibleVersionList(app.storage.client["custom"])) \
                    .bind_value(app.storage.user, 'primary_bible')
                ui.select(label='Secondary Bible',
                          options=getBibleVersionList(app.storage.client["custom"])) \
                    .bind_value(app.storage.user, 'secondary_bible')
                ui.select(label='Hebrew Lexicon',
                          options=getLexiconList(app.storage.client["custom"])) \
                    .bind_value(app.storage.user, 'hebrew_lexicon')
                ui.select(label='Greek Lexicon',
                          options=getLexiconList(app.storage.client["custom"])) \
                    .bind_value(app.storage.user, 'greek_lexicon')

        # --- Semantic Searches ---
        with ui.expansion('Semantic Searches', icon='search').classes('w-full rounded-lg'):
            with ui.column().classes('w-full p-4'):
                # Similar Entries
                with ui.row().classes('w-full items-center'):
                    ui.label("Similar Entries").classes('flex items-center font-bold mr-4')
                    # We display the current % value next to the label for clarity
                    ui.label().bind_text_from(app.storage.user, 'top_similar_entries', backward=lambda v: str(v)).classes('text-sm text-gray-500')
                ui.slider(min=3, max=30, step=1, value=app.storage.user['top_similar_entries']) \
                    .bind_value(app.storage.user, 'top_similar_entries') \
                    .props('label-always color=primary') \
                    .classes('w-full mb-4') \
                    .tooltip('Adjust the global top similar entries in a semantic search (3 to 30)')
                # Similar Verses
                with ui.row().classes('w-full items-center'):
                    ui.label("Similar Verses").classes('flex items-center font-bold mr-4')
                    # We display the current % value next to the label for clarity
                    ui.label().bind_text_from(app.storage.user, 'top_similar_verses', backward=lambda v: str(v)).classes('text-sm text-gray-500')
                ui.slider(min=5, max=100, step=1, value=app.storage.user['top_similar_verses']) \
                    .bind_value(app.storage.user, 'top_similar_verses') \
                    .props('label-always color=primary') \
                    .classes('w-full mb-4') \
                    .tooltip('Adjust the global top similar verses in a semantic search (5 to 100)')

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
                          options={'eng': 'English', 'tc': '繁體中文', 'sc': '简体中文'}) \
                    .bind_value(app.storage.user, 'ui_language')

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
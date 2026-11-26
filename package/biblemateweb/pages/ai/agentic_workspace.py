import importlib.util
import os
from urllib.parse import quote

from nicegui import app, ui
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemateweb import config, get_translation

WORKSPACE_BACKENDS = {
    'agy': {
        'label': 'Antigravity',
        'file': 'web_app_agy.py',
        'description': 'Signed-in Google subscription via Antigravity CLI',
    },
    'claude': {
        'label': 'Claude Code',
        'file': 'web_app_claude.py',
        'description': 'Signed-in Claude Code CLI',
    },
    'codex': {
        'label': 'Codex',
        'file': 'web_app_codex.py',
        'description': 'Signed-in OpenAI Codex CLI',
    },
    'grok': {
        'label': 'Grok Build',
        'file': 'web_app_grok.py',
        'description': 'Signed-in Grok Build CLI',
    },
    'gemini_api': {
        'label': 'Gemini API',
        'file': 'web_app_gemini_api_key.py',
        'description': 'google-antigravity SDK + GEMINI_API_KEY',
    },
}

_LOADED_MODULES = {}
_IMAGES_MOUNTED = False


def get_workspace_dir() -> str:
    """Return the configured biblemate-agentic-workspace directory."""
    return os.path.expanduser(os.environ.get('BIBLEMATE_WORKSPACE_DIR', '~/biblemate'))


def get_available_workspace_backends() -> dict:
    """Return available workspace backends whose web_app_*.py files exist."""
    workspace_dir = get_workspace_dir()
    if not os.path.isdir(workspace_dir):
        return {}
    available = {}
    for key, meta in WORKSPACE_BACKENDS.items():
        if os.path.isfile(os.path.join(workspace_dir, meta['file'])):
            available[key] = meta
    return available


def get_default_workspace_backend(available: dict | None = None) -> str | None:
    """Return 'agy' if available, otherwise the first available backend."""
    if available is None:
        available = get_available_workspace_backends()
    if not available:
        return None
    if 'agy' in available:
        return 'agy'
    return next(iter(available))


def is_custom_data_accessible(token: str | None = None) -> bool:
    """Return True when custom data is accessible for the current user/session."""
    if not config.custom_token:
        return True
    if token and token == config.custom_token:
        return True
    try:
        if app.storage.client.get('custom', False):
            return True
    except Exception:
        pass
    try:
        if app.storage.user.get('custom_token', '') == config.custom_token:
            return True
    except Exception:
        pass
    return False


def is_workspace_available() -> bool:
    """Return True if custom data is accessible and at least one workspace web app file is detected."""
    return is_custom_data_accessible() and bool(get_available_workspace_backends())


def ensure_workspace_images_mounted() -> None:
    """Mount ~/biblemate/images on /images once when needed."""
    global _IMAGES_MOUNTED
    if _IMAGES_MOUNTED:
        return
    images_dir = os.path.join(get_workspace_dir(), 'images')
    os.makedirs(images_dir, exist_ok=True)
    app.add_static_files('/images', images_dir)
    _IMAGES_MOUNTED = True


def load_workspace_module(backend: str):
    """Lazily load and cache the requested workspace backend module."""
    available = get_available_workspace_backends()
    if backend not in available:
        return None, f"Backend '{backend}' is not installed in {get_workspace_dir()}."

    if backend in _LOADED_MODULES:
        mod = _LOADED_MODULES[backend]
        return mod, getattr(mod, 'BACKEND_ERROR', None)

    file_path = os.path.join(get_workspace_dir(), available[backend]['file'])
    ensure_workspace_images_mounted()

    spec = importlib.util.spec_from_file_location(f'biblemate_workspace_{backend}', file_path)
    if spec is None or spec.loader is None:
        return None, f"Could not create module spec for {file_path}."

    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit as exc:
        return None, f"Workspace backend '{backend}' exited during load (code {exc.code})."
    except Exception as exc:
        return None, f"Failed to load '{available[backend]['file']}': {exc}"

    _LOADED_MODULES[backend] = mod
    return mod, getattr(mod, 'BACKEND_ERROR', None)


def render_workspace_error(title: str, message: str, dark_mode: bool = True) -> None:
    """Render a friendly setup/status card when a backend cannot be started."""
    ui.dark_mode(value=dark_mode)
    with ui.column().classes('w-full min-h-screen items-center justify-center p-8 gap-4'):
        ui.icon('terminal', size='56px').classes('text-primary')
        ui.label(title).classes('text-2xl font-bold text-secondary')
        with ui.card().classes('w-full max-w-xl p-6'):
            ui.label(message).classes('text-base leading-relaxed')
            ui.label(f'Workspace path: {get_workspace_dir()}').classes('text-xs opacity-70 mt-3')


def render_workspace_page(backend: str | None = None, ref: str = '', dark: bool | None = None, t: str | None = None) -> None:
    """Render the standalone/embedded NiceGUI workspace app for the selected backend."""
    dark_mode = app.storage.user.get('dark_mode', True) if dark is None else bool(dark)
    if not is_custom_data_accessible(t):
        render_workspace_error(
            'Studio Mode Unavailable',
            'Custom data access is required to use Studio Mode. Please configure a valid custom token.',
            dark_mode=dark_mode,
        )
        return

    available = get_available_workspace_backends()
    if not available:
        render_workspace_error(
            'Studio Mode Not Found',
            'No web_app_*.py files were detected in ~/biblemate. Install biblemate-agentic-workspace first.',
            dark_mode=dark_mode,
        )
        return

    if not backend or backend not in available:
        backend = get_default_workspace_backend(available)

    mod, err = load_workspace_module(backend)
    if err or mod is None:
        label = available.get(backend, {}).get('label', backend)
        render_workspace_error(f'{label} Unavailable', err or 'Unknown error.', dark_mode=dark_mode)
        return

    app_instance = mod.BibleMateApp()
    app_instance.build_ui(dark_mode=dark_mode, initial_ref=ref, embedded=True)
    _apply_biblemateweb_theme(dark_mode=dark_mode)
    if getattr(app_instance, 'message_input', None) is not None:
        app_instance.message_input.props('dense rows=1')
        if ref:
            app_instance.message_input.props(f'placeholder="Ask about {ref} (or any Bible topic)..."')
    if getattr(app_instance, 'action_button', None) is not None:
        app_instance.action_button.props('size=sm dense', remove='size=lg').classes(remove='mb-1')


def _apply_biblemateweb_theme(dark_mode: bool = True) -> None:
    """Align the embedded workspace palette with biblemateweb's dark/light theme."""
    primary = app.storage.user.get('primary_color', '#827e67')
    secondary = app.storage.user.get('secondary_color', '#c7c279')
    negative = app.storage.user.get('negative_color', '#ff384f')
    ui.colors(
        primary=primary,
        secondary=secondary,
        accent=secondary,
        negative=negative,
        dark='#1d1d1d',
        dark_page='#121212',
    )
    ui.add_css(
        """
        .nicegui-content {
            padding: 0 !important;
        }
        .q-header {
            padding: 2px 12px !important;
            min-height: 42px !important;
        }
        .q-footer {
            padding: 4px 12px !important;
        }
        .q-btn.send-button {
            width: 34px !important;
            height: 34px !important;
            min-width: 34px !important;
            min-height: 34px !important;
            margin-bottom: 0 !important;
        }
        """
    )
    if not dark_mode:
        return
    ui.add_css(
        f"""
        body.body--dark {{
            --theme-bg: #121212;
            --theme-panel: #1d1d1d;
            --theme-inset: #272727;
            --theme-text: #e5e5e5;
            --theme-muted: #a8a492;
            --theme-border: #333333;
            --theme-link: {secondary};
            --theme-selection: #3a382c;
            --q-primary: {primary} !important;
            --q-secondary: {secondary} !important;
            --q-accent: {secondary} !important;
            --q-negative: {negative} !important;
        }}
        body.body--dark .q-tab--active {{
            color: {secondary} !important;
        }}
        body.body--dark .q-btn.send-button:not(.bg-negative) {{
            background: {primary};
            color: #ffffff;
            border-color: {secondary};
        }}
        """
    )


def ai_agentic_workspace(gui=None, **kwargs):
    """Tool-tab view in BibleMateWeb that embeds the selected AI Workspace backend."""
    if gui is not None and getattr(gui, '_pane_state', None) is None:
        tab_id = kwargs.get('tab2') or gui.get_active_area2_tab()
        panel = gui.area2_tab_panels.get(tab_id)
        if panel is not None:
            panel.classes(add='book-fill studio-fill')

    if not is_custom_data_accessible():
        with ui.column().classes('w-full items-center justify-center p-8 gap-4'):
            ui.icon('lock', size='56px').classes('text-primary')
            ui.label(get_translation('Studio Mode')).classes('text-2xl font-bold text-secondary')
            with ui.card().classes('w-full max-w-lg p-6'):
                ui.label('Custom data access is required to use Studio Mode. Please configure a valid custom token in Settings.')
        return

    available = get_available_workspace_backends()
    if not available:
        with ui.column().classes('w-full items-center justify-center p-8 gap-4'):
            ui.icon('terminal', size='56px').classes('text-primary')
            ui.label(get_translation('Studio Mode')).classes('text-2xl font-bold text-secondary')
            with ui.card().classes('w-full max-w-lg p-6'):
                ui.markdown(
                    'No `web_app_*.py` files were found in `~/biblemate`.\n\n'
                    'Install [biblemate-agentic-workspace](https://github.com/eliranwong/biblemate-agentic-workspace) '
                    'into `~/biblemate` to use this feature.'
                )
        return

    selected_backend = app.storage.user.get('workspace_backend')
    if selected_backend not in available:
        selected_backend = get_default_workspace_backend(available)
        app.storage.user['workspace_backend'] = selected_backend

    b = kwargs.get('b') or app.storage.user.get('bible_book_number', 1)
    c = kwargs.get('c') or app.storage.user.get('bible_chapter_number', 1)
    v = kwargs.get('v') or app.storage.user.get('bible_verse_number', 1)
    try:
        ref = BibleVerseParser(False, language=app.storage.user.get('ui_language', 'eng')).bcvToVerseReference(b, c, v)
    except Exception:
        ref = ''

    dark_val = 1 if app.storage.user.get('dark_mode', True) else 0

    def build_iframe_url(backend_key: str) -> str:
        url = f'/agentic-workspace?backend={quote(backend_key)}&ref={quote(ref)}&dark={dark_val}'
        if config.custom_token and app.storage.user.get('custom_token', '') != config.custom_token:
            url += f'&t={quote(config.custom_token)}'
        return url

    options = {k: meta['label'] for k, meta in available.items()}

    with ui.column().classes('w-full h-full no-wrap gap-0').style('height: 100%; min-height: 100%; overflow: hidden;'):
        with ui.row().classes('w-full items-center justify-between px-2 py-0.5 border-b gap-2 flex-wrap').style('flex: 0 0 auto; min-height: 42px;'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('smart_toy', size='sm').classes('text-secondary')
                ui.label(get_translation('Studio Mode')).classes('font-semibold text-secondary')
                if ref:
                    ui.chip(ref, icon='menu_book').props('dense outline size=sm')

            with ui.row().classes('items-center gap-2'):
                iframe_holder = {'el': None}

                def on_backend_change(e):
                    new_backend = e.value
                    if new_backend in available:
                        app.storage.user['workspace_backend'] = new_backend
                        if iframe_holder['el'] is not None:
                            iframe_holder['el'].props(f'src="{build_iframe_url(new_backend)}"')

                ui.select(
                    options=options,
                    value=selected_backend,
                    on_change=on_backend_change,
                ).props('dense outlined options-dense').classes('min-w-[170px]')

                def reload_iframe():
                    cur = app.storage.user.get('workspace_backend', selected_backend)
                    if iframe_holder['el'] is not None:
                        iframe_holder['el'].props(f'src="{build_iframe_url(cur)}"')

                ui.button(icon='refresh', on_click=reload_iframe).props('flat dense round').tooltip(get_translation('Reload'))
                ui.button(
                    icon='open_in_new',
                    on_click=lambda: ui.navigate.to(build_iframe_url(app.storage.user.get('workspace_backend', selected_backend)), new_tab=True),
                ).props('flat dense round').tooltip(get_translation('Open in new tab'))

        iframe_holder['el'] = ui.element('iframe').props(
            f'src="{build_iframe_url(selected_backend)}"'
        ).classes('w-full flex-1 border-0').style('width: 100%; height: 100%; min-height: 0; flex: 1 1 auto; display: block;')

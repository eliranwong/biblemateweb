import os, traceback, re, apsw, base64, io, qrcode
from nicegui import app, ui
from functools import partial

from biblemategui import config, BIBLEMATEGUI_APP_DIR, getBibleVersionList, get_translation

from biblemategui.pages.ai.chat import ai_chat
from biblemategui.pages.ai.partner import ai_partner
from biblemategui.pages.ai.agent import ai_agent

from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemategui.fx.bible_selection_dialog import BibleSelectionDialog

from biblemategui.js.bible import BIBLE_JS
from biblemategui.js.original import get_original_js

# Import for page content
from biblemategui.pages.bibles.original_reader import original_reader
from biblemategui.pages.bibles.original_interlinear import original_interlinear
from biblemategui.pages.bibles.original_parallel import original_parallel
from biblemategui.pages.bibles.original_discourse import original_discourse
from biblemategui.pages.bibles.original_linguistic import original_linguistic
from biblemategui.pages.bibles.bible_translation import bible_translation

from biblemategui.pages.tools.xrefs import xrefs
from biblemategui.pages.tools.treasury import treasury
from biblemategui.pages.tools.audio import bibles_audio
from biblemategui.pages.tools.podcast import bibles_podcast
from biblemategui.pages.tools.commentary import bible_commentary
from biblemategui.pages.tools.chronology import bible_chronology
from biblemategui.pages.tools.timelines import bible_timelines
from biblemategui.pages.tools.indexes import resource_indexes
from biblemategui.pages.tools.chapter_indexes import chapter_indexes
from biblemategui.pages.tools.promises import bible_promises_menu
from biblemategui.pages.tools.parallels import bible_parallels_menu
from biblemategui.pages.tools.morphology import word_morphology
from biblemategui.pages.tools.notepad import notepad
from biblemategui.pages.tools.notes import notes
from biblemategui.pages.tools.summary import chapter_summary
from biblemategui.pages.tools.analysis import book_analysis

from biblemategui.pages.search.bible_verses import search_bible_verses
from biblemategui.pages.search.bible_promises import search_bible_promises
from biblemategui.pages.search.bible_parallels import search_bible_parallels
from biblemategui.pages.search.bible_topics import search_bible_topics
from biblemategui.pages.search.bible_locations import search_bible_locations
from biblemategui.pages.search.bible_characters import search_bible_characters
from biblemategui.pages.search.bible_names import search_bible_names
from biblemategui.pages.search.dictionaries import search_bible_dictionaries
from biblemategui.pages.search.encyclopedias import search_bible_encyclopedias
from biblemategui.pages.search.lexicons import search_bible_lexicons
from biblemategui.pages.search.bible_maps import search_bible_maps
from biblemategui.pages.search.bible_relationships import search_bible_relationships

from biblemategui.pages.teachings.parousia import parousia
from biblemategui.pages.teachings.parousia_zh import parousia_zh

class BibleMateGUI:
    def __init__(self):

        # TODO: Consider dark mode latter
        # Dark Mode
        # ui.dark_mode().toggle()

        # Global variable to track current layout
        self.current_layout = app.storage.user['layout']
        self.area1_wrapper = None
        self.area2_wrapper = None
        self.splitter = None
        self.is_portrait = False

        # Tab panels and active tab tracking
        self.area1_tabs = None
        self.area2_tabs = None
        self.area1_tab_panels = {}  # Dictionary to store tab panels by name
        self.area2_tab_panels = {}
        self.area1_tab_panels_container = None
        self.area2_tab_panels_container = None

        # Tab number
        self.area1_tab_loaded = self.area1_tab_counter = 0
        self.area2_tab_loaded = self.area2_tab_counter = 0

        # tools
        self.tools = {
            "analysis": book_analysis,
            "summary": chapter_summary,
            "notes": notes,
            "notepad": notepad,
            "parousia": parousia,
            "parousia_zh": parousia_zh,
            "chat": ai_chat,
            "partner": ai_partner,
            "agent": ai_agent,
            "morphology": word_morphology,
            "indexes": resource_indexes,
            "chapterindexes": chapter_indexes,
            "podcast": bibles_podcast,
            "audio": bibles_audio,
            "verses": search_bible_verses, # API with additional options
            "treasury": treasury,
            "commentary": bible_commentary, # API with additional options
            "chronology": bible_chronology,
            "timelines": bible_timelines,
            "xrefs": xrefs,
            "promises": search_bible_promises,
            "promises_": bible_promises_menu,
            "parallels": search_bible_parallels,
            "parallels_": bible_parallels_menu,
            "topics": search_bible_topics,
            "characters": search_bible_characters,
            "locations": search_bible_locations,
            "names": search_bible_names,
            "dictionaries": search_bible_dictionaries,
            "encyclopedias": search_bible_encyclopedias, # API with additional options
            "lexicons": search_bible_lexicons, # API with additional options
            "maps": search_bible_maps,
            "relationships": search_bible_relationships,
        }

    def work_in_progress(self, **_):
        with ui.column().classes('w-full items-center'):
            ui.label('BibleMate AI').classes('text-2xl mt-4')
            ui.label('This feature is currently in progress.').classes('text-gray-600')
            ui.notify("This feature is currently in progress.")

    def check_breakpoint(self, ev):
        # prefer the well-known attributes
        # width
        width = getattr(ev, 'width', None)
        # fallback: some versions wrap data inside an attribute (try common names)
        if width is None:
            for maybe in ('args', 'arguments', 'data', 'payload'):
                candidate = getattr(ev, maybe, None)
                if isinstance(candidate, dict) and 'width' in candidate:
                    width = candidate['width']
                    break
        if width is None:
            print('Could not determine width from event:', ev)
            return
        # height
        height = getattr(ev, 'height', None)
        # fallback: some versions wrap data inside an attribute (try common names)
        if height is None:
            for maybe in ('args', 'arguments', 'data', 'payload'):
                candidate = getattr(ev, maybe, None)
                if isinstance(candidate, dict) and 'height' in candidate:
                    height = candidate['height']
                    break
        if height is None:
            print('Could not determine height from event:', ev)
            return
        self.is_portrait = width < height
        if self.splitter:
            if self.is_portrait:
                self.splitter.props('horizontal')
            else:
                self.splitter.props(remove='horizontal')

    def create_home_layout(self):
        """Create two scrollable areas with responsive layout"""
        
        # listen to the resize event
        ui.on('resize', self.check_breakpoint)
        
        # Inject JS
        ui.add_head_html('''
        <style>
            /* Make tab content area horizontal so close button is inline with label */
            .closable-tab .q-tab__content {
                flex-direction: row !important;
                align-items: center !important;
                gap: 2px;
            }
            /* Reduce tab padding for compactness */
            .closable-tab {
                padding-right: 6px !important;
            }
            /* Smaller close button */
            .closable-tab .close-btn {
                min-height: 18px !important;
                min-width: 18px !important;
                padding: 0 !important;
                margin-right: -4px !important;
            }
            .closable-tab .close-btn .q-icon {
                font-size: 12px !important;
            }
        </style>
        ''')
        ui.add_head_html(BIBLE_JS) # for active verse scrolling
        ui.add_head_html(get_original_js(app.storage.user['dark_mode'])) # for interactive highlighting

        # Create self.splitter
        self.splitter = ui.splitter(value=100, horizontal=self.is_portrait).classes('w-full').style('height: 100vh')

        # Area 1
        with self.splitter.before:
            previous_tabs1 = sorted([i for i in app.storage.user.keys() if i.startswith("tab1_")])
            default_number_of_tabs1 = app.storage.user.get("default_number_of_tabs1", 3)

            self.area1_wrapper = ui.column().classes('w-full h-full !gap-0')
            with self.area1_wrapper:
                self.area1_tabs = ui.tabs().classes('w-full')
                with self.area1_tabs:
                    if previous_tabs1:
                        for i in range(1, len(previous_tabs1)+1):
                            tab_id = f'tab1_{i}'
                            with ui.tab(f'tab1_{i}', label=app.storage.user.get(previous_tabs1[i-1]).get("label", f'Bible {i}')).classes('text-secondary closable-tab') as tab:
                                close_btn = ui.button(
                                    icon='close',
                                    on_click=partial(self.remove_tab_area1_any, tab_id),
                                ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
                                close_btn.on('click', js_handler='(e) => e.stopPropagation()')
                            self.area1_tab_counter += 1
                        self.area1_tab_loaded = self.area1_tab_counter
                    if len(previous_tabs1) < default_number_of_tabs1:
                        for i in range(len(previous_tabs1)+1, default_number_of_tabs1+1):
                            tab_id = f'tab1_{i}'
                            with ui.tab(tab_id, label=f'Bible {i}').classes('text-secondary closable-tab') as tab:
                                close_btn = ui.button(
                                    icon='close',
                                    on_click=partial(self.remove_tab_area1_any, tab_id),
                                ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
                                close_btn.on('click', js_handler='(e) => e.stopPropagation()')
                            self.area1_tab_counter += 1
                
                self.area1_tab_panels_container = ui.tab_panels(self.area1_tabs, value='tab1_1').classes('w-full h-full')
                
                with self.area1_tab_panels_container:

                    if previous_tabs1:
                        for i in range(1, len(previous_tabs1)+1):
                            tab_id = f'tab1_{i}'
                            saved_tab_id = previous_tabs1[i-1]
                            with ui.tab_panel(tab_id).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                                self.area1_tab_panels[tab_id] = ui.scroll_area().classes(f'w-full h-full {tab_id}')
                                with self.area1_tab_panels[tab_id]:
                                    args = app.storage.user.get(saved_tab_id)
                                    content = self.get_content(args.get("title"))
                                    if content is None and saved_tab_id in app.storage.user:
                                        app.storage.user.pop(saved_tab_id)
                                        continue
                                    args["tab1"] = tab_id
                                    content(gui=self, **args)
                                    if saved_tab_id != tab_id and saved_tab_id in app.storage.user:
                                        app.storage.user[tab_id] = app.storage.user.pop(saved_tab_id)
                    if len(previous_tabs1) < default_number_of_tabs1:
                        for i in range(len(previous_tabs1)+1, default_number_of_tabs1+1):
                            tab_id = f'tab1_{i}'
                            with ui.tab_panel(tab_id).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                                self.area1_tab_panels[tab_id] = ui.scroll_area().classes(f'w-full h-full {tab_id}')
                                with self.area1_tab_panels[tab_id]:
                                    ui.label(f'Bible Area - Tab {i}').classes('text-2xl font-bold mb-4')
                                    ui.label('Please select a Bible from the menu.').classes('text-gray-600')
        
        # Area 2
        with self.splitter.after:
            previous_tabs2 = sorted([i for i in app.storage.user.keys() if i.startswith("tab2_")])
            default_number_of_tabs2 = app.storage.user.get("default_number_of_tabs2", 3)

            self.area2_wrapper = ui.column().classes('w-full h-full !gap-0')
            with self.area2_wrapper:
                self.area2_tabs = ui.tabs().classes('w-full')
                with self.area2_tabs:
                    if previous_tabs2:
                        for i in range(1, len(previous_tabs2)+1):
                            tab_id = f'tab2_{i}'
                            with ui.tab(f'tab2_{i}', label=app.storage.user.get(previous_tabs2[i-1]).get("label", f'Tool {i}')).classes('text-secondary closable-tab') as tab:
                                close_btn = ui.button(
                                    icon='close',
                                    on_click=partial(self.remove_tab_area2_any, tab_id),
                                ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
                                close_btn.on('click', js_handler='(e) => e.stopPropagation()')
                            self.area2_tab_counter += 1
                        self.area2_tab_loaded = self.area2_tab_counter
                    if len(previous_tabs2) < default_number_of_tabs2:
                        for i in range(len(previous_tabs2)+1, default_number_of_tabs2+1):
                            tab_id = f'tab2_{i}'
                            with ui.tab(tab_id, label=f'Tool {i}').classes('text-secondary closable-tab') as tab:
                                close_btn = ui.button(
                                    icon='close',
                                    on_click=partial(self.remove_tab_area2_any, tab_id),
                                ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
                                close_btn.on('click', js_handler='(e) => e.stopPropagation()')
                            self.area2_tab_counter += 1
                
                self.area2_tab_panels_container = ui.tab_panels(self.area2_tabs, value='tab2_1').classes('w-full h-full')
                
                with self.area2_tab_panels_container:

                    if previous_tabs2:
                        for i in range(1, len(previous_tabs2)+1):
                            tab_id = f'tab2_{i}'
                            saved_tab_id = previous_tabs2[i-1]
                            with ui.tab_panel(tab_id).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                                self.area2_tab_panels[tab_id] = ui.scroll_area().classes(f'w-full h-full {tab_id}')
                                with self.area2_tab_panels[tab_id]:
                                    args = app.storage.user.get(previous_tabs2[i-1])
                                    content = self.get_content(args.get("title"))
                                    if content is None and saved_tab_id in app.storage.user:
                                        app.storage.user.pop(saved_tab_id)
                                        continue
                                    args["tab2"] = tab_id
                                    content(gui=self, **args)
                                    if saved_tab_id != tab_id and saved_tab_id in app.storage.user:
                                        app.storage.user[tab_id] = app.storage.user.pop(saved_tab_id)
                    if len(previous_tabs2) < default_number_of_tabs2:
                        for i in range(len(previous_tabs2)+1, default_number_of_tabs2+1):
                            tab_id = f'tab2_{i}'
                            with ui.tab_panel(tab_id).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                                self.area2_tab_panels[tab_id] = ui.scroll_area().classes(f'w-full h-full {tab_id}')
                                with self.area2_tab_panels[tab_id]:
                                    ui.label(f'Tool Area - Tab {i}').classes('text-2xl font-bold mb-4')
                                    ui.label('Please select a tool from the menu.').classes('text-gray-600')

        # A Draggable Container
        def make_draggable(element):
            """
            Applies drag-and-drop logic to any UI element.
            Snap-to-position on drag end.
            """
            def handle_drag_end(e):
                x = e.args['clientX']
                y = e.args['clientY']
                # Position element based on drop location, centered
                element.style(f'top: {y - 20}px; left: {x - 20}px; bottom: auto; right: auto')

            element.props('draggable="true"') \
                .style('cursor: grab') \
                .on('dragend', handle_drag_end, ['clientX', 'clientY'])
            return element

        with ui.column().classes('fixed bottom-6 right-6 z-50 touch-none') \
                .props('draggable="true"') \
                .style('cursor: grab') as self.fab_container1:
            make_draggable(self.fab_container1)
            self.fab_container1.bind_visibility_from(app.storage.user, 'layout_swap_button')

            # - 'fab-mini': Quasar's specific prop for a smaller floating action button.
            ui.button(icon='swap_horiz', on_click=self.swap_layout) \
                .props('fab-mini color=primary') \
                .tooltip(get_translation("Swap Layout"))

        BOOK_NAMES = {i: BibleBooks.abbrev[app.storage.user['ui_language']][str(i)][0] for i in range(1,67)}
        VERSES = BibleBooks.verses
        bible_selection_dialog = BibleSelectionDialog(self, BOOK_NAMES, VERSES)

        with ui.column().classes('fixed bottom-6 right-20 z-50 touch-none') \
                .props('draggable="true"') \
                .style('cursor: grab') as self.fab_container2:
            make_draggable(self.fab_container2)
            self.fab_container2.bind_visibility_from(app.storage.user, 'bible_select_button')

            # - 'fab-mini': Quasar's specific prop for a smaller floating action button.
            ui.button(icon='menu_book', on_click=bible_selection_dialog.open) \
                .props('fab-mini color=primary') \
                .tooltip(get_translation("Select Bible Verse"))

        # Set initial visibility
        self.update_visibility()

    def swap_layout(self, layout=None):
        """Swap between three layout modes"""
        if not layout in (1, 2, 3, None):
            layout = 2
        app.storage.user['layout'] = self.current_layout = layout if layout else (self.current_layout % 3) + 1
        self.update_visibility()

    def update_visibility(self):
        """Update visibility of areas based on current layout"""
        
        if self.current_layout == 1:
            # Area 1 visible, Area 2 invisible - maximize Area 1
            self.area1_wrapper.set_visibility(True)
            self.area2_wrapper.set_visibility(False)
            self.splitter.set_value(100)  # Move self.splitter to maximize Area 1
        elif self.current_layout == 2:
            # Both areas visible - 50/50 split
            self.area1_wrapper.set_visibility(True)
            self.area2_wrapper.set_visibility(True)
            self.splitter.set_value(50)  # Move self.splitter to middle
        elif self.current_layout == 3:
            # Area 1 invisible, Area 2 visible - maximize Area 2
            self.area1_wrapper.set_visibility(False)
            self.area2_wrapper.set_visibility(True)
            self.splitter.set_value(0)  # Move self.splitter to maximize Area 2

    def get_active_area1_tab(self):
        """Get the currently active tab in Area 1"""
        return self.area1_tab_panels_container.value

    def get_active_area2_tab(self):
        """Get the currently active tab in Area 2"""
        return self.area2_tab_panels_container.value

    def select_next_area1_tab(self, add_tab=True):
        if len(self.area1_tab_panels) == 1:
            if add_tab:
                self.add_tab_area1()
            else:
                return
        else:
            next_tab = False
            while not next_tab:
                for i in self.area1_tab_panels:
                    if next_tab:
                        self.area1_tab_panels_container.value = i
                        return None
                    elif i == self.area1_tab_panels_container.value:
                        next_tab = True

    def select_next_area2_tab(self, add_tab=True):
        if len(self.area2_tab_panels) == 1:
            if add_tab:
                self.add_tab_area2()
            else:
                return
        else:
            next_tab = False
            while not next_tab:
                for i in self.area2_tab_panels:
                    if next_tab:
                        self.area2_tab_panels_container.value = i
                        return None
                    elif i == self.area2_tab_panels_container.value:
                        next_tab = True

    def select_empty_area1_tab(self):
        for child in self.area1_tabs:
            if hasattr(child, '_props') and re.search("^Bible [0-9]", child._props.get('label', '')):
                if tab_name := child._props.get('name', ''):
                   self.area1_tab_panels_container.value = tab_name
                   return None
        self.add_tab_area1()

    def select_empty_area2_tab(self):
        for child in self.area2_tabs:
            if hasattr(child, '_props') and re.search("^Tool [0-9]", child._props.get('label', '')):
                if tab_name := child._props.get('name', ''):
                   self.area2_tab_panels_container.value = tab_name
                   return None
        self.add_tab_area2()

    def close_other_area1_tabs(self):
        keep_tab = self.area1_tab_panels_container.value
        for i in list(self.area1_tab_panels.keys()):
            if i != keep_tab:
                self.area1_tab_panels_container.value = i
                self.remove_tab_area1()

    def close_other_area2_tabs(self):
        keep_tab = self.area2_tab_panels_container.value
        for i in list(self.area2_tab_panels.keys()):
            if i != keep_tab:
                self.area2_tab_panels_container.value = i
                self.remove_tab_area2()

    def is_tool(self, title):
        return True if title.lower() in self.tools else False

    def get_content(self, title):
        if not isinstance(title, str):
            title = "NET"
        if title.lower() in self.tools:
            return self.tools[title.lower()]
        elif title == "ORB":
            return original_reader
        elif title == "OIB":
            return original_interlinear
        elif title == "OPB":
            return original_parallel
        elif title == "ODB":
            return original_discourse
        elif title == "OLB":
            return original_linguistic
        elif app.storage.client["custom"] and title in config.bibles_custom:
            return bible_translation
        elif title in config.bibles:
            return bible_translation
        else:
            return None

    def generate_qr_base64(self, data: str) -> str:
        """
        Generates a QR code for the given string and returns it 
        as a base64 encoded data URL for use in ui.image().
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image to a memory buffer (avoiding file creation)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # Return standard data URL format
        return f'data:image/png;base64,{img_str}'

    def copy_text(self, text=""):
        if text:
            # Escape quotes and newlines for JavaScript
            escaped = text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            ui.run_javascript(f'navigator.clipboard.writeText(`{escaped}`)')
            ui.notify(f'Copied: "{text}"')
        else:
            ui.notify('No text selected', type='warning')

    def add_to_notepad(self, context):
        app.storage.user["tool_query"] = context
        self.select_empty_area2_tab()
        self.load_area_2_content(title="note", sync=False)

    def ask_biblemate(self, context):
        app.storage.user["tool_query"] = context
        self.select_empty_area2_tab()
        self.load_area_2_content(title="chat", sync=False)

    def get_aic(self):
        if app.storage.user['ui_language'] == "tc":
            return "AICTC"
        elif app.storage.user['ui_language'] == "sc":
            return "AICSC"
        else:
            return "AIC"

    def open_book_context_menu(self, db, b, c, v, note=False):
        app.storage.user["tool_book_number"] = b
        app.storage.user["tool_chapter_number"] = c
        app.storage.user["tool_verse_number"] = v
        def open_tool(title):
            self.select_empty_area2_tab()
            self.load_area_2_content(title=title, sync=False)
        def open_analysis(section):
            app.storage.user["tool_query"] = section
            open_tool("Analysis")
        def open_book_note():
            app.storage.user["tool_chapter_number"] = 0
            app.storage.user["tool_verse_number"] = 0
            open_tool("Notes")
        with ui.context_menu() as menu:
            ui.menu_item(f'⏳ {get_translation("Timelines")}', on_click=lambda: open_tool("Timelines"))
            ui.separator()
            ui.menu_item(f'🔘 {get_translation("Overview")}', on_click=lambda: open_analysis("Overview"))
            ui.menu_item(f'📐 {get_translation("Structural Outline")}', on_click=lambda: open_analysis("Structural Outline"))
            ui.menu_item(f'🧵 {get_translation("Logical Flow")}', on_click=lambda: open_analysis("Logical Flow"))
            ui.menu_item(f'🕰️ {get_translation("Historical Setting")}', on_click=lambda: open_analysis("Historical Setting"))
            ui.menu_item(f'🎨 {get_translation("Themes")}', on_click=lambda: open_analysis("Themes"))
            ui.menu_item(f'🏷️ {get_translation("Keywords")}', on_click=lambda: open_analysis("Keywords"))
            ui.menu_item(f'⛪ {get_translation("Theology")}', on_click=lambda: open_analysis("Theology"))
            ui.menu_item(f'🚩 {get_translation("Canonical Placement")}', on_click=lambda: open_analysis("Canonical Placement"))
            ui.menu_item(f'🌱 {get_translation("Practical Living")}', on_click=lambda: open_analysis("Practical Living"))
            ui.menu_item(f'💎 {get_translation("Summary")}', on_click=lambda: open_analysis("Summary"))
            if config.google_client_id and config.google_client_secret:
                ui.separator()
                ui.menu_item(f'📝 {get_translation("Edit Note" if note else "Add Note")}', on_click=open_book_note)
        menu.open()

    def open_chapter_context_menu(self, db, b, c, v, note=False):
        app.storage.user["tool_book_number"] = b
        app.storage.user["tool_chapter_number"] = c
        app.storage.user["tool_verse_number"] = v
        def get_chapter_content():
            nonlocal b, c, v
            ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(b, c, v, isChapter=True)
            with apsw.Connection(db) as connn:
                query = "SELECT Verse, Scripture FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
                cursor = connn.cursor()
                cursor.execute(query, (b, c))
                fetches = cursor.fetchall()
            if not fetches: return ref
            verses = [f"[{verse}] {scripture}" for verse, scripture in fetches]
            return f"# {ref}\n\n" + "\n".join(verses)
        def open_tool(title):
            self.select_empty_area2_tab()
            self.load_area_2_content(title=title, sync=False)
        def open_map():
            nonlocal b, c, v
            ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(b, c, v, isChapter=True)
            app.storage.user["tool_query"] = f"{ref}:1-180"
            open_tool("Maps")
        def open_chapter_note():
            app.storage.user["tool_verse_number"] = 0
            open_tool("Notes")
        with ui.context_menu() as menu:
            ui.menu_item(f'📋 {get_translation("Copy")}', on_click=lambda: self.copy_text(get_chapter_content()))
            ui.separator()
            ui.menu_item(f'📡 {get_translation("Bible Podcast")}', on_click=lambda: open_tool("Podcast"))
            ui.menu_item(f'🔊 {get_translation("Bible Audio")}', on_click=lambda: open_tool("Audio"))
            ui.separator()
            ui.menu_item(f'💎 {get_translation("Chapter Summary")}', on_click=lambda: open_tool("Summary"))
            ui.menu_item(f'🗺️ {get_translation("Chapter Map")}', on_click=open_map)
            ui.menu_item(f'📑 {get_translation("Chapter Indexes")}', on_click=lambda: open_tool("Chapterindexes"))
            if config.google_client_id and config.google_client_secret:
                ui.separator()
                ui.menu_item(f'📝 {get_translation("Edit Note" if note else "Add Note")}', on_click=open_chapter_note)
        menu.open()

    def open_verse_context_menu(self, db, b, c, v, note=False):
        app.storage.user["tool_book_number"] = b
        app.storage.user["tool_chapter_number"] = c
        app.storage.user["tool_verse_number"] = v
        def get_verse_content():
            nonlocal b, c, v
            ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(b, c, v)
            with apsw.Connection(db) as connn:
                query = "SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse =?"
                cursor = connn.cursor()
                cursor.execute(query, (b, c, v))
                fetch = cursor.fetchone()
            verse_text = re.sub("<[^<>]+?>", "", fetch[0]) if fetch else ""
            return f"[{ref}] {verse_text}"
        def open_tool(title):
            self.select_empty_area2_tab()
            self.load_area_2_content(title=title, sync=False)
        def compare_verse():
            nonlocal db, b, c, v
            ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(b, c, v)
            bible_versions = sorted(list(set([app.storage.user["primary_bible"], app.storage.user["primary_bible"], os.path.basename(db)[:-6], "OHGBi"])))
            app.storage.user["tool_query"] = f"{','.join(bible_versions)}:::{ref}"
            open_tool("Verses")
        def add_to_notepad():
            nonlocal self
            self.add_to_notepad(get_verse_content())
        def ask_biblemate():
            nonlocal self
            ref, verse_content = get_verse_content()[1:].split("] ", 1)
            self.ask_biblemate(f"# {ref}\n\n{verse_content}\n\n# Query\n\n")
        with ui.context_menu() as menu:
            ui.menu_item(f'📋 {get_translation("Copy")}', on_click=lambda: self.copy_text(get_verse_content()))
            ui.separator()
            ui.menu_item(f'🔊 {get_translation("Bible Audio")}', on_click=lambda: open_tool("Audio"))
            ui.separator()
            ui.menu_item(f'🔗 {get_translation("Cross-references")}', on_click=lambda: open_tool("Xrefs"))
            ui.menu_item(f'🏦 {get_translation("Treasury")}', on_click=lambda: open_tool("Treasury"))
            ui.menu_item(f'🧠 {get_translation("AI Commentary")}', on_click=lambda: (
                app.storage.user.update(favorite_commentary=self.get_aic()),
                open_tool("Commentary")
            ))
            ui.menu_item(f'📚 {get_translation("Commentaries")}', on_click=lambda: open_tool("Commentary"))
            ui.separator()
            ui.menu_item(f'🧬 {get_translation("Morphology")}', on_click=lambda: open_tool("Morphology"))
            ui.separator()
            ui.menu_item(f'👀 {get_translation("Comparison")}', on_click=compare_verse)
            ui.menu_item(f'📑 {get_translation("Indexes")}', on_click=lambda: open_tool("Indexes"))
            ui.separator()
            if config.google_client_id and config.google_client_secret:
                ui.menu_item(f'📝 {get_translation("Edit Note" if note else "Add Note")}', on_click=lambda: open_tool("Notes"))
            else:
                ui.menu_item(f'📝 {get_translation("Add Note")}', on_click=add_to_notepad)
            ui.menu_item(f'💬 {get_translation("Ask BibleMate")}', on_click=ask_biblemate)
        menu.open()

    async def replace_url(self):
        new_url = ""
        active_bible_tab = self.get_active_area1_tab()
        if active_bible_tab in app.storage.user:
            args = app.storage.user[active_bible_tab]
            new_url = f'/?bbt={args.get("bt")}&bb={args.get("b")}&bc={args.get("c")}&bv={args.get("v")}'
        active_tool_tab = self.get_active_area2_tab()
        if active_tool_tab in app.storage.user:
            args = app.storage.user[active_tool_tab]
            title = args.get("bt")
            if not new_url:
                new_url = "/?"
            else:
                new_url += "&"
            new_url += f'tool={title if title.lower() in self.tools else "bible"}&tbt={args.get("bt")}&tb={args.get("b")}&tc={args.get("c")}&tv={args.get("v")}&tq={args.get("q")}'
        if new_url:
            new_url += f"&l={app.storage.user['layout']}"
        await ui.run_javascript(f"window.history.replaceState({{}}, '', '{new_url}')")

    def load_area_1_content(self, content=None, title="Bible", tab=None, args=None, keep=True, update_url=True):
        """Load example content in the active tab of Area 1"""

        if app.storage.user['layout'] == 3:
            self.swap_layout(2)

        if content is None:
            content = self.get_content(title)
            if content is None:
                print("No content found!")
                return None

        try:
            # modify tab label here for particular features TODO
            tab_label = title
            if not app.storage.user['bible_book_text'] == title:
                app.storage.user['bible_book_text'] = title
            # Get the currently active tab
            active_tab = tab if tab else self.get_active_area1_tab()
            # args holder
            args = args if args else {
                "title": title,
                "label": tab_label,
                "bt": app.storage.user.get('bible_book_text', app.storage.user["primary_bible"]),
                "b": app.storage.user.get('bible_book_number', 1),
                "c": app.storage.user.get('bible_chapter_number', 1),
                "v": app.storage.user.get('bible_verse_number', 1),
                "q": app.storage.user.get('bible_query', ''),
                "area": 1,
                "tab1": active_tab,
                "tab2": self.get_active_area2_tab(),
            }
            # store as history
            if update_url:
                with self.splitter: # attach to splitter to workaround `RuntimeError: The parent element this slot belongs to has been deleted.`
                    if client := ui.context.client:
                        new_url = f'/?bbt={args.get("bt")}&bb={args.get("b")}&bc={args.get("c")}&bv={args.get("v")}'
                        client.run_javascript(f"window.history.pushState({{}}, '', '{new_url}')")
                        ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(args.get("b"), args.get("c"), args.get("v"))
                        client.run_javascript(f'document.title = "[{title}] {ref}"')
            if keep:
                app.storage.user[active_tab] = args
            # Get the active tab's scroll area
            active_panel = self.area1_tab_panels[active_tab]
            # Clear and load new content
            active_panel.clear()
            # load content
            with active_panel:
                content(gui=self, **args)
            # Update tab label to reflect new content
            for child in self.area1_tabs:
                if hasattr(child, '_props') and child._props.get('name') == active_tab:
                    child.props(f'label="{tab_label}"')
                    break
            # reset bible query
            app.storage.user["bible_query"] = ""
        except:
            print(traceback.format_exc())

    def load_area_2_content(self, content=None, title="Tool", tab=None, args=None, keep=True, sync=True, update_url=True):
        """Load example content in the active tab of Area 2"""

        if app.storage.user['layout'] == 1:
            self.swap_layout(2)

        is_sync = True if sync or (sync and app.storage.user.get("sync") and not self.is_tool(title)) else False

        if content is None:
            content = self.get_content(title)
            if content is None:
                print("No content found!")
                return None

        try:
            # modify tab label here for particular features TODO
            tab_label = title
            # Get the currently active tab
            bible_tab = self.get_active_area1_tab()
            active_tab = tab if tab else self.get_active_area2_tab()
            # args holder
            sync_b = app.storage.user[bible_tab]["b"] if bible_tab in app.storage.user else app.storage.user.get('bible_book_number')
            sync_c = app.storage.user[bible_tab]["c"] if bible_tab in app.storage.user else app.storage.user.get('bible_chapter_number')
            sync_v = app.storage.user[bible_tab]["v"] if bible_tab in app.storage.user else app.storage.user.get('bible_verse_number')
            args = args if args else {
                "title": title,
                "label": tab_label,
                "bt": app.storage.user.get('tool_book_text'),
                "b": sync_b if is_sync else app.storage.user.get('tool_book_number'),
                "c": sync_c if is_sync else app.storage.user.get('tool_chapter_number'),
                "v": sync_v if is_sync else app.storage.user.get('tool_verse_number'),
                "q": app.storage.user.get('tool_query', ''),
                "area": 2,
                "tab1": bible_tab,
                "tab2": active_tab,
            }
            # store as history
            if update_url:
                with self.splitter: # attach to splitter to workaround `RuntimeError: The parent element this slot belongs to has been deleted.`
                    if client := ui.context.client:
                        new_url = f'/?tool={title if title.lower() in self.tools else "bible"}&tbt={args.get("bt")}&tb={args.get("b")}&tc={args.get("c")}&tv={args.get("v")}&tq={args.get("q")}'
                        client.run_javascript(f"window.history.pushState({{}}, '', '{new_url}')")
                        ref = BibleVerseParser(False, language=app.storage.user['ui_language']).bcvToVerseReference(args.get("b"), args.get("c"), args.get("v"))
                        client.run_javascript(f'document.title = "[{title.upper()}] {ref}"')
            if keep:
                app.storage.user[active_tab] = args
            # Get the active tab's scroll area
            active_panel = self.area2_tab_panels[active_tab]
            # Clear and load new content
            active_panel.clear()
            # load content
            with active_panel:
                content(gui=self, **args)
            # Update tab label to reflect new content
            for child in self.area2_tabs:
                if hasattr(child, '_props') and child._props.get('name') == active_tab:
                    child.props(f'label="{tab_label}"')
                    break
            # reset tool query
            app.storage.user["tool_query"] = ""
        except:
            print(traceback.format_exc())

    def update_active_area1_tab_records(self, title=None, label=None, bt=None, b=None, c=None, v=None, q=None):
        active_area1_tab = self.get_active_area1_tab()
        if active_area1_tab in app.storage.user: # only update when keep = True
            args = app.storage.user[active_area1_tab]
            if title is not None:
                args["title"] = title
            if label is not None:
                args["label"] = label
            if bt is not None:
                args["bt"] = bt
            if b is not None:
                args["b"] = b
            if c is not None:
                args["c"] = c
            if v is not None:
                args["v"] = v
            if q is not None:
                args["q"] = q
            app.storage.user[active_area1_tab] = args
        app.storage.user["bible_query"] = ""

    def update_active_area2_tab_records(self, title=None, label=None, bt=None, b=None, c=None, v=None, q=None):
        active_area2_tab = self.get_active_area2_tab()
        if active_area2_tab in app.storage.user: # only update when keep = True
            args = app.storage.user[active_area2_tab]
            if title is not None:
                args["title"] = title
            if label is not None:
                args["label"] = label
            if bt is not None:
                args["bt"] = bt
            if b is not None:
                args["b"] = b
            if c is not None:
                args["c"] = c
            if v is not None:
                args["v"] = v
            if q is not None:
                args["q"] = q
            app.storage.user[active_area2_tab] = args
        app.storage.user["tool_query"] = ""

    def get_area_1_bible_text(self):
        active_bible_tab = self.get_active_area1_tab()
        return app.storage.user[active_bible_tab]["bt"] if active_bible_tab in app.storage.user else app.storage.user['bible_book_text'] if 'bible_book_text' in app.storage.user else app.storage.user["primary_bible"]

    def get_area_2_bible_text(self):
        active_bible_tab = self.get_active_area2_tab()
        return app.storage.user[active_bible_tab]["bt"] if active_bible_tab in app.storage.user else app.storage.user['tool_book_text'] if 'tool_book_text' in app.storage.user else app.storage.user["primary_bible"]

    def show_all_verses(self, entry):
        #ui.notify('Loading all verses...')
        app.storage.user["tool_query"] = entry
        self.select_empty_area2_tab()
        self.load_area_2_content(title='Verses')

    def change_area_1_bible_chapter(self, version=None, book=1, chapter=1, verse=1):
        if version is None:
            version = self.get_area_1_bible_text()
        app.storage.user['bible_book_text'] = version
        app.storage.user['bible_book_number'] = book
        app.storage.user['bible_chapter_number'] = chapter
        app.storage.user['bible_verse_number'] = verse
        # in some cases, self.get_content do not work
        if version == "ORB":
            content = original_reader
        elif version == "OIB":
            content = original_interlinear
        elif version == "OPB":
            content = original_parallel
        elif version == "ODB":
            content = original_discourse
        elif version == "OLB":
            content = original_linguistic
        else:
            content = bible_translation
        self.load_area_1_content(content=content, title=version)
        if app.storage.user["sync"]:
            args = app.storage.user[self.get_active_area2_tab()]
            if not self.is_tool(args.get("title")) and (not args.get("b") == book or not args.get("c") == chapter):
                self.change_area_2_bible_chapter(args.get("bt"), book, chapter, verse)

    def change_area_2_bible_chapter(self, version=None, book=1, chapter=1, verse=1, sync=True):
        if version is None:
            version = self.get_area_2_bible_text()
        app.storage.user['tool_book_text'] = version
        if sync and app.storage.user.get("sync"):
            app.storage.user['bible_book_number'] = book
            app.storage.user['bible_chapter_number'] = chapter
            app.storage.user['bible_verse_number'] = verse
        else:
            app.storage.user['tool_book_number'] = book
            app.storage.user['tool_chapter_number'] = chapter
            app.storage.user['tool_verse_number'] = verse
        # in some cases, self.get_content do not work
        if version == "ORB":
            content = original_reader
        elif version == "OIB":
            content = original_interlinear
        elif version == "OPB":
            content = original_parallel
        elif version == "ODB":
            content = original_discourse
        elif version == "OLB":
            content = original_linguistic
        else:
            content = bible_translation
        self.load_area_2_content(content=content, title=version, sync=sync)
        if sync and app.storage.user["sync"]:
            args = app.storage.user[self.get_active_area1_tab()]
            if not args.get("b") == book or not args.get("c") == chapter:
                self.change_area_1_bible_chapter(args.get("bt"), book, chapter, verse)

    def add_tab_area1(self):
        """Dynamically add a new tab to Area 1"""
        self.area1_tab_counter += 1
        new_tab_name = f'tab1_{self.area1_tab_counter}'
        # Add new tab
        with self.area1_tabs:
            with ui.tab(new_tab_name, label=f'Bible {self.area1_tab_counter}').classes('text-secondary closable-tab') as tab:
                close_btn = ui.button(
                    icon='close',
                    on_click=partial(self.remove_tab_area1_any, new_tab_name),
                ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
                close_btn.on('click', js_handler='(e) => e.stopPropagation()')
        # Add new tab panel
        with self.area1_tab_panels_container:
            with ui.tab_panel(new_tab_name).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                self.area1_tab_panels[new_tab_name] = ui.scroll_area().classes(f'w-full h-full {new_tab_name}')
                with self.area1_tab_panels[new_tab_name]:
                    ui.label(f'Bible Area - Tab {self.area1_tab_counter}').classes('text-2xl font-bold mb-4')
                    ui.label('Please select a Bible from the menu.').classes('text-gray-600')
        self.area1_tabs.set_value(new_tab_name)

    def remove_tab_area1_any(self, id):
        """Remove any tabs from Area 1, even they are not active"""
        active_tab = self.area1_tab_panels_container.value
        if not active_tab == id:
            self.area1_tab_panels_container.value = id
        self.remove_tab_area1()
        if not active_tab == id and not self.area1_tab_panels_container.value == active_tab:
            self.area1_tab_panels_container.value = active_tab

    def remove_tab_area1(self):
        """Remove the currently active tab from Area 1"""
        active_tab = self.get_active_area1_tab()
        # Don't allow removing if it's the last tab
        if len(self.area1_tab_panels) <= 1:
            ui.notify('Cannot remove the last tab!', type='warning')
            return
        # Find and remove the tab
        tab_to_remove = None
        for child in self.area1_tabs:
            if hasattr(child, '_props') and child._props.get('name') == active_tab:
                tab_to_remove = child
                break
        if tab_to_remove:
            # Switch to a different tab before removing
            remaining_tabs = [k for k in self.area1_tab_panels.keys() if k != active_tab]
            if remaining_tabs:
                self.area1_tab_panels_container.set_value(remaining_tabs[0])
            # Remove the tab
            self.area1_tabs.remove(tab_to_remove)
            # Remove the tab panel
            if active_tab in self.area1_tab_panels:
                self.area1_tab_panels[active_tab].parent_slot.parent.delete()
                del self.area1_tab_panels[active_tab]
            if active_tab in app.storage.user:
                del app.storage.user[active_tab]
        #self.area1_tab_counter = len(self.area1_tab_panels) # do not update, otherwise new tab records may override the existing ones

    def add_tab_area2(self):
        """Dynamically add a new tab to Area 2"""
        self.area2_tab_counter += 1
        new_tab_name = f'tab2_{self.area2_tab_counter}'
        # Add new tab
        with self.area2_tabs:
            with ui.tab(new_tab_name, label=f'Tool {self.area2_tab_counter}').classes('text-secondary closable-tab') as tab:
                close_btn = ui.button(
                    icon='close',
                    on_click=partial(self.remove_tab_area2_any, new_tab_name),
                ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
                close_btn.on('click', js_handler='(e) => e.stopPropagation()')
        # Add new tab panel
        with self.area2_tab_panels_container:
            with ui.tab_panel(new_tab_name).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                self.area2_tab_panels[new_tab_name] = ui.scroll_area().classes(f'w-full h-full {new_tab_name}')
                with self.area2_tab_panels[new_tab_name]:
                    ui.label(f'Tool Area - Tab {self.area2_tab_counter}').classes('text-2xl font-bold mb-4')
                    ui.label('Please select a tool from the menu.').classes('text-gray-600')
        self.area2_tabs.set_value(new_tab_name)

    def remove_tab_area2_any(self, id):
        """Remove any tabs from Area 2, even they are not active"""
        active_tab = self.area2_tab_panels_container.value
        if not active_tab == id:
            self.area2_tab_panels_container.value = id
        self.remove_tab_area2()
        if not active_tab == id and not self.area2_tab_panels_container.value == active_tab:
            self.area2_tab_panels_container.value = active_tab

    def remove_tab_area2(self):
        """Remove the currently active tab from Area 2"""
        active_tab = self.get_active_area2_tab()
        # Don't allow removing if it's the last tab
        if len(self.area2_tab_panels) <= 1:
            ui.notify('Cannot remove the last tab!', type='warning')
            return
        # Find and remove the tab
        tab_to_remove = None
        for child in self.area2_tabs:
            if hasattr(child, '_props') and child._props.get('name') == active_tab:
                tab_to_remove = child
                break
        if tab_to_remove:
            # Switch to a different tab before removing
            remaining_tabs = [k for k in self.area2_tab_panels.keys() if k != active_tab]
            if remaining_tabs:
                self.area2_tab_panels_container.set_value(remaining_tabs[0])
            # Remove the tab
            self.area2_tabs.remove(tab_to_remove)
            # Remove the tab panel
            if active_tab in self.area2_tab_panels:
                self.area2_tab_panels[active_tab].parent_slot.parent.delete()
                del self.area2_tab_panels[active_tab]
            if active_tab in app.storage.user:
                del app.storage.user[active_tab]
        #self.area2_tab_counter = len(self.area2_tab_panels) # do not update, otherwise new tab records may override the existing ones

    # --- Shared Menu Function ---
    # This function creates the header, horizontal menu (desktop),
    # and drawer (mobile).

    def create_menu(self):
        """Create the responsive header and navigation drawer."""

        auto_suggestions = [BibleBooks.abbrev[app.storage.user['ui_language']][str(i)][0] for i in range(1,67)]
        auto_suggestions += [f"{i}:::" for i in self.tools.keys()]

        parser = BibleVerseParser(False)
        def perform_quick_search(quick_search):
            app.storage.user.update(left_drawer_open=False)
            if search_item := quick_search.value.strip():
                client_bibles = getBibleVersionList(app.storage.client["custom"])
                refs = parser.extractAllReferences(search_item)
                if search_item.lower().startswith("bible:::") and refs: # open a parallel bible chapter in area 2
                    search_item = search_item[8:]
                    b,c,v = refs[0]
                    if ":::" in search_item and search_item.split(":::", 1)[0].strip() in client_bibles: # bible version is specified
                        version, search_item = search_item.split(":::", 1)
                        version = version.strip()
                    else: # bible version is not specified
                        version = None
                    self.change_area_2_bible_chapter(version=version, book=b, chapter=c, verse=v)
                elif ":::" in search_item and search_item.split(":::", 1)[0].strip().lower() in self.tools: # open a tool in area 2
                    tool, app.storage.user["tool_query"] = search_item.split(":::", 1)
                    tool = tool.strip()
                    self.load_area_2_content(title=tool, sync=app.storage.user["sync"])
                elif len(refs) == 1: # open a bible chapter in area 1
                    b,c,v = refs[0]
                    if ":::" in search_item and search_item.split(":::", 1)[0].strip() in client_bibles: # bible version is specified
                        search_item = search_item[8:]
                        version, search_item = search_item.split(":::", 1)
                        version = version.strip()
                    else: # bible version is not specified
                        version = None
                    self.change_area_1_bible_chapter(version=version,book=b, chapter=c, verse=v)
                else: # search for verses in area 2; when no reference or more than a reference
                    app.storage.user["tool_query"] = search_item
                    self.load_area_2_content(title='Verses', sync=app.storage.user["sync"])

        # qr code dialog
        with ui.dialog() as dialog, ui.card().classes('items-center text-center p-6'):
            ui.label('URL & QR Code').classes('text-xl font-bold text-secondary')
            
            # Container to hold dynamic content (URL label + QR image)
            qr_container = ui.column().classes('items-center gap-4')

            ui.link("[BibleMate AI]", "https://github.com/eliranwong/biblemate").classes('text-secondary break-all max-w-[300px]')
            
            ui.button('Close', on_click=dialog.close).props('outline align=center text-color=secondary')

        # --- Event Handler ---
        async def show_url_popup():
            await self.replace_url()

            # 1. Get the current URL from the user's browser
            # We must await this because it requires a round-trip to the client
            current_url = await ui.run_javascript('window.location.href')
            
            # 2. Update the dialog content
            qr_container.clear() # Clear previous content
            with qr_container:
                # Show URL (clickable link)
                ui.link(current_url, current_url).classes('break-all max-w-[300px]')
                
                # Show QR Code
                # We generate it on the fly based on the fetched URL
                base64_img = self.generate_qr_base64(current_url)
                ui.image(base64_img).style('width: 250px; height: 250px')
                
            # 3. Open the dialog
            dialog.open()

        # --- Header ---
        with ui.header(elevated=True).classes('bg-primary text-white p-0'):
            # We use 'justify-between' to push the left and right groups apart
            with ui.row().classes('w-full items-center justify-between no-wrap'):
                
                # --- Left Aligned Group ---
                with ui.row().classes('items-center no-wrap'):
                    # --- Hamburger Button (Mobile Only) ---
                    # This button toggles the 'left_drawer_open' value in user storage
                    # .classes('lt-sm') means "visible only on screens LESS THAN Medium"
                    ui.button(
                        on_click=lambda: app.storage.user.update(left_drawer_open=not app.storage.user['left_drawer_open']),
                        icon='menu'
                    ).props('flat color=white').classes('lt-sm')

                    # --- Desktop Avatar + Title (Home) ---
                    # The button contains a row with the avatar and the label
                    with ui.button(on_click=lambda: ui.timer(0, show_url_popup, once=True)).props('flat text-color=white').classes('gt-xs'):
                        with ui.row().classes('items-center no-wrap'):
                            # Use a fallback icon in case the image fails to load
                            with ui.avatar(size='32px'):
                                with ui.image(app.storage.user["avatar"] if app.storage.user["avatar"] else os.path.expanduser(config.avatar) if config.avatar else os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')) as image:
                                    with image.add_slot('error'):
                                        ui.icon('account_circle').classes('m-auto') # Center fallback icon
                            
                            # This is just a label now; the parent button handles the click
                            ui.label('BibleMate AI').classes('text-lg ml-2') # Added margin-left for spacing

                quick_search1 = ui.input(placeholder=f'🔍 {get_translation("Quick search")} ...', autocomplete=auto_suggestions) \
                        .props('clearable outlined rounded dense autofocus enterkeyhint="search"') \
                        .classes('gt-xs flex-grow')
                quick_search1.on('keydown.enter.prevent', lambda: perform_quick_search(quick_search1))

                # --- Right Aligned Group (Features & About Us) ---
                with ui.row().classes('items-center no-wrap'):

                    primary_bible = app.storage.user["primary_bible"]
                    secondary_bible = app.storage.user["secondary_bible"]
                    
                    #with ui.row().classes('gt-xs items-center overflow-x-auto overflow-y-hidden no-wrap'):                            
                    # Bibles
                    with ui.button(icon='local_library').props('flat color=white round').tooltip(get_translation("Bibles")):
                        with ui.menu():
                            ui.menu_item(get_translation("Add Bible Tab"), on_click=self.add_tab_area1)
                            ui.menu_item(get_translation("Close Bible Tab"), on_click=self.remove_tab_area1)
                            ui.menu_item(get_translation("Close Others"), on_click=self.close_other_area1_tabs)
                            ui.separator()
                            ui.menu_item(primary_bible, on_click=lambda: self.load_area_1_content(title=primary_bible)).tooltip(primary_bible)
                            ui.menu_item(secondary_bible, on_click=lambda: self.load_area_1_content(title=secondary_bible)).tooltip(secondary_bible)
                            ui.separator()
                            ui.menu_item(get_translation("Original Reader’s Bible"), on_click=lambda: self.load_area_1_content(title='ORB')).tooltip('ORB')
                            ui.menu_item(get_translation("Original Interlinear Bible"), on_click=lambda: self.load_area_1_content(title='OIB')).tooltip('OIB')
                            ui.menu_item(get_translation("Original Parallel Bible"), on_click=lambda: self.load_area_1_content(title='OPB')).tooltip('OPB')
                            ui.menu_item(get_translation("Original Discourse Bible"), on_click=lambda: self.load_area_1_content(title='ODB')).tooltip('ODB')
                            ui.menu_item(get_translation("Original Linguistic Bible"), on_click=lambda: self.load_area_1_content(title='OLB')).tooltip('OLB')
                            ui.separator()
                            if app.storage.client["custom"] and config.bibles_custom:
                                for i in config.bibles_custom:
                                    if not i in (primary_bible, secondary_bible):
                                        ui.menu_item(i, on_click=partial(self.load_area_1_content, title=i)).tooltip(config.bibles_custom[i][0])
                                ui.separator()
                            for i in config.bibles:
                                if not i in (primary_bible, secondary_bible) and ((app.storage.client["custom"] and not i in config.bibles_custom) or not app.storage.client["custom"]):
                                    ui.menu_item(i, on_click=partial(self.load_area_1_content, title=i)).tooltip(config.bibles[i][0])

                    with ui.button(icon='devices_fold').props('flat color=white round').tooltip(get_translation("Parallel Bibles")):
                        with ui.menu():
                            ui.menu_item(get_translation("Add Parallel Tab"), on_click=self.add_tab_area2)
                            ui.menu_item(get_translation("Close Parallel Tab"), on_click=self.remove_tab_area2)
                            ui.menu_item(get_translation("Close Others"), on_click=self.close_other_area2_tabs)
                            ui.separator()
                            ui.menu_item(primary_bible, on_click=lambda: self.load_area_2_content(title=primary_bible)).tooltip(primary_bible)
                            ui.menu_item(secondary_bible, on_click=lambda: self.load_area_2_content(title=secondary_bible)).tooltip(secondary_bible)
                            ui.separator()
                            ui.menu_item(get_translation("Original Reader’s Bible"), on_click=lambda: self.load_area_2_content(title='ORB')).tooltip('ORB')
                            ui.menu_item(get_translation("Original Interlinear Bible"), on_click=lambda: self.load_area_2_content(title='OIB')).tooltip('OIB')
                            ui.menu_item(get_translation("Original Parallel Bible"), on_click=lambda: self.load_area_2_content(title='OPB')).tooltip('OPB')
                            ui.menu_item(get_translation("Original Discourse Bible"), on_click=lambda: self.load_area_2_content(title='ODB')).tooltip('ODB')
                            ui.menu_item(get_translation("Original Linguistic Bible"), on_click=lambda: self.load_area_2_content(title='OLB')).tooltip('OLB')
                            ui.separator()
                            if app.storage.client["custom"] and config.bibles_custom:
                                for i in config.bibles_custom:
                                    if not i in (primary_bible, secondary_bible):
                                        ui.menu_item(i, on_click=partial(self.load_area_2_content, title=i)).tooltip(config.bibles_custom[i][0])
                                ui.separator()
                            for i in config.bibles:
                                if not i in (primary_bible, secondary_bible) and ((app.storage.client["custom"] and not i in config.bibles_custom) or not app.storage.client["custom"]):
                                    ui.menu_item(i, on_click=partial(self.load_area_2_content, title=i)).tooltip(config.bibles[i][0])
                            

                    # Bible Tools
                    with ui.button(icon='build').props('flat color=white round').tooltip(get_translation("Tools")):
                        with ui.menu():
                            ui.menu_item(get_translation("Add Tool Tab"), on_click=self.add_tab_area2)
                            ui.menu_item(get_translation("Close Tool Tab"), on_click=self.remove_tab_area2)
                            ui.menu_item(get_translation("Close Others"), on_click=self.close_other_area2_tabs)
                            ui.separator()
                            ui.menu_item(get_translation("Bible Podcast"), on_click=lambda: self.load_area_2_content(title='Podcast', sync=True))
                            ui.menu_item(get_translation("Bible Audio"), on_click=lambda: self.load_area_2_content(title='Audio', sync=True))
                            ui.separator()
                            ui.menu_item(get_translation("Book Analysis"), on_click=lambda: self.load_area_2_content(title='Analysis', sync=True))
                            ui.menu_item(get_translation("Chapter Summary"), on_click=lambda: self.load_area_2_content(title='Summary', sync=True))
                            ui.separator()
                            ui.menu_item(get_translation("Bible Commentaries"), on_click=lambda: self.load_area_2_content(title='Commentary', sync=True))
                            ui.menu_item(get_translation("Cross-references"), on_click=lambda: self.load_area_2_content(title='Xrefs', sync=True))
                            ui.menu_item(get_translation("Treasury of Scripture Knowledge"), on_click=lambda: self.load_area_2_content(title='Treasury', sync=True))
                            #ui.menu_item(get_translation("Discourse Analysis"), on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            #ui.menu_item(get_translation("Morphological Data"), on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            #ui.menu_item(get_translation("Translation Spectrum"), on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.separator()
                            ui.menu_item(get_translation("Bible Promises"), on_click=lambda: self.load_area_2_content(title='Promises_'))
                            ui.menu_item(get_translation("Bible Parallels"), on_click=lambda: self.load_area_2_content(title='Parallels_'))
                            ui.separator()
                            ui.menu_item(get_translation("Bible Timelines"), on_click=lambda: self.load_area_2_content(title='Timelines', sync=True))
                            ui.menu_item(get_translation("Bible Chronology"), on_click=lambda: self.load_area_2_content(title='Chronology'))
                            ui.separator()
                            ui.menu_item(get_translation("Morphology"), on_click=lambda: self.load_area_2_content(title='Morphology', sync=True))
                            ui.separator()
                            ui.menu_item(get_translation("Chapter Indexes"), on_click=lambda: self.load_area_2_content(title='Chapterindexes', sync=True))
                            ui.menu_item(get_translation("Verse Indexes"), on_click=lambda: self.load_area_2_content(title='Indexes', sync=True))
                            ui.separator()
                            if config.google_client_id and config.google_client_secret:
                                ui.menu_item(get_translation("Bible Notes"), on_click=lambda: self.load_area_2_content(title='Notes', sync=True))
                            ui.menu_item(get_translation("Notepad"), on_click=lambda: self.load_area_2_content(title='Notepad', sync=True))
                    
                    with ui.button(icon='search').props('flat color=white round').tooltip(get_translation("Search")):
                        with ui.menu():
                            #ui.menu_item(get_translation("Add Search Tab"), on_click=self.add_tab_area2)
                            #ui.menu_item(get_translation("Remove Search Tab"), on_click=self.remove_tab_area2)
                            #ui.menu_item(get_translation("Close Others"), on_click=self.close_other_area2_tabs)
                            #ui.separator()
                            ui.menu_item(get_translation("Verses"), on_click=lambda: self.load_area_2_content(title='Verses'))
                            ui.menu_item(get_translation("Parallels"), on_click=lambda: self.load_area_2_content(title='Parallels'))
                            ui.menu_item(get_translation("Promises"), on_click=lambda: self.load_area_2_content(title='Promises'))
                            ui.menu_item(get_translation("Topics"), on_click=lambda: self.load_area_2_content(title='Topics'))
                            ui.menu_item(get_translation("Characters"), on_click=lambda: self.load_area_2_content(title='Characters'))
                            ui.menu_item(get_translation("Relationships"), on_click=lambda: self.load_area_2_content(title='Relationships'))
                            ui.menu_item(get_translation("Locations"), on_click=lambda: self.load_area_2_content(title='Locations'))
                            ui.menu_item(get_translation("Maps"), on_click=lambda: self.load_area_2_content(title='Maps'))
                            ui.menu_item(get_translation("Names"), on_click=lambda: self.load_area_2_content(title='Names'))
                            ui.menu_item(get_translation("Dictionaries"), on_click=lambda: self.load_area_2_content(title='Dictionaries'))
                            ui.menu_item(get_translation("Encyclopedias"), on_click=lambda: self.load_area_2_content(title='Encyclopedias'))
                            ui.menu_item(get_translation("Lexicons"), on_click=lambda: self.load_area_2_content(title='Lexicons'))

                    with ui.button(icon='auto_awesome').props('flat color=white round').tooltip(get_translation("AI")):
                        with ui.menu():
                            ui.menu_item(get_translation("Book Analysis"), on_click=lambda: self.load_area_2_content(title='Analysis'))
                            ui.menu_item(get_translation("Chapter Summary"), on_click=lambda: self.load_area_2_content(title='Summary'))
                            ui.menu_item(get_translation("Verse Commentary"), on_click=lambda: (
                                app.storage.user.update(favorite_commentary=self.get_aic()),
                                self.load_area_2_content(title='Commentary', sync=True)
                            ))
                            ui.separator()
                            #ui.menu_item('AI Q&A', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item(get_translation("AI Chat"), on_click=lambda: self.load_area_2_content(title='Chat'))
                            ui.menu_item(get_translation("Partner Mode"), on_click=lambda: self.load_area_2_content(title='Partner'))
                            ui.menu_item(get_translation("Agent Mode"), on_click=lambda: self.load_area_2_content(title='Agent'))

                    with ui.button(icon='settings').props('flat color=white round').tooltip(get_translation("Settings")):
                        with ui.menu():
                            with ui.row().classes('w-full justify-between'):                            
                                # Back Button
                                ui.button(icon='arrow_back', on_click=lambda: ui.run_javascript('history.back()')) \
                                    .props('dense flat round') \
                                    .tooltip('Go Back')
                                #ui.space()
                                # Forward Button
                                ui.button(icon='arrow_forward', on_click=lambda: ui.run_javascript('history.forward()')) \
                                    .props('dense flat round') \
                                    .tooltip('Go Forward')
                            # swap layout
                            ui.menu_item(get_translation("Bible Only"), on_click=lambda: self.swap_layout(1))
                            ui.menu_item(get_translation("Tool Only"), on_click=lambda: self.swap_layout(3))
                            ui.menu_item(get_translation("Bible & Tool"), on_click=lambda: self.swap_layout(2))
                            # swap
                            def toggleSwapButton():
                                app.storage.user["layout_swap_button"] = not app.storage.user["layout_swap_button"]
                            with ui.row().tooltip(get_translation("Toggle Display of Swap Layout Button")):
                                ui.menu_item(get_translation("Swap"), on_click=toggleSwapButton)
                                ui.space()
                                ui.switch().bind_value(app.storage.user, 'layout_swap_button')
                            # navigate
                            def toggleBibleSelectionButton():
                                app.storage.user["bible_select_button"] = not app.storage.user["bible_select_button"]
                            with ui.row().tooltip(get_translation("Toggle Display of Bible Selection Button")):
                                ui.menu_item(get_translation("Go"), on_click=toggleBibleSelectionButton)
                                ui.space()
                                ui.switch().bind_value(app.storage.user, 'bible_select_button')
                            # notes
                            def toggleNotes():
                                app.storage.user["notes"] = not app.storage.user["notes"]
                                ui.run_javascript('location.reload()')
                            with ui.row().tooltip(get_translation("Toggle Note Indicators")):
                                ui.menu_item(get_translation("Notes"), on_click=toggleNotes)
                                ui.space()
                                ui.switch(value=app.storage.user["notes"], on_change=toggleNotes)
                            # sync
                            def toggleSync():
                                app.storage.user["sync"] = not app.storage.user["sync"]
                            with ui.row().tooltip(get_translation("Toggle Bible Synchronization")):
                                ui.menu_item(get_translation("Sync"), on_click=toggleSync)
                                ui.space()
                                ui.switch().bind_value(app.storage.user, 'sync')
                            ui.separator()
                            # full screen
                            def toggleFullscreen(): # ui.fullscreen().toggle does not work in this case
                                app.storage.user["fullscreen"] = not app.storage.user["fullscreen"]
                            with ui.row().tooltip(get_translation("Toggle Fullscreen")):
                                ui.menu_item(get_translation("Screen"), on_click=toggleFullscreen)
                                ui.space()
                                ui.switch().bind_value(app.storage.user, 'fullscreen')
                            # dark mode
                            with ui.menu_item() as dark_mode_menu_item:
                                dark_mode_label = ui.label(get_translation("Light Mode") if app.storage.user["dark_mode"] else get_translation("Dark Mode")).classes('flex items-center')
                            def toggle_dark_mode_menu_item(text_label: ui.label):
                                app.storage.user['dark_mode'] = not app.storage.user['dark_mode']
                                #text_label.set_text("Light Mode" if app.storage.user["dark_mode"] else "Dark Mode")
                                ui.run_javascript('location.reload()')
                            dark_mode_menu_item.on('click', lambda: toggle_dark_mode_menu_item(dark_mode_label))
                            ui.separator()
                            ui.menu_item(get_translation("Preferences"), on_click=lambda: ui.navigate.to('/settings'))

        # --- Drawer (Mobile Menu) ---
        # This section is unchanged
        with ui.drawer('left') \
                .classes('lt-sm') \
                .props('overlay') \
                .bind_value(app.storage.user, 'left_drawer_open') as left_drawer:

            # The button contains a row with the avatar and the label
            with ui.button(on_click=lambda: (
                ui.timer(0, show_url_popup, once=True),
                app.storage.user.update(left_drawer_open=False)
            )).props('flat text-color=white'):
                with ui.row().classes('items-center no-wrap'):
                    # Use a fallback icon in case the image fails to load
                    with ui.avatar(size='32px'):
                        with ui.image(app.storage.user["avatar"] if app.storage.user["avatar"] else os.path.expanduser(config.avatar) if config.avatar else os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')) as image:
                            with image.add_slot('error'):
                                ui.icon('account_circle').classes('m-auto') # Center fallback icon
                    
                    # This is just a label now; the parent button handles the click
                    ui.label('BibleMate AI').classes('text-lg ml-2')

            quick_search2 = ui.input(placeholder=f'🔍 {get_translation("Quick search")} ...', autocomplete=auto_suggestions) \
                    .props('clearable outlined rounded dense autofocus enterkeyhint="search" hide-bottom-space') \
                    .classes('w-full !m-0 !p-0')
            quick_search2.on('keydown.enter.prevent', lambda: perform_quick_search(quick_search2))

            ui.switch(get_translation("Go")).bind_value(app.storage.user, 'bible_select_button')
            ui.switch(get_translation("Swap")).bind_value(app.storage.user, 'layout_swap_button')
            ui.switch(get_translation("Notes"), value=app.storage.user["notes"], on_change=toggleNotes)
            ui.switch(get_translation("Sync")).bind_value(app.storage.user, 'sync')
            ui.switch(get_translation("Fullscreen")).bind_value(app.storage.user, 'fullscreen')
            ui.switch(get_translation("Dark Mode")).bind_value(app.storage.user, 'dark_mode').on_value_change(lambda: ui.run_javascript('location.reload()'))

            # Bibles
            with ui.expansion(get_translation("Bibles"), icon='local_library').props('header-class="text-secondary"'):
                ui.item(get_translation("Original Reader’s Bible"), on_click=lambda: (
                    self.load_area_1_content(title='ORB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ORB')
                ui.item(get_translation("Original Interlinear Bible"), on_click=lambda: (
                    self.load_area_1_content(title='OIB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OIB')
                ui.item(get_translation("Original Parallel Bible"), on_click=lambda: (
                    self.load_area_1_content(title='OPB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OPB')
                ui.item(get_translation("Original Discourse Bible"), on_click=lambda: (
                    self.load_area_1_content(title='ODB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ODB')
                ui.item(get_translation("Original Linguistic Bible"), on_click=lambda: (
                    self.load_area_1_content(title='OLB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OLB')
                ui.separator()
                if app.storage.client["custom"] and config.bibles_custom:
                    for i in config.bibles_custom:
                        ui.item(i, on_click=lambda: (
                            self.load_area_1_content(title=i),
                            app.storage.user.update(left_drawer_open=False)
                        )).props('clickable').tooltip(config.bibles_custom[i][0])
                    ui.separator()
                for i in config.bibles:
                    if (app.storage.client["custom"] and not i in config.bibles_custom) or not app.storage.client["custom"]:
                        ui.item(i, on_click=lambda: (
                            self.load_area_1_content(title=i),
                            app.storage.user.update(left_drawer_open=False)
                        )).props('clickable').tooltip(config.bibles[i][0])

            # Parallel Bibles
            with ui.expansion(get_translation("Parallel Bibles"), icon='devices_fold').props('header-class="text-secondary"'):
                ui.item(get_translation("Original Reader’s Bible"), on_click=lambda: (
                    self.load_area_2_content(title='ORB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ORB')
                ui.item(get_translation("Original Interlinear Bible"), on_click=lambda: (
                    self.load_area_2_content(title='OIB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OIB')
                ui.item(get_translation("Original Parallel Bible"), on_click=lambda: (
                    self.load_area_2_content(title='OPB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OPB')
                ui.item(get_translation("Original Discourse Bible"), on_click=lambda: (
                    self.load_area_2_content(title='ODB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ODB')
                ui.item(get_translation("Original Linguistic Bible"), on_click=lambda: (
                    self.load_area_2_content(title='OLB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OLB')
                ui.separator()
                if app.storage.client["custom"] and config.bibles_custom:
                    for i in config.bibles_custom:
                        ui.item(i, on_click=lambda: (
                            self.load_area_2_content(title=i),
                            app.storage.user.update(left_drawer_open=False)
                        )).props('clickable').tooltip(config.bibles_custom[i][0])
                    ui.separator()
                for i in config.bibles:
                    if (app.storage.client["custom"] and not i in config.bibles_custom) or not app.storage.client["custom"]:
                        ui.item(i, on_click=lambda: (
                            self.load_area_2_content(title=i),
                            app.storage.user.update(left_drawer_open=False)
                        )).props('clickable').tooltip(config.bibles[i][0])

            # Bible Tools
            with ui.expansion(get_translation("Tools"), icon='build').props('header-class="text-secondary"'):
                ui.item(get_translation("Bible Podcast"), on_click=lambda: (
                    self.load_area_2_content(title='Podcast', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Bible Audio"), on_click=lambda: (
                    self.load_area_2_content(title='Audio', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item(get_translation("Book Analysis"), on_click=lambda: (
                    self.load_area_2_content(title='Analysis', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Chapter Summary"), on_click=lambda: (
                    self.load_area_2_content(title='Summary', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item(get_translation("Bible Commentaries"), on_click=lambda: (
                    self.load_area_2_content(title='Commentary', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Cross-references"), on_click=lambda: (
                    self.load_area_2_content(title='Xrefs', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Treasury of Scripture Knowledge"), on_click=lambda: (
                    self.load_area_2_content(title='Treasury', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                #ui.item(get_translation("Discourse Analysis"), on_click=lambda: (
                #    self.load_area_2_content(self.work_in_progress),
                #    app.storage.user.update(left_drawer_open=False)
                #)).props('clickable')
                #ui.item(get_translation("Morphological Data"), on_click=lambda: (
                #    self.load_area_2_content(self.work_in_progress),
                #    app.storage.user.update(left_drawer_open=False)
                #)).props('clickable')
                #ui.item(get_translation("Translation Spectrum"), on_click=lambda: (
                #    self.load_area_2_content(self.work_in_progress),
                #    app.storage.user.update(left_drawer_open=False)
                #)).props('clickable')
                ui.item(get_translation("Bible Promises"), on_click=lambda: (
                    self.load_area_2_content(title='Promises_'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Bible Parallels"), on_click=lambda: (
                    self.load_area_2_content(title='Parallels_'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item(get_translation("Bible Timelines"), on_click=lambda: (
                    self.load_area_2_content(title='Timelines', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Bible Chronology"), on_click=lambda: (
                    self.load_area_2_content(title='Chronology'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item(get_translation("Morphology"), on_click=lambda: (
                    self.load_area_2_content(title='Morphology', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item(get_translation("Chapter Indexes"), on_click=lambda: (
                    self.load_area_2_content(title='Chapterindexes', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Verse Indexes"), on_click=lambda: (
                    self.load_area_2_content(title='Indexes', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                if config.google_client_id and config.google_client_secret:
                    ui.item(get_translation("Bible Notes"), on_click=lambda: (
                        self.load_area_2_content(title='Notes', sync=True),
                        app.storage.user.update(left_drawer_open=False)
                    )).props('clickable')
                ui.item(get_translation("Notepad"), on_click=lambda: (
                    self.load_area_2_content(title='Notepad', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')

            # Search
            with ui.expansion(get_translation("Search"), icon='search').props('header-class="text-secondary"'):
                ui.item(get_translation("Verses"), on_click=lambda: (
                    self.load_area_2_content(title='Verses'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Parallels"), on_click=lambda: (
                    self.load_area_2_content(title='Parallels'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Promises"), on_click=lambda: (
                    self.load_area_2_content(title='Promises'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Topics"), on_click=lambda: (
                    self.load_area_2_content(title='Topics'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Characters"), on_click=lambda: (
                    self.load_area_2_content(title='Characters'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Relationships"), on_click=lambda: (
                    self.load_area_2_content(title='Relationships'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Locations"), on_click=lambda: (
                    self.load_area_2_content(title='Locations'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Maps"), on_click=lambda: (
                    self.load_area_2_content(title='Maps'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Names"), on_click=lambda: (
                    self.load_area_2_content(title='Names'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Dictionaries"), on_click=lambda: (
                    self.load_area_2_content(title='Dictionaries'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Encyclopedias"), on_click=lambda: (
                    self.load_area_2_content(title='Encyclopedias'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Lexicons"), on_click=lambda: (
                    self.load_area_2_content(title='Lexicons'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
            
            # AI
            with ui.expansion(get_translation("AI"), icon='auto_awesome').props('header-class="text-secondary"'):
                ui.item(get_translation("Book Analysis"), on_click=lambda: (
                    self.load_area_2_content(title='Analysis'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Chapter Summary"), on_click=lambda: (
                    self.load_area_2_content(title='Summary'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Verse Commentary"), on_click=lambda: (
                    app.storage.user.update(favorite_commentary=self.get_aic()),
                    self.load_area_2_content(title='Commentary', sync=True),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                #ui.item('AI Q&A', on_click=lambda: (
                #    self.load_area_2_content(self.work_in_progress),
                #    app.storage.user.update(left_drawer_open=False)
                #)).props('clickable')
                ui.item(get_translation("AI Chat"), on_click=lambda: (
                    self.load_area_2_content(title='Chat'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Partner Mode"), on_click=lambda: (
                    self.load_area_2_content(title='Partner'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Agent Mode"), on_click=lambda: (
                    self.load_area_2_content(title='Agent'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')

            # Preferences
            with ui.expansion(get_translation("Settings"), icon='settings').props('header-class="text-secondary"'):
                ui.item(get_translation("Bible Only"), on_click=lambda: (
                    self.swap_layout(1),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Tool Only"), on_click=lambda: (
                    self.swap_layout(2),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item(get_translation("Bible & Tool"), on_click=lambda: (
                    self.swap_layout(3),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item(get_translation("Preferences"), on_click=lambda: (
                    ui.navigate.to('/settings'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')

            with ui.row().classes('w-full justify-between'):                            
                # Back Button
                ui.button(color="secondary", icon='arrow_back', on_click=lambda: ui.run_javascript('history.back()')) \
                    .props('flat round') \
                    .tooltip('Go Back')
                # Forward Button
                ui.button(color="secondary", icon='arrow_forward', on_click=lambda: ui.run_javascript('history.forward()')) \
                    .props('flat round') \
                    .tooltip('Go Forward')
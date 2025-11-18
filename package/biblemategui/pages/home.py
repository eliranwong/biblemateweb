import os, traceback
from nicegui import app, ui
from functools import partial

from biblemategui import config, BIBLEMATEGUI_APP_DIR

from biblemategui.pages.ai.chat import ai_chat

from biblemategui.js.bible import BIBLE_JS
from biblemategui.js.original import get_original_js

# Import for page content
from biblemategui.pages.bibles.original_reader import original_reader
from biblemategui.pages.bibles.original_interlinear import original_interlinear
from biblemategui.pages.bibles.original_parallel import original_parallel
from biblemategui.pages.bibles.original_discourse import original_discourse
from biblemategui.pages.bibles.original_linguistic import original_linguistic
from biblemategui.pages.bibles.bible_translation import bible_translation

from biblemategui.pages.tools.audio import bibles_audio
from biblemategui.pages.tools.chronology import bible_chronology

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
        ui.add_head_html(BIBLE_JS) # for active verse scrolling
        ui.add_head_html(get_original_js(app.storage.user['dark_mode'])) # for interactive highlighting

        # Create self.splitter
        self.splitter = ui.splitter(value=100, horizontal=self.is_portrait).classes('w-full').style('height: 100vh')
        
        # Area 1
        with self.splitter.before:
            previous_tabs1 = sorted([i for i in app.storage.user.keys() if i.startswith("tab1_")])
            default_number_of_tabs1 = 3

            self.area1_wrapper = ui.column().classes('w-full h-full !gap-0')
            with self.area1_wrapper:
                self.area1_tabs = ui.tabs().classes('w-full')
                with self.area1_tabs:
                    if previous_tabs1:
                        for i in range(1, len(previous_tabs1)+1):
                            tab_id = f'tab1_{i}'
                            ui.tab(f'tab1_{i}', label=app.storage.user.get(previous_tabs1[i-1]).get("label", f'Bible {i}')).classes('text-secondary')
                            self.area1_tab_counter += 1
                        self.area1_tab_loaded = self.area1_tab_counter
                    if len(previous_tabs1) < default_number_of_tabs1:
                        for i in range(len(previous_tabs1)+1, default_number_of_tabs1+1):
                            tab_id = f'tab1_{i}'
                            ui.tab(tab_id, label=f'Bible {i}').classes('text-secondary')
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
                                    if content is None:
                                        app.storage.user.pop(saved_tab_id)
                                        continue
                                    args["tab1"] = tab_id
                                    content(gui=self, **args)
                                    if saved_tab_id != tab_id:
                                        app.storage.user[tab_id] = app.storage.user.pop(saved_tab_id)
                    if len(previous_tabs1) < default_number_of_tabs1:
                        for i in range(len(previous_tabs1)+1, default_number_of_tabs1+1):
                            tab_id = f'tab1_{i}'
                            with ui.tab_panel(tab_id).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                                self.area1_tab_panels[tab_id] = ui.scroll_area().classes(f'w-full h-full {tab_id}')
                                with self.area1_tab_panels[tab_id]:
                                    ui.label(f'Bible Area - Tab {i}').classes('text-2xl font-bold mb-4')
                                    #ui.label('[Content will be displayed here.]').classes('text-gray-600')
        
        # Area 2
        with self.splitter.after:
            previous_tabs2 = sorted([i for i in app.storage.user.keys() if i.startswith("tab2_")])
            default_number_of_tabs2 = 5

            self.area2_wrapper = ui.column().classes('w-full h-full !gap-0')
            with self.area2_wrapper:
                self.area2_tabs = ui.tabs().classes('w-full')
                with self.area2_tabs:
                    if previous_tabs2:
                        for i in range(1, len(previous_tabs2)+1):
                            tab_id = f'tab2_{i}'
                            ui.tab(f'tab2_{i}', label=app.storage.user.get(previous_tabs2[i-1]).get("label", f'Tool {i}')).classes('text-secondary')
                            self.area2_tab_counter += 1
                        self.area2_tab_loaded = self.area2_tab_counter
                    if len(previous_tabs2) < default_number_of_tabs2:
                        for i in range(len(previous_tabs2)+1, default_number_of_tabs2+1):
                            tab_id = f'tab2_{i}'
                            ui.tab(tab_id, label=f'Tool {i}').classes('text-secondary')
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
                                    if content is None:
                                        app.storage.user.pop(saved_tab_id)
                                        continue
                                    args["tab2"] = tab_id
                                    content(gui=self, **args)
                                    if saved_tab_id != tab_id:
                                        app.storage.user[tab_id] = app.storage.user.pop(saved_tab_id)
                    if len(previous_tabs2) < default_number_of_tabs2:
                        for i in range(len(previous_tabs2)+1, default_number_of_tabs2+1):
                            tab_id = f'tab2_{i}'
                            with ui.tab_panel(tab_id).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                                self.area2_tab_panels[tab_id] = ui.scroll_area().classes(f'w-full h-full {tab_id}')
                                with self.area2_tab_panels[tab_id]:
                                    ui.label(f'Tool Area - Tab {i}').classes('text-2xl font-bold mb-4')
                                    #ui.label('[Content will be displayed here.]').classes('text-gray-600')

        # Set initial visibility
        self.update_visibility()

    def swap_layout(self, layout=None):
        """Swap between three layout modes"""
        
        self.current_layout = layout if layout else (self.current_layout % 3) + 1
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

    def get_content(self, title):
        if title.lower() == "audio":
            return bibles_audio
        elif title.lower() == "chronology":
            return bible_chronology
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
        elif title in config.available_tools:
            return None # TODO
        else:
            return None

    def load_area_1_content(self, content=None, title="Bible", tab=None, args=None, keep=True):
        """Load example content in the active tab of Area 1"""
        if content is None:
            content = self.get_content(title)
            if content is None:
                print("No content found!")
                return None

        try:
            # modify tab label here for particular features TODO
            tab_label = title
            # Get the currently active tab
            active_tab = tab if tab else self.get_active_area1_tab()
            # args holder
            args = args if args else {
                "title": title,
                "label": tab_label,
                "bt": app.storage.user.get('bible_book_text'),
                "b": app.storage.user.get('bible_book_number'),
                "c": app.storage.user.get('bible_chapter_number'),
                "v": app.storage.user.get('bible_verse_number'),
                "area": 1,
                "tab1": active_tab,
                "tab2": self.get_active_area2_tab(),
            }
            # Get the active tab's scroll area
            active_panel = self.area1_tab_panels[active_tab]
            # Clear and load new content
            active_panel.clear()
            with active_panel:
                # load content here
                content(gui=self, **args)
            # Update tab label to reflect new content
            for child in self.area1_tabs:
                if hasattr(child, '_props') and child._props.get('name') == active_tab:
                    # current label
                    # print(child._props.get('label'))
                    child.props(f'label="{tab_label}"')
                    break
            # store as history
            if keep:
                app.storage.user[active_tab] = args
        except:
            print(traceback.format_exc())


    def load_area_2_content(self, content=None, title="Tool", tab=None, args=None, keep=True):
        """Load example content in the active tab of Area 2"""
        if content is None:
            content = self.get_content(title)
            if content is None:
                print("No content found!")
                return None

        try:
            # modify tab label here for particular features TODO
            tab_label = title
            # Get the currently active tab
            active_tab = tab if tab else self.get_active_area2_tab()
            # args holder
            args = args if args else {
                "title": title,
                "label": tab_label,
                "bt": app.storage.user.get('tool_book_text'),
                "b": app.storage.user.get('bible_book_number') if app.storage.user.get("sync") else app.storage.user.get('tool_book_number'),
                "c": app.storage.user.get('bible_chapter_number') if app.storage.user.get("sync") else app.storage.user.get('tool_chapter_number'),
                "v": app.storage.user.get('bible_verse_number') if app.storage.user.get("sync") else app.storage.user.get('tool_verse_number'),
                "area": 2,
                "tab1": self.get_active_area1_tab(),
                "tab2": active_tab,
            }
            # Get the active tab's scroll area
            active_panel = self.area2_tab_panels[active_tab]
            # Clear and load new content
            active_panel.clear()
            with active_panel:
                content(gui=self, **args)
            # Update tab label to reflect new content
            for child in self.area2_tabs:
                if hasattr(child, '_props') and child._props.get('name') == active_tab:
                    # current label
                    # print(child._props.get('label'))
                    child.props(f'label="{tab_label}"')
                    break
            # store as history
            if keep:
                app.storage.user[active_tab] = args
        except:
            print(traceback.format_exc())

    def change_area_1_bible_chapter(self, version, book=1, chapter=1):
        app.storage.user['bible_book_number']= book
        app.storage.user['bible_chapter_number']= chapter
        app.storage.user['bible_verse_number']= 1
        self.load_area_1_content(title=version)

    def change_area_2_bible_chapter(self, version, book=1, chapter=1):
        app.storage.user['bible_book_number']= book
        app.storage.user['bible_chapter_number']= chapter
        app.storage.user['bible_verse_number']= 1
        self.load_area_2_content(title=version)

    def add_tab_area1(self):
        """Dynamically add a new tab to Area 1"""
        self.area1_tab_counter += 1
        new_tab_name = f'tab1_{self.area1_tab_counter}'
        # Add new tab
        with self.area1_tabs:
            ui.tab(new_tab_name, label=f'Bible {self.area1_tab_counter}').classes('text-secondary')
        # Add new tab panel
        with self.area1_tab_panels_container:
            with ui.tab_panel(new_tab_name).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                self.area1_tab_panels[new_tab_name] = ui.scroll_area().classes(f'w-full h-full {new_tab_name}')
                with self.area1_tab_panels[new_tab_name]:
                    ui.label(f'Bible Area - Tab {self.area1_tab_counter}').classes('text-2xl font-bold mb-4')
                    ui.label('[Content will be displayed here.]').classes('text-gray-600')
        self.area1_tabs.set_value(new_tab_name)

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


    def add_tab_area2(self):
        """Dynamically add a new tab to Area 2"""
        self.area2_tab_counter += 1
        new_tab_name = f'tab2_{self.area2_tab_counter}'
        # Add new tab
        with self.area2_tabs:
            ui.tab(new_tab_name, label=f'Tool {self.area2_tab_counter}').classes('text-secondary')
        # Add new tab panel
        with self.area2_tab_panels_container:
            with ui.tab_panel(new_tab_name).classes('w-full h-full !p-0 !b-0 !m-0 !gap-0'):
                self.area2_tab_panels[new_tab_name] = ui.scroll_area().classes(f'w-full h-full {new_tab_name}')
                with self.area2_tab_panels[new_tab_name]:
                    ui.label(f'Tool Area - Tab {self.area2_tab_counter}').classes('text-2xl font-bold mb-4')
                    ui.label('[Content will be displayed here.]').classes('text-gray-600')
        self.area2_tabs.set_value(new_tab_name)

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

    # --- Shared Menu Function ---
    # This function creates the header, horizontal menu (desktop),
    # and drawer (mobile).

    def create_menu(self):
        """Create the responsive header and navigation drawer."""
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

                    # --- Mobile Avatar Button (Home) ---
                    # This is a button that contains the avatar
                    with ui.button(on_click=lambda: ui.navigate.to('/')).props('flat round dense').classes('lt-sm'):
                        with ui.avatar(size='32px'):
                            with ui.image(config.avatar if config.avatar else os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')) as image:
                                with image.add_slot('error'):
                                    ui.icon('account_circle').classes('m-auto') # Center fallback icon

                    # --- Desktop Avatar + Title (Home) ---
                    # The button contains a row with the avatar and the label
                    with ui.button(on_click=lambda: ui.navigate.to('/')).props('flat text-color=white').classes('gt-xs'):
                        with ui.row().classes('items-center no-wrap'):
                            # Use a fallback icon in case the image fails to load
                            with ui.avatar(size='32px'):
                                with ui.image(config.avatar if config.avatar else os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')) as image:
                                    with image.add_slot('error'):
                                        ui.icon('account_circle').classes('m-auto') # Center fallback icon
                            
                            # This is just a label now; the parent button handles the click
                            ui.label('BibleMate AI').classes('text-lg ml-2') # Added margin-left for spacing

                # --- Right Aligned Group (Features & About Us) ---
                with ui.row().classes('items-center no-wrap'):
                    
                    #with ui.row().classes('gt-xs items-center overflow-x-auto overflow-y-hidden no-wrap'):                            
                    # Bibles
                    with ui.button(icon='local_library').props('flat color=white round').tooltip('Bibles'):
                        with ui.menu():
                            ui.menu_item('Add Bible Tab', on_click=self.add_tab_area1)
                            ui.menu_item('Remove Bible Tab', on_click=self.remove_tab_area1)
                            ui.separator()
                            ui.menu_item('Original Reader’s Bible', on_click=lambda: self.load_area_1_content(title='ORB')).tooltip('ORB')
                            ui.menu_item('Original Interlinear Bible', on_click=lambda: self.load_area_1_content(title='OIB')).tooltip('OIB')
                            ui.menu_item('Original Parallel Bible', on_click=lambda: self.load_area_1_content(title='OPB')).tooltip('OPB')
                            ui.menu_item('Original Discourse Bible', on_click=lambda: self.load_area_1_content(title='ODB')).tooltip('ODB')
                            ui.menu_item('Original Linguistic Bible', on_click=lambda: self.load_area_1_content(title='OLB')).tooltip('OLB')
                            ui.separator()
                            if app.storage.client["custom"] and config.bibles_custom:
                                for i in config.bibles_custom:
                                    ui.menu_item(i, on_click=partial(self.load_area_1_content, title=i)).tooltip(config.bibles_custom[i][0])
                                ui.separator()
                            for i in config.bibles:
                                if (app.storage.client["custom"] and not i in config.bibles_custom) or not app.storage.client["custom"]:
                                    ui.menu_item(i, on_click=partial(self.load_area_1_content, title=i)).tooltip(config.bibles[i][0])

                    with ui.button(icon='devices_fold').props('flat color=white round').tooltip('Parallel Bibles'):
                        with ui.menu():
                            ui.menu_item('Add Parallel Tab', on_click=self.add_tab_area2)
                            ui.menu_item('Remove Parallel Tab', on_click=self.remove_tab_area2)
                            ui.separator()
                            ui.menu_item('Original Reader’s Bible', on_click=lambda: self.load_area_2_content(title='ORB')).tooltip('ORB')
                            ui.menu_item('Original Interlinear Bible', on_click=lambda: self.load_area_2_content(title='OIB')).tooltip('OIB')
                            ui.menu_item('Original Parallel Bible', on_click=lambda: self.load_area_2_content(title='OPB')).tooltip('OPB')
                            ui.menu_item('Original Discourse Bible', on_click=lambda: self.load_area_2_content(title='ODB')).tooltip('ODB')
                            ui.menu_item('Original Linguistic Bible', on_click=lambda: self.load_area_2_content(title='OLB')).tooltip('OLB')
                            ui.separator()
                            if app.storage.client["custom"] and config.bibles_custom:
                                for i in config.bibles_custom:
                                    ui.menu_item(i, on_click=partial(self.load_area_2_content, title=i)).tooltip(config.bibles_custom[i][0])
                                ui.separator()
                            for i in config.bibles:
                                if (app.storage.client["custom"] and not i in config.bibles_custom) or not app.storage.client["custom"]:
                                    ui.menu_item(i, on_click=partial(self.load_area_2_content, title=i)).tooltip(config.bibles[i][0])
                            

                    # Bible Tools
                    with ui.button(icon='build').props('flat color=white round').tooltip('Tools'):
                        with ui.menu():
                            ui.menu_item('Add Tool Tab', on_click=self.add_tab_area2)
                            ui.menu_item('Remove Tool Tab', on_click=self.remove_tab_area2)
                            ui.separator()
                            ui.menu_item('Bible Verse', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Bible Audio', on_click=lambda: self.load_area_2_content(title='Audio'))
                            ui.menu_item('Compare Chapter', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Compare Verse', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.separator()
                            ui.menu_item('Bible Commentaries', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Cross-references', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Treasury of Scripture Knowledge', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Discourse Analysis', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Morphological Data', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Translation Spectrum', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Bible Timelines', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Bible Chronology', on_click=lambda: self.load_area_2_content(title='Chronology'))
                    
                    """with ui.button(icon='book').props('flat color=white round'):
                        with ui.menu():
                            ..."""
                    
                    with ui.button(icon='search').props('flat color=white round').tooltip('Search'):
                        with ui.menu():
                            ui.menu_item('Bibles', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Parallels', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Promises', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Topics', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Names', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Characters', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Locations', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Dictionary', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Encyclopedia', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Lexicon', on_click=lambda: self.load_area_2_content(self.work_in_progress))

                    with ui.button(icon='auto_awesome').props('flat color=white round').tooltip('AI'):
                        with ui.menu():
                            ui.menu_item('AI Commentary', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('AI Q&A', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('AI Chat', on_click=lambda: self.load_area_2_content(ai_chat, 'Chat'))
                            ui.menu_item('Partner Mode', on_click=lambda: self.load_area_2_content(self.work_in_progress))
                            ui.menu_item('Agent Mode', on_click=lambda: self.load_area_2_content(self.work_in_progress))

                    with ui.button(icon='settings').props('flat color=white round').tooltip('Settings'):
                        with ui.menu():
                            ui.menu_item('Bible Only', on_click=lambda: self.swap_layout(1))
                            ui.menu_item('Tool Only', on_click=lambda: self.swap_layout(3))
                            ui.menu_item('Bible & Tool', on_click=lambda: self.swap_layout(2))
                            ui.separator()
                            with ui.menu_item() as dark_mode_menu_item:
                                dark_mode_label = ui.label("Light Mode" if app.storage.user["dark_mode"] else "Dark Mode").classes('flex items-center')
                            def toggle_dark_mode_menu_item(text_label: ui.label):
                                app.storage.user['dark_mode'] = not app.storage.user['dark_mode']
                                #text_label.set_text("Light Mode" if app.storage.user["dark_mode"] else "Dark Mode")
                                ui.run_javascript('location.reload()')
                            dark_mode_menu_item.on('click', lambda: toggle_dark_mode_menu_item(dark_mode_label))
                            def toggleFullscreen(): # ui.fullscreen().toggle does not work in this case
                                app.storage.user["fullscreen"] = not app.storage.user["fullscreen"]
                            with ui.row():
                                ui.menu_item('Fullscreen', on_click=toggleFullscreen)
                                ui.switch().bind_value(app.storage.user, 'fullscreen')
                            ui.separator()
                            ui.menu_item('Preferences', on_click=lambda: ui.navigate.to('/settings'))

        # --- Drawer (Mobile Menu) ---
        # This section is unchanged
        with ui.drawer('left') \
                .classes('lt-sm') \
                .props('overlay') \
                .bind_value(app.storage.user, 'left_drawer_open') as left_drawer:
            
            ui.label('Navigation').classes('text-xl')

            # Home Link
            ui.item('Home', on_click=lambda: (
                ui.navigate.to('/'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.switch('Dark Mode').bind_value(app.storage.user, 'dark_mode').on_value_change(lambda: ui.run_javascript('location.reload()'))
            ui.switch('Fullscreen').bind_value(app.storage.user, 'fullscreen')

            # Bibles
            with ui.expansion('Bibles', icon='local_library').props('header-class="text-secondary"'):
                ui.item('Original Reader’s Bible', on_click=lambda: (
                    self.load_area_1_content(title='ORB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ORB')
                ui.item('Original Interlinear Bible', on_click=lambda: (
                    self.load_area_1_content(title='OIB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OIB')
                ui.item('Original Parallel Bible', on_click=lambda: (
                    self.load_area_1_content(title='OPB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OPB')
                ui.item('Original Discourse Bible', on_click=lambda: (
                    self.load_area_1_content(title='ODB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ODB')
                ui.item('Original Linguistic Bible', on_click=lambda: (
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
            with ui.expansion('Parallel Bibles', icon='devices_fold').props('header-class="text-secondary"'):
                ui.item('Original Reader’s Bible', on_click=lambda: (
                    self.load_area_2_content(title='ORB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ORB')
                ui.item('Original Interlinear Bible', on_click=lambda: (
                    self.load_area_2_content(title='OIB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OIB')
                ui.item('Original Parallel Bible', on_click=lambda: (
                    self.load_area_2_content(title='OPB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('OPB')
                ui.item('Original Discourse Bible', on_click=lambda: (
                    self.load_area_2_content(title='ODB'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable').tooltip('ODB')
                ui.item('Original Linguistic Bible', on_click=lambda: (
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
            with ui.expansion('Tools', icon='build').props('header-class="text-secondary"'):
                ui.item('Bible Verse', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Bible Audio', on_click=lambda: (
                    self.load_area_2_content(title='Audio'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Compare Chapter', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Compare Verse', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')

                ui.item('Bible Commentaries', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Cross-references', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Treasury of Scripture Knowledge', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Discourse Analysis', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Morphological Data', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Translation Spectrum', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Bible Timelines', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Bible Chronology', on_click=lambda: (
                    self.load_area_2_content(title='Chronology'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')

            # Search
            with ui.expansion('Search', icon='search').props('header-class="text-secondary"'):
                ui.item('Bibles', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Parallels', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Promises', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Topics', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Names', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Characters', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Locations', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Dictionary', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Encyclopedia', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Lexicon', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
            
            # AI
            with ui.expansion('AI', icon='auto_awesome').props('header-class="text-secondary"'):
                ui.item('AI Commentary', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('AI Q&A', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('AI Chat', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Partner Mode', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Agent Mode', on_click=lambda: (
                    self.load_area_2_content(self.work_in_progress),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')

            # Preferences
            with ui.expansion('Settings', icon='auto_awesome').props('header-class="text-secondary"'):
                ui.item('Bible Only', on_click=lambda: (
                    self.swap_layout(1),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Tool Only', on_click=lambda: (
                    self.swap_layout(2),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.item('Bible & Tool', on_click=lambda: (
                    self.swap_layout(3),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
                ui.item('Preferences', on_click=lambda: (
                    ui.navigate.to('/settings'),
                    app.storage.user.update(left_drawer_open=False)
                )).props('clickable')
                ui.separator()
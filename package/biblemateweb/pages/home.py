import os

from nicegui import app, ui

from biblemateweb import BIBLEMATEWEB_APP_DIR

from biblemateweb.pages.bibles.original_reader import original_reader
from biblemateweb.pages.bibles.original_interlinear import original_interlinear
from biblemateweb.pages.bibles.original_parallel import original_parallel
from biblemateweb.pages.bibles.original_discourse import original_discourse
from biblemateweb.pages.bibles.original_linguistic import original_linguistic

from biblemateweb.pages.tools.audio import bibles_audio
from biblemateweb.pages.tools.chronology import bible_chronology

from biblemateweb.pages.ai.chat import ai_chat

from biblemateweb.js.bible import BIBLE_JS
from biblemateweb.js.original import ORIGINAL_JS


# Global variable to track current layout
current_layout = 2  # 1, 2, or 3
area1_container = None
area2_container = None
area1_wrapper = None
area2_wrapper = None
splitter = None
is_lt_sm = False

# Tab panels and active tab tracking
area1_tabs = None
area2_tabs = None
area1_tab_panels = {}  # Dictionary to store tab panels by name
area2_tab_panels = {}
area1_tab_panels_container = None
area2_tab_panels_container = None
area1_tab_counter = 3  # Counter for new tabs in Area 1
area2_tab_counter = 5  # Counter for new tabs in Area 2

def check_breakpoint(ev):
    global is_lt_sm, splitter
    # prefer the well-known attributes
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
    is_lt_sm = width < 640   # tailwind sm = 640px
    if splitter:
        if is_lt_sm:
            splitter.props('horizontal')
        else:
            splitter.props(remove='horizontal')

def create_home_layout():
    """Create two scrollable areas with responsive layout"""
    global area1_wrapper, area2_wrapper, splitter, is_lt_sm
    global area1_tabs, area2_tabs, area1_tab_panels, area2_tab_panels
    global area1_tab_panels_container, area2_tab_panels_container

    # listen to the resize event
    ui.on('resize', check_breakpoint)
    
    # Inject JS
    ui.add_head_html(BIBLE_JS) # for active verse scrolling
    ui.add_head_html(ORIGINAL_JS) # for interactive highlighting

    # Create splitter
    splitter = ui.splitter(value=100, horizontal=is_lt_sm).classes('w-full').style('height: calc(100vh - 64px)')
    
    # Area 1 with 4 tabs
    with splitter.before:
        area1_wrapper = ui.column().classes('w-full h-full')
        with area1_wrapper:
            area1_tabs = ui.tabs().classes('w-full')
            with area1_tabs:
                ui.tab('tab1_1', label='Bible 1')
                ui.tab('tab1_2', label='Bible 2')
                ui.tab('tab1_3', label='Bible 3')
            
            area1_tab_panels_container = ui.tab_panels(area1_tabs, value='tab1_1').classes('w-full h-full')
            
            with area1_tab_panels_container:
                with ui.tab_panel('tab1_1'):
                    area1_tab_panels['tab1_1'] = ui.scroll_area().classes('w-full h-full p-4 tab1_1')
                    with area1_tab_panels['tab1_1']:
                        ui.label('Bible Area').classes('text-2xl font-bold mb-4')
                        ui.label('Bible content is placed here.').classes('text-gray-600')
                
                with ui.tab_panel('tab1_2'):
                    area1_tab_panels['tab1_2'] = ui.scroll_area().classes('w-full h-full p-4 tab1_2')
                    with area1_tab_panels['tab1_2']:
                        ...
                
                with ui.tab_panel('tab1_3'):
                    area1_tab_panels['tab1_3'] = ui.scroll_area().classes('w-full h-full p-4 tab1_3')
                    with area1_tab_panels['tab1_3']:
                        ...
    
    # Area 2 with 5 tabs
    with splitter.after:
        area2_wrapper = ui.column().classes('w-full h-full')
        with area2_wrapper:
            area2_tabs = ui.tabs().classes('w-full')
            with area2_tabs:
                ui.tab('tab2_1', label='Tool 1')
                ui.tab('tab2_2', label='Tool 2')
                ui.tab('tab2_3', label='Tool 3')
                ui.tab('tab2_4', label='Tool 4')
                ui.tab('tab2_5', label='Tool 5')
            
            area2_tab_panels_container = ui.tab_panels(area2_tabs, value='tab2_1').classes('w-full h-full')
            
            with area2_tab_panels_container:
                with ui.tab_panel('tab2_1'):
                    area2_tab_panels['tab2_1'] = ui.scroll_area().classes('w-full h-full p-4 tab2_1')
                    with area2_tab_panels['tab2_1']:
                        ui.label('Tool Area').classes('text-2xl font-bold mb-4')
                        ui.label('Tool content is placed here.').classes('text-gray-600')
                
                with ui.tab_panel('tab2_2'):
                    area2_tab_panels['tab2_2'] = ui.scroll_area().classes('w-full h-full p-4 tab2_2')
                    with area2_tab_panels['tab2_2']:
                        ...
                
                with ui.tab_panel('tab2_3'):
                    area2_tab_panels['tab2_3'] = ui.scroll_area().classes('w-full h-full p-4 tab2_3')
                    with area2_tab_panels['tab2_3']:
                        ...
                
                with ui.tab_panel('tab2_4'):
                    area2_tab_panels['tab2_4'] = ui.scroll_area().classes('w-full h-full p-4 tab2_4')
                    with area2_tab_panels['tab2_4']:
                        ...
                
                with ui.tab_panel('tab2_5'):
                    area2_tab_panels['tab2_5'] = ui.scroll_area().classes('w-full h-full p-4 tab2_5')
                    with area2_tab_panels['tab2_5']:
                        ...
    
    # Set initial visibility (Area 1 visible, Area 2 hidden)
    update_visibility()

def swap_layout():
    """Swap between three layout modes"""
    global current_layout
    
    current_layout = (current_layout % 3) + 1
    update_visibility()
    #ui.notify(f'Switched to Layout {current_layout}')

def update_visibility():
    """Update visibility of areas based on current layout"""
    global current_layout, area1_wrapper, area2_wrapper, splitter
    
    if current_layout == 1:
        # Area 1 visible, Area 2 invisible - maximize Area 1
        area1_wrapper.set_visibility(True)
        area2_wrapper.set_visibility(False)
        splitter.set_value(100)  # Move splitter to maximize Area 1
    elif current_layout == 2:
        # Both areas visible - 50/50 split
        area1_wrapper.set_visibility(True)
        area2_wrapper.set_visibility(True)
        splitter.set_value(50)  # Move splitter to middle
    elif current_layout == 3:
        # Area 1 invisible, Area 2 visible - maximize Area 2
        area1_wrapper.set_visibility(False)
        area2_wrapper.set_visibility(True)
        splitter.set_value(0)  # Move splitter to maximize Area 2

def get_active_area1_tab():
    """Get the currently active tab in Area 1"""
    global area1_tab_panels_container
    return area1_tab_panels_container.value

def get_active_area2_tab():
    """Get the currently active tab in Area 2"""
    global area2_tab_panels_container
    return area2_tab_panels_container.value

def load_area_1_content(content, title="Bible"):
    """Load example content in the active tab of Area 1"""
    global area1_tab_panels, area1_tabs
    
    # Get the currently active tab
    active_tab = get_active_area1_tab()
    # Get the active tab's scroll area
    active_panel = area1_tab_panels[active_tab]
    # Clear and load new content
    active_panel.clear()
    with active_panel:
        # load content here
        args = {
            "b": 63,
            "c": 1,
            "v": 3,
            "area": 1,
            "tab1": active_tab,
            "tab2": get_active_area2_tab(),
        }
        content(**args)
    # Update tab label to reflect new content
    for child in area1_tabs:
        if hasattr(child, '_props') and child._props.get('name') == active_tab:
            # current label
            # print(child._props.get('label'))
            child.props(f'label="{title}"')
            break
    #ui.notify(f'Loaded content in Area 1 - {active_tab}')

def load_area_2_content(content, title="Tool"):
    """Load example content in the active tab of Area 2"""
    global area2_tab_panels, area2_tabs
    
    # Get the currently active tab
    active_tab = get_active_area2_tab()
    # Get the active tab's scroll area
    active_panel = area2_tab_panels[active_tab]
    # Clear and load new content
    active_panel.clear()
    with active_panel:
        args = {
            "b": 63,
            "c": 1,
            "v": 3,
            "area": 2,
            "tab1": get_active_area1_tab(),
            "tab2": active_tab,
        }
        content(**args)
    # Update tab label to reflect new content
    for child in area2_tabs:
        if hasattr(child, '_props') and child._props.get('name') == active_tab:
            # current label
            # print(child._props.get('label'))
            child.props(f'label="{title}"')
            break
    #ui.notify(f'Loaded content in Area 2 - {active_tab}')

def add_tab_area1():
    """Dynamically add a new tab to Area 1"""
    global area1_tab_counter, area1_tabs, area1_tab_panels, area1_tab_panels_container
    
    area1_tab_counter += 1
    new_tab_name = f'tab1_{area1_tab_counter}'
    # Add new tab
    with area1_tabs:
        ui.tab(new_tab_name, label=f'Bible {area1_tab_counter}')
    # Add new tab panel
    with area1_tab_panels_container:
        with ui.tab_panel(new_tab_name):
            area1_tab_panels[new_tab_name] = ui.scroll_area().classes(f'w-full h-full p-4 {new_tab_name}')
            with area1_tab_panels[new_tab_name]:
                ...
    #ui.notify(f'Added Tab {area1_tab_counter} to Area 1')

def remove_tab_area1():
    """Remove the currently active tab from Area 1"""
    global area1_tab_panels, area1_tabs, area1_tab_panels_container
    
    active_tab = get_active_area1_tab()
    # Don't allow removing if it's the last tab
    if len(area1_tab_panels) <= 1:
        ui.notify('Cannot remove the last tab!', type='warning')
        return
    # Find and remove the tab
    tab_to_remove = None
    for child in area1_tabs:
        if hasattr(child, '_props') and child._props.get('name') == active_tab:
            tab_to_remove = child
            break
    if tab_to_remove:
        # Switch to a different tab before removing
        remaining_tabs = [k for k in area1_tab_panels.keys() if k != active_tab]
        if remaining_tabs:
            area1_tab_panels_container.set_value(remaining_tabs[0])
        # Remove the tab
        area1_tabs.remove(tab_to_remove)
        # Remove the tab panel
        if active_tab in area1_tab_panels:
            area1_tab_panels[active_tab].parent_slot.parent.delete()
            del area1_tab_panels[active_tab]
        #ui.notify(f'Removed {active_tab} from Area 1')

def add_tab_area2():
    """Dynamically add a new tab to Area 2"""
    global area2_tab_counter, area2_tabs, area2_tab_panels, area2_tab_panels_container
    
    area2_tab_counter += 1
    new_tab_name = f'tab2_{area2_tab_counter}'
    # Add new tab
    with area2_tabs:
        ui.tab(new_tab_name, label=f'Tool {area2_tab_counter}')
    # Add new tab panel
    with area2_tab_panels_container:
        with ui.tab_panel(new_tab_name):
            area2_tab_panels[new_tab_name] = ui.scroll_area().classes(f'w-full h-full p-4 {new_tab_name}')
            with area2_tab_panels[new_tab_name]:
                ...
    #ui.notify(f'Added Tab {area2_tab_counter} to Area 2')

def remove_tab_area2():
    """Remove the currently active tab from Area 2"""
    global area2_tab_panels, area2_tabs, area2_tab_panels_container
    
    active_tab = get_active_area2_tab()
    # Don't allow removing if it's the last tab
    if len(area2_tab_panels) <= 1:
        ui.notify('Cannot remove the last tab!', type='warning')
        return
    # Find and remove the tab
    tab_to_remove = None
    for child in area2_tabs:
        if hasattr(child, '_props') and child._props.get('name') == active_tab:
            tab_to_remove = child
            break
    if tab_to_remove:
        # Switch to a different tab before removing
        remaining_tabs = [k for k in area2_tab_panels.keys() if k != active_tab]
        if remaining_tabs:
            area2_tab_panels_container.set_value(remaining_tabs[0])
        # Remove the tab
        area2_tabs.remove(tab_to_remove)
        # Remove the tab panel
        if active_tab in area2_tab_panels:
            area2_tab_panels[active_tab].parent_slot.parent.delete()
            del area2_tab_panels[active_tab]
        #ui.notify(f'Removed {active_tab} from Area 2')

# --- Shared Menu Function ---
# This function creates the header, horizontal menu (desktop),
# and drawer (mobile).

def create_menu():
    """Create the responsive header and navigation drawer."""

    global load_area_2_content
    
    # TODO: Consider dark mode latter
    # Dark Mode
    # ui.dark_mode().toggle()
    
    # Use app.storage.user to store session-specific state
    # This keeps the drawer state unique for each user
    app.storage.user.setdefault('left_drawer_open', False)

    # --- Header ---
    with ui.header(elevated=True).classes('bg-primary text-white'):
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
                         with ui.image(os.path.join(BIBLEMATEWEB_APP_DIR, 'eliranwong.jpg')) as image:
                            with image.add_slot('error'):
                                ui.icon('account_circle').classes('m-auto') # Center fallback icon

                # --- Desktop Avatar + Title (Home) ---
                # The button contains a row with the avatar and the label
                with ui.button(on_click=lambda: ui.navigate.to('/')).props('flat text-color=white').classes('gt-xs'):
                    with ui.row().classes('items-center no-wrap'):
                        # Use a fallback icon in case the image fails to load
                        with ui.avatar(size='32px'):
                            with ui.image(os.path.join(BIBLEMATEWEB_APP_DIR, 'eliranwong.jpg')) as image:
                                with image.add_slot('error'):
                                    ui.icon('account_circle').classes('m-auto') # Center fallback icon
                        
                        # This is just a label now; the parent button handles the click
                        ui.label('BibleMate AI').classes('text-lg ml-2') # Added margin-left for spacing

            # --- Right Aligned Group (Features & About Us) ---
            with ui.row().classes('items-center no-wrap'):
                
                # --- Desktop Menu (Features & About) ---
                # This row contains buttons only visible on desktop
                with ui.row().classes('gt-xs items-center no-wrap'):                            
                    # Bibles
                    with ui.button('Bibles').props('flat color=white'):
                        with ui.menu():
                            ui.menu_item('Add Bible Tab', on_click=add_tab_area1)
                            ui.menu_item('Remove Bible Tab', on_click=remove_tab_area1)
                            ui.separator()
                            ui.menu_item('Original Reader’s Bible', on_click=lambda: load_area_1_content(original_reader, 'ORB'))
                            ui.menu_item('Original Interlinear Bible', on_click=lambda: load_area_1_content(original_interlinear, 'OIB'))
                            ui.menu_item('Original Parallel Bible', on_click=lambda: load_area_1_content(original_parallel, 'OPB'))
                            ui.menu_item('Original Discourse Bible', on_click=lambda: load_area_1_content(original_discourse, 'ODB'))
                            ui.menu_item('Original Linguistic Bible', on_click=lambda: load_area_1_content(original_linguistic, 'OLB'))
                            ui.separator()
                            ui.menu_item('Bible Chapter', on_click=lambda: ui.navigate.to('/bibles/chapter'))
                            ui.menu_item('Bible Verse', on_click=lambda: ui.navigate.to('/bibles/verse'))
                            ui.menu_item('Bible Audio', on_click=lambda: load_area_2_content(bibles_audio, 'Audio'))
                            ui.menu_item('Compare Chapter', on_click=lambda: ui.navigate.to('/compare/chapter'))
                            ui.menu_item('Compare Verse', on_click=lambda: ui.navigate.to('/compare/verse'))

                    # Bible Tools
                    with ui.button('Tools').props('flat color=white'):
                        with ui.menu():
                            ui.menu_item('Add Tool Tab', on_click=add_tab_area2)
                            ui.menu_item('Remove Tool Tab', on_click=remove_tab_area2)
                            ui.separator()
                            ui.menu_item('Bible Commentaries', on_click=lambda: ui.navigate.to('/tool/commentary'))
                            ui.menu_item('Cross-references', on_click=lambda: ui.navigate.to('/tool/xref'))
                            ui.menu_item('Treasury of Scripture Knowledge', on_click=lambda: ui.navigate.to('/tool/tske'))
                            ui.menu_item('Discourse Analysis', on_click=lambda: ui.navigate.to('/tool/discourse'))
                            ui.menu_item('Morphological Data', on_click=lambda: ui.navigate.to('/tool/morphology'))
                            ui.menu_item('Translation Spectrum', on_click=lambda: ui.navigate.to('/tool/translations'))
                            ui.menu_item('Bible Timelines', on_click=lambda: ui.navigate.to('/tool/timelines'))
                            ui.menu_item('Bible Chronology', on_click=lambda: load_area_2_content(bible_chronology, 'Chronology'))
                
                # --- Mobile "About Us" Icon Button ---
                # This button is only visible on mobile

                """with ui.button(icon='book').props('flat color=white round'):
                    with ui.menu():
                        ..."""
                
                with ui.button(icon='search').props('flat color=white round').tooltip('Search'):
                    with ui.menu():
                        ui.menu_item('Bibles', on_click=lambda: ui.navigate.to('/search/bible'))
                        ui.menu_item('Parallels', on_click=lambda: ui.navigate.to('/search/parallels'))
                        ui.menu_item('Promises', on_click=lambda: ui.navigate.to('/search/promises'))
                        ui.menu_item('Topics', on_click=lambda: ui.navigate.to('/search/topics'))
                        ui.menu_item('Names', on_click=lambda: ui.navigate.to('/search/names'))
                        ui.menu_item('Characters', on_click=lambda: ui.navigate.to('/search/characters'))
                        ui.menu_item('Locations', on_click=lambda: ui.navigate.to('/search/locations'))
                        ui.menu_item('Dictionary', on_click=lambda: ui.navigate.to('/search/dictionary'))
                        ui.menu_item('Encyclopedia', on_click=lambda: ui.navigate.to('/search/encyclopedia'))
                        ui.menu_item('Lexicon', on_click=lambda: ui.navigate.to('/search/lexicon'))

                with ui.button(icon='bolt').props('flat color=white round').tooltip('AI'):
                    with ui.menu():
                        ui.menu_item('AI Commentary', on_click=lambda: ui.navigate.to('/ai/commentary'))
                        ui.menu_item('AI Q&A', on_click=lambda: ui.navigate.to('/ai/qna'))
                        ui.menu_item('AI Chat', on_click=lambda: load_area_2_content(ai_chat, 'Chat'))
                        ui.menu_item('Partner Mode', on_click=lambda: ui.navigate.to('/ai/partner'))
                        ui.menu_item('Agent Mode', on_click=lambda: ui.navigate.to('/ai/agent'))

                ui.button(on_click=swap_layout, icon='swap_horiz').props('flat color=white round').tooltip('Swap Layout')

    # --- Drawer (Mobile Menu) ---
    # This section is unchanged
    with ui.drawer('left') \
            .classes('lt-sm') \
            .props('overlay') \
            .bind_value(app.storage.user, 'left_drawer_open') as left_drawer:
        
        ui.label('Navigation').classes('text-xl p-4')

        # Home Link
        ui.item('Home', on_click=lambda: (
            ui.navigate.to('/'),
            app.storage.user.update(left_drawer_open=False)
        )).props('clickable')

        # Original Bible Suite
        with ui.expansion('Original', icon='book').props('header-class="text-primary"'):
            ui.item('Original Reader’s Bible', on_click=lambda: (
                ui.navigate.to('/original/reader'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Interlinear Bible', on_click=lambda: (
                ui.navigate.to('/original/interlinear'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Parallel Bible', on_click=lambda: (
                ui.navigate.to('/original/parallel'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Discourse Bible', on_click=lambda: (
                ui.navigate.to('/original/discourse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Original Linguistic Bible', on_click=lambda: (
                ui.navigate.to('/original/linguistic'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # Bibles
        with ui.expansion('Bibles', icon='book').props('header-class="text-primary"'):
            ui.item('Bible Chapter', on_click=lambda: (
                ui.navigate.to('/bibles/chapter'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Verse', on_click=lambda: (
                ui.navigate.to('/bibles/verse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Audio', on_click=lambda: (
                ui.navigate.to('/bibles/audio'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Compare Chapter', on_click=lambda: (
                ui.navigate.to('/compare/chapter'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Compare Verse', on_click=lambda: (
                ui.navigate.to('/compare/verse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # Bible Tools
        with ui.expansion('Tools', icon='build').props('header-class="text-primary"'):
            ui.item('Bible Commentaries', on_click=lambda: (
                ui.navigate.to('/tool/commentary'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Cross-references', on_click=lambda: (
                ui.navigate.to('/tool/xref'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Treasury of Scripture Knowledge', on_click=lambda: (
                ui.navigate.to('/tool/tske'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Discourse Analysis', on_click=lambda: (
                ui.navigate.to('/tool/discourse'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Morphological Data', on_click=lambda: (
                ui.navigate.to('/tool/morphology'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Translation Spectrum', on_click=lambda: (
                ui.navigate.to('/tool/translations'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Timelines', on_click=lambda: (
                ui.navigate.to('/tool/timelines'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Bible Chronology', on_click=lambda: (
                ui.navigate.to('/tool/chronology'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # Search
        with ui.expansion('Search', icon='search').props('header-class="text-primary"'):
            ui.item('Bibles', on_click=lambda: (
                ui.navigate.to('/search/bible'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Parallels', on_click=lambda: (
                ui.navigate.to('/search/parallels'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Promises', on_click=lambda: (
                ui.navigate.to('/search/promises'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Topics', on_click=lambda: (
                ui.navigate.to('/search/topics'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Names', on_click=lambda: (
                ui.navigate.to('/search/names'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Characters', on_click=lambda: (
                ui.navigate.to('/search/characters'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Locations', on_click=lambda: (
                ui.navigate.to('/search/locations'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Dictionary', on_click=lambda: (
                ui.navigate.to('/search/dictionary'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Encyclopedia', on_click=lambda: (
                ui.navigate.to('/search/encyclopedia'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Lexicon', on_click=lambda: (
                ui.navigate.to('/search/lexicon'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
        
        # AI
        with ui.expansion('AI', icon='bolt').props('header-class="text-primary"'):
            ui.item('AI Commentary', on_click=lambda: (
                ui.navigate.to('/ai/commentary'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('AI Q&A', on_click=lambda: (
                ui.navigate.to('/ai/qna'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('AI Chat', on_click=lambda: (
                ui.navigate.to('/ai/chat'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Partner Mode', on_click=lambda: (
                ui.navigate.to('/ai/partner'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Agent Mode', on_click=lambda: (
                ui.navigate.to('/ai/agent'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')

        # About Expansion
        '''with ui.expansion('About Us', icon='info'):
            ui.item('Our Church', on_click=lambda: (
                ui.navigate.to('/about'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')
            ui.item('Contact', on_click=lambda: (
                ui.navigate.to('/contact'),
                app.storage.user.update(left_drawer_open=False)
            )).props('clickable')'''
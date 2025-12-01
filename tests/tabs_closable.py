from nicegui import ui

# Global variable to track current layout
current_layout = 1  # 1, 2, or 3
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
area1_tab_refs = {}  # Store references to tab elements
area2_tab_refs = {}
area1_tab_panels_container = None
area2_tab_panels_container = None
area1_tab_counter = 3  # Counter for new tabs in Area 1
area2_tab_counter = 5  # Counter for new tabs in Area 2


def create_closable_tab(tabs_container, tab_panels, tab_panels_container, tab_refs, tab_name, label, area_num):
    """Create a tab with a close button inline with the label"""
    with tabs_container:
        tab = ui.tab(tab_name, label=label)
        tab_refs[tab_name] = tab
        
        # Make the tab content area a flex row so button appears inline
        tab.classes('closable-tab')
        
        with tab:
            def close_this_tab(name=tab_name):
                close_tab(tabs_container, tab_panels, tab_panels_container, tab_refs, name, area_num)
            
            close_btn = ui.button(
                icon='close',
                on_click=close_this_tab
            ).props('flat dense round size=xs').classes('close-btn opacity-50 hover:opacity-100')
            close_btn.on('click', js_handler='(e) => e.stopPropagation()')
    
    return tab


def close_tab(tabs_container, tab_panels, tab_panels_container, tab_refs, tab_name, area_num):
    """Close a specific tab"""
    # Don't allow removing if it's the last tab
    if len(tab_panels) <= 1:
        ui.notify('Cannot remove the last tab!', type='warning')
        return
    
    # Check if this is the active tab
    is_active = tab_panels_container.value == tab_name
    
    # Find remaining tabs
    remaining_tabs = [k for k in tab_panels.keys() if k != tab_name]
    
    # If closing active tab, switch to another one first
    if is_active and remaining_tabs:
        tab_panels_container.set_value(remaining_tabs[0])
    
    # Remove the tab
    if tab_name in tab_refs:
        tabs_container.remove(tab_refs[tab_name])
        del tab_refs[tab_name]
    
    # Remove the tab panel
    if tab_name in tab_panels:
        tab_panels[tab_name].parent_slot.parent.delete()
        del tab_panels[tab_name]


@ui.page('/')
def page_home(q: str | None = None):
    # Add CSS to style the closable tabs with inline close button
    ui.add_head_html('''
    <style>
        /* Make tab content area horizontal so close button is inline with label */
        .closable-tab .q-tab__content {
            flex-direction: row !important;
            align-items: center !important;
            gap: 4px;
        }
        /* Smaller close button */
        .closable-tab .close-btn {
            min-height: 20px !important;
            min-width: 20px !important;
            padding: 2px !important;
        }
        .closable-tab .close-btn .q-icon {
            font-size: 14px !important;
        }
    </style>
    ''')
    create_menu()
    create_content_areas()


def create_menu():
    """Create horizontal navigation bar at the top"""
    with ui.header().classes('items-center'):
        with ui.row().classes('items-center gap-4'):
            ui.button('Swap Layout', on_click=swap_layout, icon='swap_horiz')
            ui.button('Example Page 1', on_click=load_area_1_content, icon='description')
            ui.button('Example Page 2', on_click=load_area_2_content, icon='article')
            ui.separator().props('vertical')
            ui.button('Add Tab Area 1', on_click=add_tab_area1, icon='add')
            ui.separator().props('vertical')
            ui.button('Add Tab Area 2', on_click=add_tab_area2, icon='add')


def check_breakpoint(ev):
    global is_lt_sm, splitter
    width = getattr(ev, 'width', None)
    if width is None:
        for maybe in ('args', 'arguments', 'data', 'payload'):
            candidate = getattr(ev, maybe, None)
            if isinstance(candidate, dict) and 'width' in candidate:
                width = candidate['width']
                break
    if width is None:
        print('Could not determine width from event:', ev)
        return
    is_lt_sm = width < 640
    if splitter:
        if is_lt_sm:
            splitter.props('horizontal')
        else:
            splitter.props(remove='horizontal')


def create_content_areas():
    """Create two scrollable areas with responsive layout"""
    global area1_wrapper, area2_wrapper, splitter, is_lt_sm
    global area1_tabs, area2_tabs, area1_tab_panels, area2_tab_panels
    global area1_tab_panels_container, area2_tab_panels_container
    global area1_tab_refs, area2_tab_refs
    
    ui.on('resize', check_breakpoint)
    splitter = ui.splitter(value=100, horizontal=is_lt_sm).classes('w-full').style('height: calc(100vh - 64px)')
    
    # Area 1 with closable tabs
    with splitter.before:
        area1_wrapper = ui.column().classes('w-full h-full')
        with area1_wrapper:
            area1_tabs = ui.tabs().classes('w-full')
            
            area1_tab_panels_container = ui.tab_panels(area1_tabs, value='tab1_1').classes('w-full h-full')
            
            # Create initial tabs with close buttons
            for i, (tab_name, label) in enumerate([('tab1_1', 'Bible 1'), ('tab1_2', 'Bible 2'), ('tab1_3', 'Bible 3')]):
                create_closable_tab(area1_tabs, area1_tab_panels, area1_tab_panels_container, area1_tab_refs, tab_name, label, 1)
                
                with area1_tab_panels_container:
                    with ui.tab_panel(tab_name):
                        area1_tab_panels[tab_name] = ui.scroll_area().classes('w-full h-full p-4')
                        with area1_tab_panels[tab_name]:
                            if i == 0:
                                ui.label('Bible Area').classes('text-2xl font-bold mb-4')
                                ui.label('Bible content is placed here.').classes('text-gray-600')
    
    # Area 2 with closable tabs
    with splitter.after:
        area2_wrapper = ui.column().classes('w-full h-full')
        with area2_wrapper:
            area2_tabs = ui.tabs().classes('w-full')
            
            area2_tab_panels_container = ui.tab_panels(area2_tabs, value='tab2_1').classes('w-full h-full')
            
            # Create initial tabs with close buttons
            for i, (tab_name, label) in enumerate([
                ('tab2_1', 'Tool 1'), ('tab2_2', 'Tool 2'), ('tab2_3', 'Tool 3'),
                ('tab2_4', 'Tool 4'), ('tab2_5', 'Tool 5')
            ]):
                create_closable_tab(area2_tabs, area2_tab_panels, area2_tab_panels_container, area2_tab_refs, tab_name, label, 2)
                
                with area2_tab_panels_container:
                    with ui.tab_panel(tab_name):
                        area2_tab_panels[tab_name] = ui.scroll_area().classes('w-full h-full p-4')
                        with area2_tab_panels[tab_name]:
                            if i == 0:
                                ui.label('Tool Area').classes('text-2xl font-bold mb-4')
                                ui.label('Tool content is placed here.').classes('text-gray-600')
    
    update_visibility()


def swap_layout():
    """Swap between three layout modes"""
    global current_layout
    current_layout = (current_layout % 3) + 1
    update_visibility()
    ui.notify(f'Switched to Layout {current_layout}')


def update_visibility():
    """Update visibility of areas based on current layout"""
    global current_layout, area1_wrapper, area2_wrapper, splitter
    
    if current_layout == 1:
        area1_wrapper.set_visibility(True)
        area2_wrapper.set_visibility(False)
        splitter.set_value(100)
    elif current_layout == 2:
        area1_wrapper.set_visibility(True)
        area2_wrapper.set_visibility(True)
        splitter.set_value(50)
    elif current_layout == 3:
        area1_wrapper.set_visibility(False)
        area2_wrapper.set_visibility(True)
        splitter.set_value(0)


def get_active_area1_tab():
    global area1_tab_panels_container
    return area1_tab_panels_container.value


def get_active_area2_tab():
    global area2_tab_panels_container
    return area2_tab_panels_container.value


def load_area_1_content(content=None, title="Bible"):
    """Load example content in the active tab of Area 1"""
    global area1_tab_panels, area1_tab_refs
    
    active_tab = get_active_area1_tab()
    active_panel = area1_tab_panels[active_tab]
    active_panel.clear()
    
    with active_panel:
        if content:
            content()
        else:
            ui.label('Example Page 1 Content').classes('text-xl')
            ui.label('This is sample content loaded into the active tab.')
    
    # Update tab label using props
    if active_tab in area1_tab_refs:
        area1_tab_refs[active_tab].props(f'label="{title}"')


def load_area_2_content(content=None, title="Tool"):
    """Load example content in the active tab of Area 2"""
    global area2_tab_panels, area2_tab_refs
    
    active_tab = get_active_area2_tab()
    active_panel = area2_tab_panels[active_tab]
    active_panel.clear()
    
    with active_panel:
        if content:
            content()
        else:
            ui.label('Example Page 2 Content').classes('text-xl')
            ui.label('This is sample content loaded into the active tab.')
    
    # Update tab label using props
    if active_tab in area2_tab_refs:
        area2_tab_refs[active_tab].props(f'label="{title}"')


def add_tab_area1():
    """Dynamically add a new tab to Area 1"""
    global area1_tab_counter, area1_tabs, area1_tab_panels, area1_tab_panels_container, area1_tab_refs
    
    area1_tab_counter += 1
    new_tab_name = f'tab1_{area1_tab_counter}'
    
    create_closable_tab(area1_tabs, area1_tab_panels, area1_tab_panels_container, area1_tab_refs, 
                        new_tab_name, f'Bible {area1_tab_counter}', 1)
    
    with area1_tab_panels_container:
        with ui.tab_panel(new_tab_name):
            area1_tab_panels[new_tab_name] = ui.scroll_area().classes('w-full h-full p-4')
    
    # Switch to the new tab
    area1_tab_panels_container.set_value(new_tab_name)


def add_tab_area2():
    """Dynamically add a new tab to Area 2"""
    global area2_tab_counter, area2_tabs, area2_tab_panels, area2_tab_panels_container, area2_tab_refs
    
    area2_tab_counter += 1
    new_tab_name = f'tab2_{area2_tab_counter}'
    
    create_closable_tab(area2_tabs, area2_tab_panels, area2_tab_panels_container, area2_tab_refs,
                        new_tab_name, f'Tool {area2_tab_counter}', 2)
    
    with area2_tab_panels_container:
        with ui.tab_panel(new_tab_name):
            area2_tab_panels[new_tab_name] = ui.scroll_area().classes('w-full h-full p-4')
    
    # Switch to the new tab
    area2_tab_panels_container.set_value(new_tab_name)


ui.run(port=9999)
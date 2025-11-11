from nicegui import ui

# Option 1

ui.label('Simple Horizontal Scroll').classes('text-h6')

# 'overflow-x-auto' enables horizontal scrolling when needed
# 'no-wrap' prevents buttons from falling to the next line
with ui.row().classes('w-full overflow-x-auto no-wrap scroll_row'):
    for i in range(15):
        ui.button(icon='book', on_click=lambda i=i: ui.notify(f'Opened Book {i}'))

# Option 1b

ui.label('Row with Horizontal-Only Scroll').classes('text-h6')

# 'overflow-x-auto': Enables horizontal scroll only when needed
# 'overflow-y-hidden': Disables vertical scroll and hides the scrollbar
# 'no-wrap': Keeps all buttons on a single line
# 'py-2': Adds a little vertical padding, which is more flexible than a fixed height
with ui.row().classes('w-full overflow-x-auto overflow-y-hidden no-wrap py-2'):
    for i in range(15):
        # .props('dense') makes the buttons a bit smaller and more compact
        ui.button(icon='bookmark', color='secondary').props('dense')

# Option 2

ui.label('NiceGUI Scroll Area').classes('text-h6')

with ui.scroll_area().classes('w-full h-16 overflow-y-hidden'):
    with ui.row().classes('no-wrap'):
        for i in range(15):
            ui.button(icon='bookmark', color='secondary')

# Option 3

ui.label('Carousel Menu with Arrows').classes('text-h6')

with ui.carousel(animated=True, arrows=True, navigation=False) \
        .classes('w-full h-14 bg-gray-100'):
    # Slide 1
    with ui.carousel_slide().classes('p-1'):
        with ui.row().classes('w-full justify-evenly no-wrap'):
             ui.button(icon='home', on_click=lambda: ui.notify('Home')) \
                .props('flat round dense')
             ui.button(icon='search', on_click=lambda: ui.notify('Search')) \
                .props('flat round dense')
             ui.button(icon='menu_book', on_click=lambda: ui.notify('Read')) \
                .props('flat round dense')
             ui.button(icon='settings', on_click=lambda: ui.notify('Settings')) \
                .props('flat round dense')
    # Slide 2
    with ui.carousel_slide().classes('p-1'):
        with ui.row().classes('w-full justify-evenly no-wrap'):
             ui.button(icon='info', on_click=lambda: ui.notify('Info')) \
                .props('flat round dense')
             ui.button(icon='help', on_click=lambda: ui.notify('Help')) \
                .props('flat round dense')
             ui.button(icon='logout', on_click=lambda: ui.notify('Logout')) \
                .props('flat round dense')

# Option 4

ui.label('Resize browser to see arrows appear/disappear').classes('text-h6 m-4')

with ui.tabs().classes('w-full bg-primary text-white shadow-2') \
        .props('dense narrow-indicator align="left"'):

    # The first argument 'home', 'bible', etc. is the required unique name
    ui.tab('home', icon='home', label='Home').on('click', lambda: ui.notify('Go Home'))
    ui.tab('bible', icon='menu_book', label='Bible').on('click', lambda: ui.notify('Open Bible'))
    ui.tab('search', icon='search').on('click', lambda: ui.notify('Search'))

    for i in range(1, 8):
        # Using f-string to generate unique names for the loop
        ui.tab(f'bookmark_{i}', icon='bookmark', label=f'Bk {i}') \
            .on('click', lambda i=i: ui.notify(f'Bookmark {i}'))

    ui.tab('settings', icon='settings').on('click', lambda: ui.notify('Settings'))

# Option 5

ui.label('Resize browser to see arrows appear/disappear').classes('text-h6 m-4')

with ui.tabs().classes('w-full bg-primary text-white shadow-2') \
        .props('dense narrow-indicator align="right"'):

    # The first argument 'home', 'bible', etc. is the required unique name
    ui.tab('', icon='home').on('click', lambda: ui.notify('Go Home'))
    ui.tab('', icon='menu_book').on('click', lambda: ui.notify('Open Bible'))
    ui.tab('', icon='search').on('click', lambda: ui.notify('Search'))

    for i in range(1, 8):
        # Using f-string to generate unique names for the loop
        ui.tab('', icon='bookmark') \
            .on('click', lambda i=i: ui.notify(f'Bookmark {i}'))

    ui.tab('', icon='settings').on('click', lambda: ui.notify('Settings'))

# Option 6:

ui.label('Click the "Bible" tab to see the menu').classes('text-h6 m-4')

with ui.tabs().classes('w-full bg-primary text-white') \
        .props('dense align="right"'):

    ui.tab('home', icon='home', label=None)

    # This tab acts as a menu trigger
    with ui.tab('bible_menu', icon='menu_book', label='Bible'):
        with ui.menu():
            ui.menu_item('Bible Chapter',
                         on_click=lambda: ui.notify('Navigating to Chapter...'))
            ui.menu_item('Bible Verse',
                         on_click=lambda: ui.notify('Navigating to Verse...'))
            ui.separator()
            ui.menu_item('Close Menu', on_click=lambda: ui.notify('Closed'))

    ui.tab('settings', icon='settings', label='Settings')

ui.run(port=9999)
"""
Bible Timelines Page for BibleMate AI
A clean, interactive page for viewing Bible timeline images across different periods.
"""

from nicegui import ui
from pathlib import Path
import os

# Timeline data: index -> (title, filename)
TIMELINES = {
    0: ('2210-2090 BCE', '0.png'),
    1: ('2090-1970 BCE', '1.png'),
    2: ('1970-1850 BCE', '2.png'),
    3: ('1850-1730 BCE', '3.png'),
    4: ('1750-1630 BCE', '4.png'),
    5: ('1630-1510 BCE', '5.png'),
    6: ('1510-1390 BCE', '6.png'),
    7: ('1410-1290 BCE', '7.png'),
    8: ('1290-1170 BCE', '8.png'),
    9: ('1170-1050 BCE', '9.png'),
    10: ('1050-930 BCE', '10.png'),
    11: ('930-810 BCE', '11.png'),
    12: ('810-690 BCE', '12.png'),
    13: ('690-570 BCE', '13.png'),
    14: ('570-450 BCE', '14.png'),
    15: ('470-350 BCE', '15.png'),
    16: ('350-230 BCE', '16.png'),
    17: ('240-120 BCE', '17.png'),
    18: ('120-1 BCE', '18.png'),
    19: ('10-110 CE', '19.png'),
    20: ('Gospel by Matthew', '20.png'),
    21: ('Gospel by Mark', '21.png'),
    22: ('Gospel by Luke', '22.png'),
    23: ('Gospel by John', '23.png'),
    24: ('All 4 Gospels', '24.png'),
}

# Group timelines for better organization
OT_TIMELINES = [(k, v[0]) for k, v in TIMELINES.items() if k <= 19]
GOSPEL_TIMELINES = [(k, v[0]) for k, v in TIMELINES.items() if k >= 20]

# Image base path - adjust this to your actual path
IMAGE_BASE_PATH = os.path.expanduser("~/UniqueBible/marvelData/books/Timelines")  # e.g., "static/timelines" or wherever your images are


def create_timelines_page():
    """Create the Bible timelines page."""
    
    # State
    selected_index = {'value': 0}
    fit_to_width = {'value': True}
    
    # References to UI elements
    image_container = {'ref': None}
    title_label = {'ref': None}
    
    def get_image_path(index: int) -> str:
        """Get the image path for a given timeline index."""
        filename = TIMELINES[index][1]
        return f"{IMAGE_BASE_PATH}/{filename}"
    
    def get_title(index: int) -> str:
        """Get the title for a given timeline index."""
        return TIMELINES[index][0]
    
    def update_image():
        """Update the displayed image."""
        image_container['ref'].clear()
        with image_container['ref']:
            img_path = get_image_path(selected_index['value'])
            if fit_to_width['value']:
                ui.image(img_path).classes('w-full max-w-full')
            else:
                # Actual size with scroll
                ui.image(img_path).classes('')
        
        title_label['ref'].set_text(get_title(selected_index['value']))
    
    def select_timeline(index: int):
        """Select a timeline by index."""
        selected_index['value'] = index
        update_image()
    
    def toggle_fit_mode(value: bool):
        """Toggle between fit-to-width and actual size."""
        fit_to_width['value'] = value
        update_image()
    
    def go_previous():
        """Go to previous timeline."""
        if selected_index['value'] > 0:
            select_timeline(selected_index['value'] - 1)
    
    def go_next():
        """Go to next timeline."""
        if selected_index['value'] < len(TIMELINES) - 1:
            select_timeline(selected_index['value'] + 1)
    
    # Page layout
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        
        # Header
        with ui.row().classes('w-full bg-amber-800 text-white p-4 items-center justify-between shadow-md'):
            ui.label('📜 Bible Timelines').classes('text-2xl font-bold')
            title_label['ref'] = ui.label(get_title(0)).classes('text-xl')
        
        # Controls bar
        with ui.row().classes('w-full bg-white p-3 items-center gap-4 shadow-sm flex-wrap'):
            
            # Period dropdown
            with ui.row().classes('items-center gap-2'):
                ui.label('Period:').classes('font-medium text-gray-700')
                options = {k: v[0] for k, v in TIMELINES.items()}
                ui.select(
                    options=options,
                    value=0,
                    on_change=lambda e: select_timeline(e.value)
                ).classes('w-48')
            
            ui.separator().props('vertical').classes('h-8')
            
            # Navigation buttons
            with ui.row().classes('items-center gap-2'):
                ui.button(icon='chevron_left', on_click=go_previous).props('flat round').tooltip('Previous')
                ui.button(icon='chevron_right', on_click=go_next).props('flat round').tooltip('Next')
            
            ui.separator().props('vertical').classes('h-8')
            
            # View mode toggle
            with ui.row().classes('items-center gap-2'):
                ui.label('View:').classes('font-medium text-gray-700')
                ui.toggle(
                    {True: 'Fit to Width', False: 'Actual Size'},
                    value=True,
                    on_change=lambda e: toggle_fit_mode(e.value)
                ).props('no-caps')
        
        # Quick access chips
        with ui.expansion('Quick Access', icon='schedule').classes('w-full bg-white'):
            with ui.column().classes('p-2 gap-3'):
                
                # Old Testament periods
                ui.label('Old Testament Periods').classes('font-medium text-gray-600')
                with ui.row().classes('flex-wrap gap-2'):
                    for idx, title in OT_TIMELINES:
                        ui.chip(
                            title,
                            on_click=lambda i=idx: select_timeline(i),
                            color='amber'
                        ).props('clickable outline')
                
                ui.separator()
                
                # Gospel timelines
                ui.label('Gospel Timelines').classes('font-medium text-gray-600')
                with ui.row().classes('flex-wrap gap-2'):
                    for idx, title in GOSPEL_TIMELINES:
                        ui.chip(
                            title,
                            on_click=lambda i=idx: select_timeline(i),
                            color='blue'
                        ).props('clickable outline')
        
        # Image display area
        with ui.scroll_area().classes('flex-grow w-full bg-gray-100'):
            image_container['ref'] = ui.column().classes('w-full p-4 items-center')
            with image_container['ref']:
                ui.image(get_image_path(0)).classes('w-full max-w-full')
        
        # Footer with keyboard shortcuts hint
        with ui.row().classes('w-full bg-gray-200 p-2 justify-center'):
            ui.label('💡 Tip: Use the dropdown or chips to quickly jump between periods').classes('text-sm text-gray-600')
    
    # Keyboard navigation
    ui.keyboard(on_key=lambda e: go_previous() if e.key == 'ArrowLeft' and e.action.keydown else (
        go_next() if e.key == 'ArrowRight' and e.action.keydown else None
    ))


# For standalone testing
if __name__ in {"__main__", "__mp_main__"}:
    create_timelines_page()
    ui.run(title='Bible Timelines', port=9999)
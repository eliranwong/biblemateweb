import os
from nicegui import ui, app

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

# Set this to False to use your real images
USE_PLACEHOLDERS = False

TIMELINE_DATA = {
    0: ('2210-2090 BCE', '0.png'), 1: ('2090-1970 BCE', '1.png'), 
    2: ('1970-1850 BCE', '2.png'), 3: ('1850-1730 BCE', '3.png'), 
    4: ('1750-1630 BCE', '4.png'), 5: ('1630-1510 BCE', '5.png'), 
    6: ('1510-1390 BCE', '6.png'), 7: ('1410-1290 BCE', '7.png'), 
    8: ('1290-1170 BCE', '8.png'), 9: ('1170-1050 BCE', '9.png'), 
    10: ('1050-930 BCE', '10.png'), 11: ('930-810 BCE', '11.png'), 
    12: ('810-690 BCE', '12.png'), 13: ('690-570 BCE', '13.png'), 
    14: ('570-450 BCE', '14.png'), 15: ('470-350 BCE', '15.png'), 
    16: ('350-230 BCE', '16.png'), 17: ('240-120 BCE', '17.png'), 
    18: ('120-1 BCE', '18.png'), 19: ('10-110 CE', '19.png'), 
    20: ('Matthew', '20.png'), 21: ('Mark', '21.png'), 
    22: ('Luke', '22.png'), 23: ('John', '23.png'), 
    24: ('All 4 Gospels', '24.png')
}

DROPDOWN_OPTIONS = {
    k: f"{v[0].replace('_', ' ')}" 
    for k, v in TIMELINE_DATA.items()
}

# Serve the local folder containing images so NiceGUI can access them
# We map the URL '/static' to your specific folder path
app.add_static_files('/timelines', os.path.expanduser("~/UniqueBible/marvelData/books/Timelines"))

# -----------------------------------------------------------------------------
# APP LOGIC
# -----------------------------------------------------------------------------

@ui.page('/')
def timeline_page():
    
    # --- Helper Functions ---
    def get_image_source(idx):
        if idx is None: return "" # Handle initial load safety
        
        filename = TIMELINE_DATA[idx][1]
        title = TIMELINE_DATA[idx][0]
        
        if USE_PLACEHOLDERS:
            # Generate dummy image
            width = 1800 if idx % 2 == 0 else 800
            text = title.replace(' ', '+')
            return f"https://placehold.co/{width}x1000?text={text}"
        else:
            return f"/timelines/{filename}"

    # --- UI Layout ---
    
    # 1. Header with Zoom Switch
    with ui.header().classes('bg-slate-800 text-white shadow-md'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('BibleMate AI: Timelines').classes('text-lg font-bold')
            
            with ui.row().classes('items-center gap-2'):
                ui.icon('aspect_ratio', size='xs')
                # We define the switch here. We will read its value later.
                fit_switch = ui.switch('Fit Width', value=True).props('color=green-4')

    # 2. Main Content
    with ui.column().classes('w-full h-[calc(100vh-60px)] p-0 gap-0 bg-slate-100 dark:bg-slate-900'):
        
        # --- Navigation Bar ---
        with ui.row().classes('w-full p-4 items-center justify-center gap-4 bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-gray-700'):
            
            prev_btn = ui.button(icon='chevron_left').props('round flat').classes('text-slate-700 dark:text-slate-200')
            
            # The Dropdown is our "Source of Truth" for the current ID
            period_select = ui.select(
                options=DROPDOWN_OPTIONS, 
                value=0, # Start at 0
                label='Select Period'
            ).classes('w-64 min-w-[200px]')
            
            next_btn = ui.button(icon='chevron_right').props('round flat').classes('text-slate-700 dark:text-slate-200')

            # Define button logic to manipulate the select's value
            def next_period():
                if period_select.value < max(TIMELINE_DATA.keys()):
                    period_select.value += 1

            def prev_period():
                if period_select.value > min(TIMELINE_DATA.keys()):
                    period_select.value -= 1

            # Attach handlers
            prev_btn.on_click(prev_period)
            next_btn.on_click(next_period)
            
            # Bind button enabled state to the select value
            # We use lambda to check boundaries
            prev_btn.bind_enabled_from(period_select, 'value', backward=lambda x: x > 0)
            next_btn.bind_enabled_from(period_select, 'value', backward=lambda x: x < 24)

        # --- Image Display Area ---
        with ui.scroll_area().classes('w-full flex-grow relative bg-gray-200'):
            # Use a simpler container structure. 
            # w-full: ensures it spans width. 
            # items-start: ensures large images don't get clipped on the left by 'center' alignment.
            with ui.column().classes('w-full min-h-full items-start transition-all'):
                
                # This function refreshes whenever called
                @ui.refreshable
                def render_timeline_image():
                    current_idx = period_select.value
                    is_fit = fit_switch.value
                    
                    src = get_image_source(current_idx)
                    title = TIMELINE_DATA[current_idx][0].replace('_', ' ')
                    
                    # CSS Logic
                    if is_fit:
                        # Fit to screen: 100% width, maintain aspect ratio
                        img_style = "width: 100%; height: auto; display: block;"
                    else:
                        # Actual size: Reset width/max-width to allow natural size
                        img_style = "width: auto; max-width: none; display: block;"
                    
                    # CHANGED: Switched from ui.image() to ui.element('img')
                    # ui.image uses Quasar's q-img which can collapse to 0 height if width is auto.
                    # Native <img> tag is much more reliable for "Actual Size" scrolling.
                    # We add 'mx-auto' to center it when it is smaller than the screen.
                    ui.element('img').props(f'src="{src}"').style(img_style).classes('transition-all duration-300 shadow-lg mx-auto')
                    
                    if is_fit:
                        ui.label(f"Viewing: {title}").classes('mt-2 text-gray-500 text-sm mx-auto')

                # Render initially
                render_timeline_image()
                
                # --- REACTIVITY ---
                # When the select changes, refresh the image
                period_select.on_value_change(render_timeline_image.refresh)
                # When the switch changes, refresh the image (to update CSS)
                fit_switch.on_value_change(render_timeline_image.refresh)

ui.run(title='BibleMate Timelines', favicon='📖', port=9999)
import os
from nicegui import ui, app
from biblemateweb.data.bible_timelines import bible_timelines as TIMELINE_DATA
from biblemateweb import get_translation

def bible_timelines(gui=None, b=1, q="", **_):

    # -----------------------------------------------------------------------------
    # CONFIGURATION
    # -----------------------------------------------------------------------------

    # Set this to False to use your real images
    USE_PLACEHOLDERS = False

    DROPDOWN_OPTIONS = {
        k: f"{v[0].replace('_', ' ')}" 
        for k, v in TIMELINE_DATA.items()
    }

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

    # Main Content
    with ui.column().classes('w-full h-[calc(100vh-60px)] p-0 gap-0 bg-slate-100 dark:bg-slate-900'):
        
        # --- Navigation Bar ---
        with ui.row().classes('w-full p-1 items-center justify-center gap-1 border-b border-primary'):
            
            prev_btn = ui.button(icon='chevron_left').props('round flat').classes('text-secondary')
            
            # The Dropdown is our "Source of Truth" for the current ID
            period_select = ui.select(
                options=DROPDOWN_OPTIONS,
                value=0,
                label='Select Period'
            ).classes('w-30')
            
            next_btn = ui.button(icon='chevron_right').props('round flat').classes('text-secondary')

            fit_switch = ui.switch('Fit Width', value=True).props('color=primary')

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
    book_maps = {
        1: 0,
        2: 4,
        3: 6,
        4: 6,
        5: 6,
        6: 6,
        7: 7,
        8: 7,
        9: 10,
        10: 10,
        11: 10,
        12: 11,
        13: 10,
        14: 10,
        15: 14,
        16: 15,
        17: 14,
        18: 6,
        19: 10,
        20: 10,
        21: 10,
        22: 10,
        23: 12,
        24: 13,
        25: 13,
        26: 13,
        27: 13,
        28: 12,
        29: 11,
        30: 12,
        31: 11,
        32: 12,
        33: 12,
        34: 13,
        35: 13,
        36: 13,
        37: 14,
        38: 14,
        39: 15,
        40: 20,
        41: 21,
        42: 22,
        43: 23,
        44: 19,
        45: 19,
        46: 19,
        47: 19,
        48: 19,
        49: 19,
        50: 19,
        51: 19,
        52: 19,
        53: 19,
        54: 19,
        55: 19,
        56: 19,
        57: 19,
        58: 19,
        59: 19,
        60: 19,
        61: 19,
        62: 19,
        63: 19,
        64: 19,
        65: 19,
        66: 19,
    }
    period_select.value = book_maps.get(b, 0)
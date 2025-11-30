from biblemategui.data.bible_locations import BIBLE_LOCATIONS
from biblemategui.fx.location_finder import LocationFinder
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from nicegui import ui, app
from functools import partial
import math, re, asyncio


# --- Data: 66 Bible Books & ID Mapping ---
BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]

# Create a dictionary for Dropdown options: {ID: "Name (ID)"}
# This handles duplicate names by ensuring the value passed is the unique ID
LOCATION_OPTIONS = {
    uid: data[0] for uid, data in BIBLE_LOCATIONS.items()
}

# --- 2. HELPER FUNCTIONS ---

def haversine_distance(coord1, coord2, unit='km'):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    
    distance = c * r
    
    if unit == 'miles':
        return distance * 0.621371
    return distance

# --- 3. UI LAYOUT ---

def search_bible_maps(gui=None, q='', **_):

    def exlbl(event):
        nonlocal gui
        app.storage.user['tool_query'], *_ = event.args
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Locations')
    ui.on('exlbl', exlbl)

    jerusalem = (31.777, 35.235)
    parser = BibleVerseParser(False)
    finder = LocationFinder()

    location_multiselect = None
    # Apply a full height column with no wrap so the map can stretch
    with ui.column().classes('w-full h-screen no-wrap p-4 gap-4'):

        # Dictionary to keep track of added layers {loc_id: layer}
        # Leaflet in NiceGUI doesn't have a direct "get_marker_by_id", so we track them locally
        active_markers = {} 

        def update_map_markers(selected_ids):
            """
            Synchronizes the map markers with the list of selected IDs.
            """
            current_ids = set(active_markers.keys())
            target_ids = set(selected_ids)

            # 1. Remove markers that are no longer selected
            to_remove = current_ids - target_ids
            for uid in to_remove:
                bible_map.remove_layer(active_markers[uid])
                del active_markers[uid]

            # 2. Add new markers
            to_add = target_ids - current_ids
            for uid in to_add:
                name, lat, lon = BIBLE_LOCATIONS[uid]
                # Add marker with popup
                marker = bible_map.marker(latlng=(lat, lon))
                # The following line does not work when tool_query parameter is loaded when the page is opened
                #marker.run_method('bindPopup', f'''<b>{name}</b><br>[<ref onclick="emitEvent('exlbl', ['{uid}']); return false;">{uid}</ref>]''')
                # Wait until marker is ready; wait 0.1 seconds to let the JS layer catch up
                async def bind_marker(marker, name, uid):
                    # 1. Non-blocking Wait: Checks every 0.1s, but lets other app events happen
                    while marker.id is None:
                        await asyncio.sleep(0.1)
                    # 2. Add a tiny buffer for the JavaScript side to render the marker
                    await asyncio.sleep(0.1)
                    # 3. Bind
                    marker.run_method('bindPopup', f'''<b>{name}</b><br>[<ref onclick="emitEvent('exlbl', ['{uid}']); return false;">{uid}</ref>]''')
                # Fire the safe async function
                ui.timer(0.1, partial(bind_marker, marker, name, uid), once=True)
                
                active_markers[uid] = marker
                
            # If we added exactly one new marker, pan to it
            if len(to_add) == 1:
                uid = list(to_add)[0]
                lat, lon = BIBLE_LOCATIONS[uid][1], BIBLE_LOCATIONS[uid][2]
                bible_map.set_center((lat, lon))
                bible_map.set_zoom(9)
            else:
                fit_all_markers()


        # ==========================================
        # CONTROLS
        # ==========================================
        with ui.card().classes('w-full'):
            #ui.label('📍 Map Explorer').classes('text-sm font-bold text-gray-500')
            
            with ui.row().classes('w-full items-center gap-4 !p-0'):
                
                # Prepare options for multiselect with "All" and "None"
                # Using special keys that we can intercept
                multi_options = {
                    'CMD_ALL': 'All', 
                    'CMD_NONE': 'None'
                }
                multi_options.update(LOCATION_OPTIONS)

                # Multi-select dropdown
                location_multiselect = ui.select(
                    multi_options, 
                    label='Locations', 
                    multiple=True,
                    with_input=True
                ).classes('w-30').props('dense clearable')  # min-w-[40px]

                # Text Input for quick search
                search_input = ui.input(
                    #label='Search',
                    autocomplete=list(LOCATION_OPTIONS.values())+BIBLE_BOOKS,
                    placeholder='Search for location(s) or verse reference(s) ...',
                ).classes('flex-grow text-lg').props('outlined clearable autofocus enterkeyhint="search"')
                
                def on_search_enter(keep=True):
                    """Finds a location by name and adds it to the multiselect (which triggers map update)"""
                    query = search_input.value.strip()
                    if not query: return

                    if keep:
                        gui.update_active_area2_tab_records(q=query)

                    current_vals = location_multiselect.value or []

                    # when users enter verse reference(s)
                    if verseList := parser.extractAllReferences(query, tagged=False):
                        combinedLocations = []
                        for reference in verseList:
                            combinedLocations += finder.getLocationsFromReference(reference)
                        if found_id := sorted(list(set(combinedLocations))):
                            location_multiselect.value = list(set(current_vals + found_id))
                            ui.notify(f"{len(found_id)} locations found!")
                            search_input.value = ""
                            return
                    
                    # when users enter location id(s)
                    if re.search("^BL[0-9BL, ]+?$", query):
                        found_id = [i.strip() for i in query.split(",") if i.strip() in BIBLE_LOCATIONS]
                        if found_id:
                            location_multiselect.value = list(set(current_vals + found_id))
                            ui.notify(f"{len(found_id)} locations found!")
                            search_input.value = ""
                            if len(found_id) == 2:
                                loc1_select.value, loc2_select.value = found_id
                                calculate()
                            return

                    # when users enter location name(s)
                    query = search_input.value.lower()

                    found_id = []
                    for i in query.split(","):
                        i = i.strip()
                        if not i: continue
                        for uid, data in BIBLE_LOCATIONS.items():
                            if i in data[0].lower():
                                found_id.append(uid)
                                break
                    
                    if found_id:
                        # This update will trigger the on_value_change event
                        location_multiselect.value = list(set(current_vals + found_id))
                        ui.notify(f"{len(found_id)} locations found!")
                        search_input.value = "" # clear input
                    else:
                        ui.notify("Location not found", type='warning')

                search_input.on('keydown.enter.prevent', on_search_enter)

                # Intercept selection to handle "All" and "None" logic
                def handle_selection_change(e):
                    selected_values = e.value
                    
                    # Handle "All"
                    if 'CMD_ALL' in selected_values:
                        all_real_ids = list(LOCATION_OPTIONS.keys())
                        location_multiselect.value = all_real_ids
                        update_map_markers(all_real_ids)
                        return

                    # Handle "None"
                    if 'CMD_NONE' in selected_values:
                        location_multiselect.value = []
                        update_map_markers([])
                        return

                    # Normal update
                    update_map_markers(selected_values)

                # Bind the custom handler
                location_multiselect.on_value_change(handle_selection_change)

        # ==========================================
        # DISTANCE CALCULATOR
        # ==========================================
        with ui.card().classes('w-full'):
            #ui.label('📏 Bible Location Distance Calculator').classes('text-lg font-bold text-gray-700 mb-2')
            
            with ui.row().classes('w-full items-center gap-4 p-0'):
                # Location Selectors
                loc1_select = ui.select(LOCATION_OPTIONS, label='From', with_input=True).classes('w-35').props('dense')
                loc2_select = ui.select(LOCATION_OPTIONS, label='To', with_input=True).classes('w-35').props('dense')
                
                # Unit Toggle
                unit_radio = ui.radio(['km', 'miles'], value='km').props('dense inline')
                
                # Result Label
                result_label = ui.label('Distance').classes('dense text-lg font-medium text-secondary ml-auto mr-4')

                # Calculation Logic
                def calculate():
                    #nonlocal location_multiselect, result_label
                    if loc1_select.value and not loc1_select.value in location_multiselect.value:
                        location_multiselect.value = location_multiselect.value + [loc1_select.value]
                    if loc2_select.value and not loc2_select.value in location_multiselect.value:
                        location_multiselect.value = location_multiselect.value + [loc2_select.value]
                    if (loc1_select.value and not loc2_select.value) or (not loc1_select.value and loc2_select.value):
                        result_label.text = "Select one more"
                        return
                    
                    # Get coordinates from ID
                    id1 = loc1_select.value
                    id2 = loc2_select.value
                    
                    coord1 = (BIBLE_LOCATIONS[id1][1], BIBLE_LOCATIONS[id1][2])
                    coord2 = (BIBLE_LOCATIONS[id2][1], BIBLE_LOCATIONS[id2][2])
                    
                    dist = haversine_distance(coord1, coord2, unit_radio.value)
                    unit_label = "km" if unit_radio.value == 'km' else "miles"
                    
                    result_label.text = f"{dist:.2f} {unit_label}"

                # Trigger calculation on button click or change
                #ui.button('Calculate', on_click=calculate).classes('bg-blue-600 text-white')
                
                # Auto-calculate when inputs change
                loc1_select.on_value_change(calculate)
                loc2_select.on_value_change(calculate)
                unit_radio.on_value_change(calculate)

        # ==========================================
        # LEAFLET MAP
        # ==========================================

        # Fit bounds using JavaScript
        def fit_all_markers():
            if not location_multiselect.value:
                bible_map.set_center(jerusalem) # Jerusalem
                bible_map.set_zoom(9)
                return
            locations = [BIBLE_LOCATIONS[uid][1:] for uid in location_multiselect.value]
            lats = [loc[0] for loc in locations]
            lngs = [loc[1] for loc in locations]
            #center = (sum(lats)/len(lats), sum(lngs)/len(lngs))
            bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]
            ui.run_javascript(f'''
                setTimeout(() => {{
                    const element = getElement({bible_map.id});
                    if (element && element.map) {{
                        const bounds = L.latLngBounds({bounds});
                        element.map.fitBounds(bounds, {{
                            padding: [50, 50],
                            maxZoom: 12
                        }});
                    }}
                }}, 100);
            ''')

        with ui.element('div').style('position: relative; width: 100%; display: flex; flex-direction: column; height: 100%;'):
            bible_map = ui.leaflet(center=jerusalem, zoom=9).classes('w-full flex-grow rounded-lg shadow-md') # default; center on Jerusalem approx
            with ui.button(on_click=fit_all_markers).props('fab-mini color=primary icon=center_focus_strong').style(
                'position: absolute; top: 20px; right: 20px; z-index: 1000;'
            ):
                ui.tooltip('Zoom to Fit')

        if q:
            search_input.value = q
            on_search_enter(keep=False)
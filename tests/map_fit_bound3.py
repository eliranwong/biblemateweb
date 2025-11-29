from nicegui import ui

locations = [
    (31.7683, 35.2137),  # Jerusalem
    (32.7016, 35.2968),  # Nazareth
    (31.7054, 35.2024),  # Bethlehem
    (32.5568, 35.8469),  # Jordan River
    (31.5037, 35.4839)   # Dead Sea
]

# Calculate center and bounds
lats = [loc[0] for loc in locations]
lngs = [loc[1] for loc in locations]
center = (sum(lats)/len(lats), sum(lngs)/len(lngs))
bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]

ui.label("Testing fit bound")
ui.label("Testing fit bound")
ui.label("Testing fit bound")

# Create a container for the map and floating button
with ui.element('div').style('position: relative; width: 100%; height: 600px;'):
    # Create map
    m = ui.leaflet(center=center, zoom=10).style('width: 100%; height: 100%;')
    #m.tile_layer()
    
    # Add markers with labels
    place_names = ['Jerusalem', 'Nazareth', 'Bethlehem', 'Jordan River', 'Dead Sea']
    for (lat, lng), name in zip(locations, place_names):
        marker = m.marker(latlng=(lat, lng))
        #marker.tooltip(name)
    
    # Fit bounds using JavaScript
    def fit_all_markers():
        ui.run_javascript(f'''
            setTimeout(() => {{
                const element = getElement({m.id});
                if (element && element.map) {{
                    const bounds = L.latLngBounds({bounds});
                    element.map.fitBounds(bounds, {{
                        padding: [50, 50],
                        maxZoom: 12
                    }});
                }}
            }}, 100);
        ''')
    
    # Option 1: Floating action button with "zoom out map" icon
    #with ui.button(on_click=fit_all_markers).props('fab color=blue icon=zoom_out_map').style(
    #    'position: absolute; bottom: 20px; right: 20px; z-index: 1000;'
    #):
    #    ui.tooltip('Show all locations')
    
    # Option 2: Alternative position (top-right) with different icon
    #with ui.button(on_click=fit_all_markers).props('fab color=teal icon=aspect_ratio').style(
    #    'position: absolute; top: 20px; right: 20px; z-index: 1000;'
    #):
    #    ui.tooltip('Fit all markers')
    
    # Option 3: Mini FAB with fullscreen icon
    with ui.button(on_click=fit_all_markers).props('fab-mini color=primary icon=fullscreen').style(
        'position: absolute; bottom: 20px; right: 20px; z-index: 1000;'
    ):
        ui.tooltip('Reset view')

# Initial fit after map loads
ui.timer(0.5, fit_all_markers, once=True)

ui.run(port=9999)
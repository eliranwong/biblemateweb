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

# Create a container for the map and floating button
with ui.element('div').style('position: relative; width: 100%; height: 600px;'):
    # Create map
    m = ui.leaflet(center=center, zoom=10).style('width: 100%; height: 100%;')
    #m.tile_layer()
    
    # Add markers
    for lat, lng in locations:
        m.marker(latlng=(lat, lng))
    
    # Fit bounds using JavaScript (fire and forget - no await)
    def fit_all_markers():
        # Don't await - just execute
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
    
    # Add floating button with nice icon
    with ui.button(on_click=fit_all_markers).props('fab color=primary icon=center_focus_strong').style(
        'position: absolute; bottom: 20px; right: 20px; z-index: 1000;'
    ):
        ui.tooltip('Fit all markers').classes('text-center')

# Initial fit after map loads
ui.timer(0.5, fit_all_markers, once=True)

ui.run(port=9999)
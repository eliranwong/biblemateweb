from nicegui import ui

# 1. Mock Data
bible_data = {
    'Abraham': {'spouse': ['Sarah', 'Hagar'], 'sons': ['Isaac', 'Ishmael'], 'father': 'Terah'},
    'Sarah': {'spouse': ['Abraham'], 'sons': ['Isaac']},
    'Hagar': {'spouse': ['Abraham'], 'sons': ['Ishmael']},
    'Isaac': {'father': 'Abraham', 'mother': 'Sarah', 'spouse': ['Rebekah'], 'sons': ['Jacob', 'Esau']},
    'Ishmael': {'father': 'Abraham', 'mother': 'Hagar'},
    'Rebekah': {'spouse': ['Isaac'], 'sons': ['Jacob', 'Esau']},
    'Jacob': {'father': 'Isaac', 'mother': 'Rebekah', 'spouse': ['Leah', 'Rachel'], 'sons': ['Joseph', 'Benjamin']},
    'Esau': {'father': 'Isaac', 'mother': 'Rebekah'},
    'Joseph': {'father': 'Jacob', 'mother': 'Rachel'},
    'Benjamin': {'father': 'Jacob', 'mother': 'Rachel'},
}
all_names = sorted(list(bible_data.keys()))

@ui.page('/')
def index():
    # --- State ---
    # We use a simple variable, but in a real app, you might use ui.state or similar
    current_focus = 'Abraham'

    # --- UI Elements (defined early so we can reference them) ---
    search_dropdown = None 
    chart = None

    # --- Logic ---
    def get_chart_options(center_person):
        """Generates the FULL ECharts options dictionary for a person."""
        nodes = []
        links = []
        
        if center_person in bible_data:
            data = bible_data[center_person]
            
            # 1. Add Center Node
            nodes.append({
                "name": center_person, 
                "symbolSize": 60, 
                "itemStyle": {"color": "#3b82f6"}, # Blue
                "label": {"show": True, "fontWeight": "bold"}
            })

            # 2. Helper to add relations
            def add_rel(name, rel_label, color):
                if name in all_names:
                    nodes.append({
                        "name": name, 
                        "symbolSize": 40, 
                        "itemStyle": {"color": color}
                    })
                    links.append({
                        "source": center_person, 
                        "target": name, 
                        "label": {"show": True, "formatter": rel_label}
                    })

            # 3. Add relationships with colors
            if 'father' in data: add_rel(data['father'], 'Father', '#10b981') # Green
            if 'mother' in data: add_rel(data['mother'], 'Mother', '#10b981')
            for spouse in data.get('spouse', []): add_rel(spouse, 'Spouse', '#ef4444') # Red
            for son in data.get('sons', []): add_rel(son, 'Son', '#f59e0b') # Orange
            
        return {
            'title': {'text': f'Focus: {center_person}', 'left': 'center'},
            'tooltip': {},
            'series': [{
                'type': 'graph',
                'layout': 'force',
                'roam': True,
                'label': {'show': True, 'position': 'right'},
                'force': {'repulsion': 1000, 'edgeLength': 120},
                'data': nodes,
                'links': links,
                'lineStyle': {'curveness': 0.1}
            }]
        }

    def update_display(new_name):
        """Updates both the Chart and the Dropdown."""
        nonlocal current_focus
        if new_name not in all_names: return

        current_focus = new_name
        
        # 1. Update Dropdown (prevent infinite loop by checking value first)
        if search_dropdown.value != new_name:
            search_dropdown.value = new_name

        # 2. Update Chart
        # Crucial: Assign a fresh dictionary to options to trigger reactivity
        chart.options = get_chart_options(new_name)
        chart.update() 

    def handle_dropdown_change(e):
        """Called when user manually selects from dropdown."""
        update_display(e.value)

    def handle_chart_click(e):
        """Called when user clicks a node in the graph."""
        # 'dataType' tells us if they clicked a Node or a Line
        if e.args.get('dataType') == 'node':
            clicked_name = e.args['name']
            if clicked_name != current_focus:
                ui.notify(f"Navigating to {clicked_name}...", type='info')
                update_display(clicked_name)

    # --- Layout ---
    with ui.column().classes('w-full h-screen items-center p-4'):
        
        # Top Bar
        with ui.row().classes('items-center gap-4 mb-4'):
            ui.label('BibleMate Graph').classes('text-xl font-bold')
            
            search_dropdown = ui.select(
                options=all_names, 
                value=current_focus, 
                on_change=handle_dropdown_change,
                with_input=True
            ).classes('w-64')

        # Chart Container
        with ui.card().classes('w-full h-full grow relative'):
            # Initialize chart with the default person
            chart = ui.echart(get_chart_options(current_focus)).classes('w-full h-full')
            
            # Bind the click event
            chart.on('click', handle_chart_click)


ui.run(port=9999)
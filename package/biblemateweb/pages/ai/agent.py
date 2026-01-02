from nicegui import ui, app

def ai_agent(gui=None, **_):
    # Main container with dark background
    with ui.column().classes('w-full items-center justify-center p-8 gap-6 min-h-screen'):
        
        # 1. Visual Indicator
        ui.icon('smart_toy', size='64px').classes('text-primary mb-4')

        # 2. Main Title
        ui.label('Agent Mode').classes('text-4xl font-bold text-secondary')
        
        # 3. Informative Status Card
        with ui.card().classes('w-full max-w-lg border-l-2 p-6'):
            ui.markdown('**Status:** Currently available in **CLI Version** only.')
            
            ui.label((
                "Agent Mode is a fully autonomous feature designed to plan, orchestrate tools, "
                "and take multiple actions to complete complex Bible-related tasks."
            )).classes(f'mt-4 text-gray-{"300" if app.storage.user["dark_mode"] else "700"} text-lg leading-relaxed')

        # 4. Feature Highlights
        with ui.row().classes('gap-4 mt-4'):
            features = ["Autonomous Planning", "Multi-step Execution", "Tool Orchestration"]
            for feature in features:
                # Darker chip background with light text
                ui.chip(feature, icon='check_circle').props('text-color=white')

        # 5. Call to Action / Link
        ui.label('To use Agent Mode, please install the BibleMate CLI:').classes(f'mt-8 text-gray-{"400" if app.storage.user["dark_mode"] else "600"}')
        
        # Button: White background for high contrast against dark page, or keeping it dark grey with white text
        ui.button('View on GitHub', icon='open_in_new') \
            .props('href=https://github.com/eliranwong/biblemate target=_blank')

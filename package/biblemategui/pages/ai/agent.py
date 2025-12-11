from nicegui import ui, app

def ai_agent(gui=None, **_):
    if app.storage.user["dark_mode"]:
        # Main container with dark background
        with ui.column().classes('w-full items-center justify-center p-8 gap-6 bg-gray-900 min-h-screen'):
            
            # 1. Visual Indicator (Lighter blue for contrast)
            ui.icon('smart_toy', size='64px').classes('text-blue-400 mb-4')

            # 2. Main Title (White text)
            ui.label('Agent Mode').classes('text-4xl font-bold text-white')
            
            # 3. Informative Status Card (Dark card with light blue border)
            with ui.card().classes('w-full max-w-lg bg-gray-800 border-l-4 border-blue-400 p-6'):
                # Text changed to light gray
                ui.markdown('**Status:** Currently available in **CLI Version** only.').classes('text-gray-200')
                
                ui.label((
                    "Agent Mode is a fully autonomous feature designed to plan, orchestrate tools, "
                    "and take multiple actions to complete complex Bible-related tasks."
                )).classes('mt-4 text-gray-300 text-lg leading-relaxed')

            # 4. Feature Highlights
            with ui.row().classes('gap-4 mt-4'):
                features = ["Autonomous Planning", "Multi-step Execution", "Tool Orchestration"]
                for feature in features:
                    # Darker chip background with light text
                    ui.chip(feature, icon='check_circle').props('color=blue-900 text-color=blue-200')

            # 5. Call to Action / Link
            ui.label('To use Agent Mode, please install the BibleMate CLI:').classes('mt-8 text-gray-400')
            
            # Button: White background for high contrast against dark page, or keeping it dark grey with white text
            ui.button('View on GitHub', icon='open_in_new') \
                .props('href=https://github.com/eliranwong/biblemate target=_blank') \
                .classes('bg-blue-600 text-white hover:bg-blue-500')
    else:
        # Main container with light background
        with ui.column().classes('w-full items-center justify-center p-8 gap-6'):
            
            # 1. Visual Indicator (Icon)
            ui.icon('smart_toy', size='64px').classes('text-blue-600 mb-4')

            # 2. Main Title
            ui.label('Agent Mode').classes('text-4xl font-bold text-gray-800')
            
            # 3. Informative Status Card
            with ui.card().classes('w-full max-w-lg bg-blue-50 border-l-4 border-blue-500 p-6'):
                ui.markdown('**Status:** Currently available in **CLI Version** only.')
                
                ui.label((
                    "Agent Mode is a fully autonomous feature designed to plan, orchestrate tools, "
                    "and take multiple actions to complete complex Bible-related tasks."
                )).classes('mt-4 text-gray-700 text-lg leading-relaxed')

            # 4. Feature Highlights (Optional but helpful)
            with ui.row().classes('gap-4 mt-4'):
                features = ["Autonomous Planning", "Multi-step Execution", "Tool Orchestration"]
                for feature in features:
                    ui.chip(feature, icon='check_circle').props('color=blue-100 text-color=blue-800')

            # 5. Call to Action / Link
            ui.label('To use Agent Mode, please install the BibleMate CLI:').classes('mt-8 text-gray-600')
            
            ui.button('View on GitHub', icon='open_in_new') \
                .props('href=https://github.com/eliranwong/biblemate target=_blank') \
                .classes('bg-gray-900 text-white hover:bg-gray-700')

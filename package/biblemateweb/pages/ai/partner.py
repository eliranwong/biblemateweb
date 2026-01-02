from nicegui import ui, app

def ai_partner(gui=None, **_):
    with ui.column().classes('w-full items-center justify-center p-8 gap-6 min-h-screen'):
        
        # 1. Visual Indicator
        ui.icon('handshake', size='64px').classes('text-primary mb-4')

        # 2. Main Title
        ui.label('Partner Mode').classes('text-4xl font-bold text-secondary')
        
        # 3. Informative Status Card
        with ui.card().classes('w-full max-w-lg border-l-2 p-6'):
            ui.markdown('**Status:** Currently available in **CLI Version** only.')
            
            ui.label((
                "Partner Mode transforms BibleMate into an interactive study companion. "
                "Instead of just answering questions, it engages in a two-way dialogue "
                "to help you explore texts, brainstorm ideas, and deepen your understanding."
            )).classes(f'mt-4 text-gray-{"300" if app.storage.user["dark_mode"] else "700"} text-lg leading-relaxed')

        # 4. Feature Highlights
        with ui.row().classes('gap-4 mt-4'):
            features = ["Interactive Dialogue", "Joint Exploration", "Study Companion"]
            for feature in features:
                ui.chip(feature, icon='forum').props('text-color=white')

        # 5. Call to Action / Link
        ui.label('To use Partner Mode, please install the BibleMate CLI:').classes(f'mt-8 text-gray-{"400" if app.storage.user["dark_mode"] else "600"}')
        
        ui.button('View on GitHub', icon='open_in_new') \
            .props('href=https://github.com/eliranwong/biblemate target=_blank')

from nicegui import ui, app

def partner_mode_page():
    if app.storage.user["dark_mode"]:
        # Main container with dark background
        with ui.column().classes('w-full items-center justify-center p-8 gap-6 bg-gray-900 min-h-screen'):
            
            # 1. Visual Indicator (Lighter teal)
            ui.icon('handshake', size='64px').classes('text-teal-400 mb-4')

            # 2. Main Title
            ui.label('Partner Mode').classes('text-4xl font-bold text-white')
            
            # 3. Informative Status Card
            with ui.card().classes('w-full max-w-lg bg-gray-800 border-l-4 border-teal-400 p-6'):
                ui.markdown('**Status:** Currently available in **CLI Version** only.').classes('text-gray-200')
                
                ui.label((
                    "Partner Mode transforms BibleMate into an interactive study companion. "
                    "Instead of just answering questions, it engages in a two-way dialogue "
                    "to help you explore texts, brainstorm ideas, and deepen your understanding."
                )).classes('mt-4 text-gray-300 text-lg leading-relaxed')

            # 4. Feature Highlights
            with ui.row().classes('gap-4 mt-4'):
                features = ["Interactive Dialogue", "Joint Exploration", "Study Companion"]
                for feature in features:
                    # Darker chip background (teal-900) with light text (teal-200)
                    ui.chip(feature, icon='forum').props('color=teal-900 text-color=teal-200')

            # 5. Call to Action / Link
            ui.label('To use Partner Mode, please install the BibleMate CLI:').classes('mt-8 text-gray-400')
            
            ui.button('View on GitHub', icon='open_in_new') \
                .props('href=https://github.com/eliranwong/biblemate target=_blank') \
                .classes('bg-teal-600 text-white hover:bg-teal-500')
    else:
        # Main container with light background
        with ui.column().classes('w-full items-center justify-center p-8 gap-6'):
            
            # 1. Visual Indicator (Icon changed to 'handshake' for partnership)
            ui.icon('handshake', size='64px').classes('text-teal-600 mb-4')

            # 2. Main Title
            ui.label('Partner Mode').classes('text-4xl font-bold text-gray-800')
            
            # 3. Informative Status Card
            with ui.card().classes('w-full max-w-lg bg-teal-50 border-l-4 border-teal-500 p-6'):
                ui.markdown('**Status:** Currently available in **CLI Version** only.')
                
                ui.label((
                    "Partner Mode transforms BibleMate into an interactive study companion. "
                    "Instead of just answering questions, it engages in a two-way dialogue "
                    "to help you explore texts, brainstorm ideas, and deepen your understanding."
                )).classes('mt-4 text-gray-700 text-lg leading-relaxed')

            # 4. Feature Highlights
            with ui.row().classes('gap-4 mt-4'):
                # Features specific to collaboration/partnership
                features = ["Interactive Dialogue", "Joint Exploration", "Study Companion"]
                for feature in features:
                    # Using teal color theme to distinguish from Agent Mode
                    ui.chip(feature, icon='forum').props('color=teal-100 text-color=teal-800')

            # 5. Call to Action / Link
            ui.label('To use Partner Mode, please install the BibleMate CLI:').classes('mt-8 text-gray-600')
            
            # Fixed button with direct href property
            ui.button('View on GitHub', icon='open_in_new') \
                .props('href=https://github.com/eliranwong/biblemate target=_blank') \
                .classes('bg-gray-900 text-white hover:bg-gray-700')

partner_mode_page()
ui.run(port=9999)
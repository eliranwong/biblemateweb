from nicegui import ui
from biblemateweb import get_translation

class SelectionDialog(ui.dialog):
    def __init__(self, big=False):
        super().__init__()
        
        # 1. Update Card Classes:
        # - Added 'flex flex-col': Ensures vertical layout logic works.
        # - Added 'max-h-[90vh]': Ensures the small dialog also respects screen height limits.
        card_classes = (
            'w-11/12 max-w-none h-[90vh] flex flex-col' if big 
            else 'w-full max-w-md max-h-[90vh] flex flex-col'
        )

        with self, ui.card().classes(card_classes):
            # 2. Header: Added 'shrink-0' so it stays fixed size
            self.text_label = ui.label(get_translation("Tool Selection")) \
                .classes('text-xl font-bold text-secondary mb-4 shrink-0')
            
            # 3. Selection Container: 
            # - 'flex-1': Consumes all vertical space between header and footer.
            # - 'overflow-y-auto': Enables scrolling ONLY inside this container.
            self.selection_container = ui.column().classes('w-full flex-1 overflow-y-auto')
            
            # 4. Footer: Added 'shrink-0' so buttons stick to the bottom
            with ui.row().classes('w-full justify-center shrink-0 pt-4'):
                # Button 1: Cancel
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                
                # Button 2: Confirm
                ui.button(get_translation("Confirm"), on_click=lambda: self.submit(self.radio.value))

    def open_with_options(self, options: list, label: str = None):
        """
        Updates the options and opens the dialog.
        Returns an awaitable object.
        """
        if label is not None:
            self.text_label.text = label
            
        self.selection_container.clear()
        
        with self.selection_container:
            # We use a radio button for selection
            val = options[0] if isinstance(options, list) else list(options.keys())[0]
            self.radio = ui.radio(options, value=val).classes('w-full').props('color=primary')
            
        self.open() # Explicitly open the dialog
        return self
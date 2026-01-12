from nicegui import ui
from biblemateweb import get_translation


class SelectionDialog(ui.dialog):
    def __init__(self, big=False):
        super().__init__()
        with self, ui.card().classes('w-11/12 max-w-none h-[90vh] flex column' if big else 'w-full max-w-md'):
            self.text_label = ui.label(get_translation("Tool Selection")).classes('text-xl font-bold text-secondary mb-4')
            
            # This container will hold the radio selection dynamically
            self.selection_container = ui.column().classes('w-full')
            
            with ui.row().classes('w-full justify-end'):
                # Button 1: Cancel
                # Sending None indicates "Canceled"
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                
                # Button 2: Confirm
                # Sending the text value indicates "Confirmed"
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
            self.radio = ui.radio(options, value=options[0] if isinstance(options, list) else list(options.keys())[0]).classes('w-full').props('color=primary')
        return self # This allows us to write: await dialog
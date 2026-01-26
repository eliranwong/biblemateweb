from nicegui import ui, app
from biblemateweb.translations.eng import translation_eng
from biblemateweb.translations.tc import translation_tc
from biblemateweb.translations.sc import translation_sc


def get_translation(text: str):
    if app.storage.user["ui_language"] == "tc":
        return translation_tc.get(text, text)
    elif app.storage.user["ui_language"] == "sc":
        return translation_sc.get(text, text)
    return translation_eng.get(text, text)

class FilenameDialog(ui.dialog):
    def __init__(self):
        super().__init__()

        card_classes = "w-full max-w-md"

        with self, ui.card().classes(card_classes):

            ui.label(get_translation("Download")).classes('text-xl font-bold')
            ui.label(get_translation("Please enter a name for your file:"))

            # Input field for the filename
            self.filename_input = ui.input(label='Filename', placeholder='example.txt') \
                .classes(card_classes).props('autofocus') \
                .on('keydown.enter', lambda: self.submit(self.filename_input.value))  # Allow pressing Enter to submit

            with ui.row().classes('w-full justify-center shrink-0 pt-4'):
                # Button 1: Cancel
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                
                # Button 2: Confirm
                ui.button(get_translation("Confirm"), on_click=lambda: self.submit(self.filename_input.value))

    def open_with_filename(self, filename: str = "BibleMate_AI"):
        """
        Updates the dialog with the provided filename and opens it.
        """
        self.filename_input.value = filename
 
        self.open() # Explicitly open the dialog
        return self
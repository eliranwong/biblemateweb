from nicegui import ui
from biblemateweb import get_translation


class ReviewDialog(ui.dialog):
    def __init__(self):
        super().__init__()
        # 1. flex column: Essential for the card
        with self, ui.card().classes('w-11/12 max-w-none h-[90vh] flex column'):
            
            self.text_label = ui.label(get_translation("Partner Mode Review")).classes('text-h6 font-bold')
            
            # 2. Add the custom CSS class 'biblemate-editor'
            self.editor = ui.textarea(label='Edit Content') \
                .classes('w-full flex-grow biblemate-editor') \
                .props('outlined') 
            
            # The buttons stay at the bottom
            with ui.row().classes('w-full justify-end'):
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                
                ui.button(get_translation("Confirm"), on_click=lambda: self.submit(self.editor.value))

    def open_with_text(self, text_to_review: str, label: str = None):
        self.editor.value = text_to_review
        if label is not None:
            self.text_label.text = label
        return self
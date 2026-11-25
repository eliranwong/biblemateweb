from nicegui import ui
from biblemateweb import get_translation
import traceback, tempfile, pypandoc


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
            with ui.row().classes('w-full justify-center'):
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                ui.button("📥 TXT", on_click=self.download_txt) \
                    .props('flat color=grey')
                ui.button("📥 DOCX", on_click=self.download_docx) \
                    .props('flat color=grey')
                
                ui.button(get_translation("Confirm"), on_click=lambda: self.submit(self.editor.value))

    def open_with_text(self, text_to_review: str, label: str = None):
        self.editor.value = text_to_review
        if label is not None:
            self.text_label.text = label
        return self

    def download_txt(self):
        if content := self.editor.value:
            ui.download(content.encode('utf-8'), 'BibleMate_AI_content.txt')
            ui.notify(get_translation("Downloaded!"), type='positive')
        else:
            ui.notify(get_translation("Nothing to download"), type='negative')

    def download_docx(self):
        if content := self.editor.value:
            try:
                # 1. Create a temporary file that acts as the bridge
                # 'delete=False' is sometimes needed on Windows to close/re-open, 
                # but in a simple flow, we can just read it back.
                with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
                    
                    # 2. Convert Markdown -> DOCX file
                    pypandoc.convert_text(
                        content, 
                        'docx', 
                        format='md', 
                        outputfile=tmp.name
                    )
                    
                    # 3. Read bytes back into memory
                    tmp.seek(0)
                    docx_bytes = tmp.read()

                # 4. Trigger download in NiceGUI (no file left on server)
                ui.download(docx_bytes, filename='BibleMate_AI_content.docx')
                ui.notify(get_translation("Downloaded!"), type='positive')
            except:
                traceback.print_exc()
        else:
            ui.notify(get_translation("Nothing to download"), type='negative')
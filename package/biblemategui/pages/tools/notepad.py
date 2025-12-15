from nicegui import ui, app
import markdown2, re
from biblemategui import get_translation
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

class Notepad:
    def __init__(self, content):
        self.text_content = content
        self.is_editing = True
        self.parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        
    def setup_ui(self):
        # --- Toolbar ---
        with ui.row().classes('gap-2 mb-4 w-full items-center'):
            with ui.column().classes('items-center'):
                self.mode_btn = ui.button('Read Mode', icon='visibility', on_click=self.toggle_mode).props('color=primary')
                with ui.row().classes('gap-2'):                
                    ui.button(on_click=self.download_file, icon='download').props('flat round color=secondary').tooltip(get_translation("Download"))
                    ui.button(on_click=self.clear_text, icon='delete').props('flat round color=negative').tooltip(get_translation("Clear"))
            ui.space()
            self.upload = ui.upload(on_upload=self.handle_upload, auto_upload=True).props('accept=.txt,.md round').classes('w-auto')

        # --- Content Area ---
        # Card must be 'flex flex-col' so the child (textarea) can grow
        with ui.card().classes('w-full h-[60vh] p-0 flex flex-col'):
            
            # 1. Edit Mode: Text Area
            # We apply our custom 'full-height-textarea' class here
            self.textarea = ui.textarea(
                placeholder='Start typing your notes here...',
                value=self.text_content
            ).classes('w-full flex-grow full-height-textarea p-2 border-none focus:outline-none') \
             .props('flat squares resize-none') \
             .bind_visibility_from(self, 'is_editing')

            # 2. Read Mode: HTML Preview
            with ui.scroll_area().classes('w-full flex-grow p-2') \
                    .bind_visibility_from(self, 'is_editing', backward=lambda x: not x):
                self.html_view = ui.html(f'<div class="content-text">{self.text_content}</div>', sanitize=False).classes('w-full prose max-w-none')
        
        ui.label('💡 Tip: Switch to Read Mode to see the formatted result.').classes('text-sm text-gray-600 mt-4')

    def toggle_mode(self):
        self.is_editing = not self.is_editing
        if self.is_editing:
            self.mode_btn.text = 'Read Mode'
            self.mode_btn.props('icon=visibility')
        else:
            self.mode_btn.text = 'Edit Mode'
            self.mode_btn.props('icon=edit')
            self.update_preview()

    def update_preview(self):
        content = self.textarea.value or ''
        try:
            # Added your requested extras
            html_content = markdown2.markdown(
                content, 
                extras=["tables", "fenced-code-blocks", "toc", "cuddled-lists"]
            )
            html_content = self.parser.parseText(html_content)
            html_content = re.sub(r'''(onclick|ondblclick)="(bdbid|lex|cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', html_content)
            html_content = re.sub(r"""(onclick|ondblclick)='(bdbid|lex|cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", html_content)
            self.html_view.content = html_content
        except Exception as e:
            self.html_view.content = f"<p class='text-red-500'>Error: {str(e)}</p>"

    def download_file(self):
        content = self.textarea.value or ''
        if not content:
            ui.notify('Nothing to download!', type='warning')
            return
        ui.download(content.encode('utf-8'), 'biblemate_notes.md')
        ui.notify('Downloaded!', type='positive')
    
    async def handle_upload(self, e):
        try:
            content = await e.file.read()
            self.textarea.value = content.decode('utf-8')
            if not self.is_editing: self.update_preview()
            ui.notify('Loaded!', type='positive')
            self.upload.reset()
        except Exception as ex:
            ui.notify(f'Error: {str(ex)}', type='negative')
    
    def clear_text(self):
        self.textarea.value = ''
        self.html_view.content = ''
        ui.notify('Cleared!', type='info')

def notepad(gui=None, q='', **_):

    def bcv(event):
        nonlocal gui
        b, c, v, *_ = event.args
        gui.change_area_1_bible_chapter(None, b, c, v)

    ui.on('bcv', bcv)

    notepad = Notepad(q)
    notepad.setup_ui()

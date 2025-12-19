from nicegui import ui, app
from biblemategui import get_translation


# --- LOGIC: Bible Selection Dialog ---
class BibleSelectionDialog:
    def __init__(self, parent, book_names, verses):
        with ui.dialog() as self.dialog, ui.card().classes('w-[90vw] max-w-screen-lg h-[90vh] flex flex-col p-4') as self.content_area:
            pass
        self.selection = {'book_id': None, 'chapter': None, 'verse': None}
        self.parent = parent
        self.book_names = book_names
        self.verses = verses
        self.set_current_verse()
    
    def set_current_verse(self):
        bible_tab = self.parent.get_active_area1_tab()
        if bible_tab in app.storage.user:
            args = app.storage.user.get(bible_tab)
            self.current_verse = (args.get("b"), args.get("c"), args.get("v"))
        else:
            self.current_verse = (1, 1, 1)

    def open(self):
        self.set_current_verse()
        self.selection = {'book_id': None, 'chapter': None, 'verse': None}
        self.render_books()
        self.dialog.open()

    def close(self):
        self.dialog.close()

    def render_header(self, title):
        # shrink-0 ensures the header doesn't get compressed by the scroll area
        with ui.row().classes('w-full justify-between items-center mb-2 shrink-0'):
            ui.label(title).classes('text-xl font-bold')
            ui.button(icon='close', on_click=self.close).props('flat round dense')
        ui.separator().classes('mb-2 shrink-0')

    def render_books(self):
        # Clear existing content in the reused card
        self.content_area.clear()
        
        with self.content_area:
            self.render_header(get_translation("Select Book"))
            
            # Use a generic container with native scrolling for better mobile compatibility
            # Use flex-1 and min-h-0 to ensure proper scrolling behavior inside flex container
            with ui.element('div').classes('w-full flex-1 overflow-y-auto min-h-0'):
                # 3-column grid for better space utilization
                with ui.row().classes('w-full gap-2'):
                    for book_id in range(1, 67):
                        name = self.book_names.get(book_id, f"Book {book_id}")
                        if book_id == self.current_verse[0]:
                            ui.button(name, on_click=lambda id=book_id: self.select_book(id)) \
                                .props('outline align=center text-color=secondary').classes('w-20')
                        else:
                            ui.button(name, on_click=lambda id=book_id: self.select_book(id)) \
                                .props('align=center').classes('w-20')                            

    def select_book(self, book_id):
        self.selection['book_id'] = book_id
        self.render_chapters()

    def render_chapters(self):
        self.content_area.clear()
        book_name = self.book_names.get(self.selection['book_id'])
        
        with self.content_area:
            self.render_header(f"{book_name}: {get_translation('Select Chapter')}")
            
            # Use flex-1 and min-h-0 to ensure proper scrolling behavior inside flex container
            with ui.element('div').classes('w-full flex-1 overflow-y-auto min-h-0'):
                # Reduced columns from 10 to 6 for better mobile layout
                with ui.row().classes('w-full gap-2 p-2'):
                    chapters = self.verses.get(self.selection['book_id'], {})
                    for chap_num in chapters.keys():
                        if chap_num == self.current_verse[1]:
                            ui.button(str(chap_num), on_click=lambda c=chap_num: self.select_chapter(c)) \
                                .classes('w-15').props('outline align=center text-color=secondary')
                        else:
                            ui.button(str(chap_num), on_click=lambda c=chap_num: self.select_chapter(c)) \
                                .classes('w-15')

            ui.button(get_translation("Back"), on_click=self.render_books).props('outline color=grey').classes('w-full mt-2 shrink-0')

    def select_chapter(self, chapter):
        self.selection['chapter'] = chapter
        self.render_verses()

    def render_verses(self):
        self.content_area.clear()
        book_name = self.book_names.get(self.selection['book_id'])
        
        with self.content_area:
            self.render_header(f"{book_name} {self.selection['chapter']}: {get_translation('Select Verse')}")
            
            # Get max verses for this chapter
            max_verses = self.verses[self.selection['book_id']][self.selection['chapter']]
            
            # Use flex-1 and min-h-0 to ensure proper scrolling behavior inside flex container
            with ui.element('div').classes('w-full flex-1 overflow-y-auto min-h-0'):
                # Reduced columns from 10 to 6 for better mobile layout
                with ui.row().classes('w-full gap-2 p-2'): 
                    for v in range(1, max_verses + 1):
                        if v == self.current_verse[2]:
                            ui.button(str(v), on_click=lambda verse=v: self.finish_selection(verse)) \
                                .classes('w-15').props('outline align=center text-color=secondary')
                        else:
                            ui.button(str(v), on_click=lambda verse=v: self.finish_selection(verse)) \
                                .classes('w-15')

            ui.button(get_translation("Back"), on_click=self.render_chapters).props('outline color=grey').classes('w-full mt-2 shrink-0')

    def finish_selection(self, verse):
        self.selection['verse'] = verse
        self.close()
        
        # Trigger the final python function
        #book_name = self.book_names.get(self.selection['book_id'])
        #msg = f"Selected: {book_name} {self.selection['chapter']}:{self.selection['verse']}"
        #ui.notify(msg, type='positive', icon='check_circle', close_button=True, position='center')
        self.parent.change_area_1_bible_chapter(book=self.selection['book_id'], chapter=self.selection['chapter'], verse=self.selection['verse'])
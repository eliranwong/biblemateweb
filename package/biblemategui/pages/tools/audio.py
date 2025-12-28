from nicegui import ui, app
import asyncio, os, re
from biblemategui import config, get_translation, getAudioVersionList
from biblemategui.fx.bible import *
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks


class BibleAudioPlayer:
    def __init__(self, text_list: list, audio_list: list, start_verse=1, title="Bible Audio", next_chapter_callback=None):
        self.title = title
        self.text_list = text_list
        self.audio_list = audio_list
        self.current_verse = None
        self.is_playing = False
        self.audio_element = None
        self.verse_buttons = {}
        self.start_verse = start_verse
        self.next_chapter_callback = next_chapter_callback
        
    def create_ui(self):

        with ui.card().classes('w-full max-w-4xl mx-auto mt-8 p-6'):
            # Title
            self.reference = ui.label(self.title).classes('text-3xl font-bold mb-6 text-center')
            
            # Audio player and controls container
            with ui.row().classes('w-full items-center justify-between mb-6 gap-4'):
                # Audio player
                self.audio_element = ui.audio('').classes('flex-grow')
                self.audio_element.on('ended', self.on_audio_ended)
                
                # Loop toggle
                with ui.row().classes('items-center gap-2'):
                    ui.label(get_translation("Loop")).classes('text-sm font-medium')
                    self.loop_toggle = ui.switch().bind_value(app.storage.user, 'loop_audio')
            
            ui.separator().classes('mb-4')
            # Verse list
            with ui.column().classes('w-full gap-2'):
                with ui.list().props('bordered separator').classes('w-full'):
                    for *_, verse_num, verse_text in self.text_list:
                        #verse_text = re.sub('<[^<>]*?>', '', verse_text).strip()
                        # add tooltip
                        if "</heb>" in verse_text:
                            verse_text = re.sub('(<heb id=")(.*?)"', r'\1\2" data-word="\2" class="tooltip-word"', verse_text)
                            verse_text = verse_text.replace("<heb> </heb>", "<heb>&nbsp;</heb>")
                        elif "</grk>" in verse_text:
                            verse_text = re.sub('(<grk id=")(.*?)"', r'\1\2" data-word="\2" class="tooltip-word"', verse_text)
                        with ui.item().classes(f'w-full hover:bg-gray-{500 if app.storage.user["dark_mode"] else 50}'):
                            with ui.item_section().props('avatar'):
                                # Audio control button
                                btn = ui.button(icon='volume_off', 
                                            on_click=lambda v=verse_num: self.toggle_verse(v))
                                btn.classes('flat round color=primary')
                                self.verse_buttons[verse_num] = btn
                            with ui.item_section():
                                verse_text = f"<vid>{verse_num}</vid> {verse_text}"
                                if "</heb>" in verse_text:
                                    verse_text = f"<div style='display: inline-block; direction: rtl;'>{verse_text}</div>"
                                ui.html(verse_text, sanitize=False).classes('text-base')
                                #ui.item_label(
                                #    f"{verse_num}. {verse_text}"
                                #).classes('text-base')

    def toggle_verse(self, verse_num):
        if self.current_verse == verse_num and self.is_playing:
            # Stop current verse
            self.stop_playing()
        else:
            # Play selected verse
            self.play_verse(verse_num)
    
    def play_verse(self, verse_num):
        # Stop current playing verse
        if self.current_verse is not None:
            self.verse_buttons[self.current_verse].props('icon=volume_off')
        
        # Update state
        self.current_verse = verse_num
        self.is_playing = True
        self.reference.text = f"{self.title}:{verse_num}"
        
        # Update UI
        self.verse_buttons[verse_num].props('icon=volume_up')
        
        # Load and play audio
        audio_file = self.audio_list[verse_num - 1]
        self.audio_element.set_source(audio_file)
        self.audio_element.run_method('play')
    
    def stop_playing(self):
        if self.audio_element:
            self.audio_element.run_method('pause')
        
        if self.current_verse is not None:
            self.verse_buttons[self.current_verse].props('icon=volume_off')
        
        self.is_playing = False
        self.current_verse = None
    
    def on_audio_ended(self):
        # Current verse finished
        if self.current_verse is not None:
            self.verse_buttons[self.current_verse].props('icon=volume_off')
        
        # Determine next verse
        if self.current_verse is not None:
            next_verse = self.current_verse + 1
            
            # Check if we've reached the end
            if next_verse > len(self.text_list):
                if app.storage.user.get("loop_audio"):
                    # Loop back to verse 1
                    self.play_verse(1)
                else:
                    # Stop playing
                    self.is_playing = False
                    self.current_verse = None
                    if self.next_chapter_callback is not None:
                        self.next_chapter_callback()
            else:
                # Play next verse
                self.play_verse(next_verse)
    
    async def auto_start(self):
        # Wait a bit for the page to fully load
        await asyncio.sleep(0.5)
        # Start playing from the specified verse
        self.play_verse(self.start_verse)

def bibles_audio(gui=None, bt=None, b=1, c=1, v=1, area=2, **_):
    if not bt:
        bt = gui.get_area_1_bible_text()

    def next_chapter(selection):
        nonlocal gui
        selected_text, selected_b, selected_c, _ = selection
        db = getBiblePath(selected_text)
        bookList = getBibleBookList(db)
        chapterList = getBibleChapterList(db, selected_b)
        if len(chapterList) == 1 or selected_c == chapterList[-1]:
            if selected_b == bookList[-1]:
                new_b = bookList[0]
                new_c = getBibleChapterList(db, new_b)[0]
            else:
                new_b = selected_b + 1
                for i in bookList:
                    previous_book = None
                    if previous_book is not None:
                        new_b = i
                        break
                    elif i == selected_b:
                        previous_book = i
                new_c = getBibleChapterList(db, new_b)[0]
        else:
            new_b = selected_b
            new_c = selected_c + 1
            for i in chapterList:
                previous_chapter = None
                if previous_chapter is not None:
                    new_c = i
                    break
                elif i == selected_c:
                    previous_chapter = i
        app.storage.user["tool_book_text"], app.storage.user["tool_book_number"], app.storage.user["tool_chapter_number"], app.storage.user["tool_verse_number"] = selected_text, new_b, new_c, 1
        gui.load_area_2_content(title="Audio", sync=False)

    # version options
    version_options = getAudioVersionList(app.storage.client["custom"])
    # version
    if bt in ("ORB", "OIB", "OPB", "ODB", "OLB") and b < 40 and "BHS5" in config.audio:
        version = "OHGB"
    elif bt in ("ORB", "OIB", "OPB", "ODB", "OLB") and "OGNT" in config.audio:
        version = "OHGB"
    elif app.storage.client["custom"] and bt in config.audio_custom:
        version = bt
    elif bt in config.audio:
        version = bt
    else:
        version = "NET"
    # Bible Selection menu
    bible_selector = BibleSelector(version_options=sorted(version_options))
    def additional_items():
        nonlocal gui, bible_selector, area
        def change_audio_chapter(selection):
            if area == 1:
                app.storage.user['tool_book_text'], app.storage.user['bible_book_number'], app.storage.user['bible_chapter_number'], app.storage.user['bible_verse_number'] = selection
                gui.load_area_1_content(title="Audio")
            else:
                app.storage.user['tool_book_text'], app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = selection
                gui.load_area_2_content(title="Audio", sync=False)
        ui.button(get_translation('Go'), on_click=lambda: change_audio_chapter(bible_selector.get_selection()))
    bible_selector.create_ui(version, b, c, v, additional_items=additional_items)
    # Text file list
    text_list = getBibleChapterVerses(getBiblePath(version), b, c)
    # Audio file list
    bible_audio_dir = config.audio_custom[version] if version in config.audio_custom else config.audio[version]
    audio_list = [os.path.join(bible_audio_dir, f"{b}_{c}", f"{version}_{b}_{c}_{verse[2]}.mp3") for verse in text_list]
    # Start the player
    player = BibleAudioPlayer(text_list=text_list, audio_list=audio_list, start_verse=v, title=BibleBooks.abbrev[app.storage.user["ui_language"]][str(b)][-1]+f" {c}", next_chapter_callback=lambda: next_chapter((bt, b, c, v)))
    player.create_ui()
    # Auto-start playing after page loads
    ui.timer(0.5, player.auto_start, once=True)

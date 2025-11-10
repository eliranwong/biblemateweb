from nicegui import ui
import asyncio, os
from biblemateweb import BIBLEMATEWEB_DATA

# Bible chapter data
bible_chapter = [
    [1, "A psalm of David. [1] The LORD is my shepherd; I have what I need."],
    [2, "He lets me lie down in green pastures; he leads me beside quiet waters."],
    [3, "He renews my life; he leads me along the right paths for his name’s sake."],
    [4, "Even when I go through the darkest valley, I fear no danger, for you are with me; your rod and your staff — they comfort me."],
    [5, "You prepare a table before me in the presence of my enemies; you anoint my head with oil; my cup overflows."],
    [6, "Only goodness and faithful love will pursue me all the days of my life, and I will dwell in the house of the LORD as long as I live."],
]

bb = "CSB"
b = 19
c = 23

bible_audio_dir = os.path.join(BIBLEMATEWEB_DATA, "audio", "bibles", bb, "default")
bible_audio = [os.path.join(bible_audio_dir, "19_23", f"{bb}_{b}_{c}_{verse[0]}.mp3") for verse in bible_chapter]

class BibleAudioPlayer:
    def __init__(self):
        self.current_verse = None
        self.is_playing = False
        self.loop_enabled = True
        self.audio_element = None
        self.verse_buttons = {}
        self.start_verse = 2  # Start with verse 2 when page loads
        
    def create_ui(self):
        with ui.card().classes('w-full max-w-4xl mx-auto mt-8 p-6'):
            # Title
            ui.label('Psalm 23').classes('text-3xl font-bold mb-6 text-center')
            
            # Audio player and controls container
            with ui.row().classes('w-full items-center justify-between mb-6 gap-4'):
                # Audio player
                self.audio_element = ui.audio('').classes('flex-grow')
                self.audio_element.on('ended', self.on_audio_ended)
                
                # Loop toggle
                with ui.row().classes('items-center gap-2'):
                    ui.label('Loop:').classes('text-sm font-medium')
                    self.loop_toggle = ui.switch(value=True).on('update:model-value', 
                        self.set_loop)
            
            ui.separator().classes('mb-4')
            
            # Verse list
            with ui.column().classes('w-full gap-2'):
                with ui.list().props('bordered separator').classes('w-full'):
                    for verse_num, verse_text in bible_chapter:
                        with ui.item().classes('w-full hover:bg-gray-50'):
                            with ui.item_section().props('avatar'):
                                # Audio control button
                                btn = ui.button(icon='volume_off', 
                                            on_click=lambda v=verse_num: self.toggle_verse(v))
                                btn.classes('flat round color=primary')
                                self.verse_buttons[verse_num] = btn
                            
                            with ui.item_section():
                                ui.item_label(
                                    f"{verse_num}. {verse_text}"
                                ).classes('text-base')
    
    def set_loop(self):
        self.loop_enabled = not self.loop_enabled

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
        
        # Update UI
        self.verse_buttons[verse_num].props('icon=volume_up')
        
        # Load and play audio
        audio_file = bible_audio[verse_num - 1]
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
            if next_verse > len(bible_chapter):
                if self.loop_enabled:
                    # Loop back to verse 1
                    self.play_verse(1)
                else:
                    # Stop playing
                    self.is_playing = False
                    self.current_verse = None
            else:
                # Play next verse
                self.play_verse(next_verse)
    
    async def auto_start(self):
        # Wait a bit for the page to fully load
        await asyncio.sleep(0.5)
        # Start playing from the specified verse
        self.play_verse(self.start_verse)

# Create the application
player = BibleAudioPlayer()

def bibles_audio(**_):
    player.create_ui()
    # Auto-start playing after page loads
    ui.timer(0.5, player.auto_start, once=True)

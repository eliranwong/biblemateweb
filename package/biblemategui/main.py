#!/usr/bin/env python3
from nicegui import ui

from biblemategui import config, BIBLEMATEGUI_APP_DIR, BIBLEMATEGUI_DATA, BIBLEMATEGUI_DATA_CUSTOM

from biblemategui.pages.home import *

from biblemategui.pages.bibles.original_reader import original_reader
from biblemategui.pages.bibles.original_interlinear import original_interlinear
from biblemategui.pages.bibles.original_parallel import original_parallel
from biblemategui.pages.bibles.original_discourse import original_discourse
from biblemategui.pages.bibles.original_linguistic import original_linguistic

from biblemategui.pages.tools.audio import bibles_audio

import os, glob

"""
# Supported parameters

t - token
m - menu

bbt - bible bible text
bb - bible book
bc - bible chapter
bv - bible verse

tbt - tool bible text
tb - tool book
tc - tool chapter
tv - tool verse

db - default bible
dc - default commentary
de - default encyclopedia
dl - default lexicon
"""

# Home Page

@ui.page('/')
def page_home(
    #t: str | None = None, # token for using custom data
    m: bool | None = True,
    bbt: str | None = None,
    bb: int | None = None,
    bc: int | None = None,
    bv: int | None = None,
    tbt: str | None = None,
    tb: int | None = None,
    tc: int | None = None,
    tv: int | None = None,
):
    """
    Home page that accepts optional parameters.
    Example: /?bb=1&bc=1&bv=1
    """

    # general settings; stored on sever side
    config.bibles = {os.path.basename(i)[:-6]: i for i in glob.glob(os.path.join(BIBLEMATEGUI_DATA, "bibles", "*.bible"))}
    config.bibles_custom = {os.path.basename(i)[:-6]: i for i in glob.glob(os.path.join(BIBLEMATEGUI_DATA_CUSTOM, "bibles", "*.bible"))}

    # default user settings; stored in users' web browser Local Storage
    # Use app.storage.user to store session-specific state
    # This keeps the settings unique for each user
    app.storage.user.setdefault('left_drawer_open', False)
    
    app.storage.user.setdefault('bible_book_text', "NET")
    if bbt is not None:
        app.storage.user['bible_book_text'] = bbt
    app.storage.user.setdefault('bible_book_number', 1)
    if bb is not None:
        app.storage.user['bible_book_number'] = bb
    app.storage.user.setdefault('bible_chapter_number', 1)
    if bc is not None:
        app.storage.user['bible_chapter_number'] = bc
    app.storage.user.setdefault('bible_verse_number', 1)
    if bv is not None:
        app.storage.user['bible_verse_number'] = bv
    app.storage.user.setdefault('tool_book_text', "KJV")
    if tbt is not None:
        app.storage.user['tool_book_text'] = tbt
    app.storage.user.setdefault('tool_book_number', 1)
    if tb is not None:
        app.storage.user['tool_book_number'] = tb
    app.storage.user.setdefault('tool_chapter_number', 1)
    if tc is not None:
        app.storage.user['tool_chapter_number'] = tc
    app.storage.user.setdefault('tool_verse_number', 1)
    if tv is not None:
        app.storage.user['tool_verse_number'] = tv
        
    # navigation menu
    if m:
        create_menu() # Add the shared menu
    # main content
    create_home_layout()

# Settings

@ui.page('/settings')
def page_Settings(q: str | None = None, m: bool = True):
    if m:
        create_menu()
    with ui.column().classes('w-full items-center'):
        ui.label('BibleMate AI').classes('text-2xl mt-4')
        ui.notify("This feature is currently in progress.")

# Entry_point

def main():
    # --- Run the App ---
    # Make sure to replace the secret!
    ui.run(
        storage_secret='REPLACE_ME_WITH_A_REAL_SECRET', # TODO
        port=8888,
        title='BibleMate AI',
        favicon=os.path.join(BIBLEMATEGUI_APP_DIR, 'eliranwong.jpg')
    )

main()
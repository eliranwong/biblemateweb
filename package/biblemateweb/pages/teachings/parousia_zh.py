from nicegui import ui
#from nicegui import app
from functools import partial
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

def parousia_zh(gui=None, **_):
    parser = BibleVerseParser(False)
    def open_verse_reference(reference: str):
        """Updates the output label with information about the clicked reference."""
        nonlocal gui, parser
        #app.storage.user['tool_query'] = reference
        #gui.select_empty_area2_tab()
        #gui.load_area_2_content(title='Verses')
        if refs := parser.extractAllReferences(reference):
            b, c, v, *_ = refs[0]
            gui.change_area_1_bible_chapter(book=b, chapter=c, verse=v)
        else:
            ui.notify("No verse reference found!")

    def render_verse_chips(verses):
        """Helper to render a list of verses as dense chips."""
        with ui.row().classes('gap-1 flex-wrap'):
            for verse in verses:
                # clickable=True makes them interactive if you add on_click later
                ui.chip(
                    verse,
                    icon='book',
                    on_click=partial(open_verse_reference, verse),
                ).props('dense outline square text-color=white icon=menu_book').classes('bg-white text-xs')

    # Page Container
    with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-6'):
        
        # --- Header ---
        with ui.column().classes('w-full items-center text-center mb-6'):
            ui.label('圍繞降臨 (Parousia) 的事件順序').classes('text-3xl font-bold text-primary')
            ui.label('觀點：前千禧年派 (Premillennialism) & 災後被提 (Post-tribulation)').classes('text-lg font-medium')
            ui.label('主要經文架構：哥林多前書 15:23-27, 保羅書信, 啟示錄 20 章').classes('text-gray-500')

        # --- Expansion 1: The Return of Jesus ---
        with ui.expansion('耶穌的再來，降臨 (The Return of Jesus, the Parousia)', icon='auto_awesome') \
                .classes('w-full bg-blue-50 rounded-lg border border-blue-200'):
            with ui.column().classes('p-4 w-full'):
                
                ui.label('● 耶穌的禱告').classes('font-bold text-blue-900')
                render_verse_chips(['太 6:10', '路 11:2'])
                
                ui.separator().classes('mb-2')
                
                ui.label('● 新創造').classes('font-bold text-blue-900')
                render_verse_chips(['賽 65:17', '賽 66:22'])
                
                ui.separator().classes('mb-2')

                ui.label('● 再來').classes('font-bold text-blue-900')
                render_verse_chips([
                    '約 14:3', '林前 15:23', '帖前 2:19', '帖前 3:13', 
                    '帖前 4:15', '帖前 5:23', '帖後 2:1', '帖後 2:8', 
                    '雅 5:7', '彼後 1:16', '彼後 3:4', '彼後 3:12', '約一 2:28'
                ])

        # --- Expansion 2: Witnesses surrounding the Parousia ---
        with ui.expansion('圍繞降臨 (Parousia) 事件的見證', icon='verified') \
                .classes('w-full bg-purple-50 rounded-lg border border-purple-200'):
            with ui.column().classes('p-4 w-full'):
                
                ui.label('● 一千年').classes('font-bold text-purple-900')
                render_verse_chips(['啟 20:6'])

                ui.separator().classes('mb-2')

                ui.label('● 舊約中神在地上的統治').classes('font-bold text-purple-900')
                render_verse_chips([
                    '詩 72:8-14', '賽 2:2-4', '但 2:28-45', 
                    '彌 4:1-3', '亞 14:5-17', '賽 11:1-10'
                ])

                ui.separator().classes('mb-2')

                ui.label('● 與人類共同掌權').classes('font-bold text-purple-900')
                render_verse_chips(['創 1:26-28', '詩 8:4-6', '來 2:6-10'])

                ui.separator().classes('mb-2')

                ui.label('● 舊約中作為列國之光的祭司國度').classes('font-bold text-purple-900')
                render_verse_chips(['出 19:6', '賽 42:6', '賽 49:6'])

                ui.separator().classes('mb-2')

                ui.label('● 君尊的祭司').classes('font-bold text-purple-900')
                render_verse_chips([
                    '彼前 2:9', '啟 1:6', '啟 5:10', '出 19:5-6', 
                    '創 1:26-28', '太 19:28', '路 22:30', 
                    '提後 2:12', '啟 20', '啟 5:10', '啟 20:4', '啟 22:5'
                ])

                ui.separator().classes('mb-2')

                ui.label('● 亞當被造是為了統治').classes('font-bold text-purple-900')
                render_verse_chips(['西 1:16', '詩 2', '詩 110'])

                ui.separator().classes('mb-2')

                ui.label('● 移交給聖徒').classes('font-bold text-purple-900')
                render_verse_chips(['但 7:27'])

        # --- Timeline ---
        with ui.timeline(side='right').classes('w-full'):

            # =================================================
            # STAGE 1: Jesus' Resurrection
            # =================================================
            with ui.timeline_entry(
                title='第一階段：耶穌的復活',
                subtitle='初熟的果子',
                icon='church',
                color='green-6'
            ):
                with ui.card().classes('bg-green-50 w-full mt-2 border-l-4 border-green-500'):
                    ui.markdown('**(1) 耶穌的復活**')
                    # Implied from the header context "1 Cor 15:23"
                    render_verse_chips(['林前 15:23'])

            # =================================================
            # CONTEXT: Post-tribulation (Before Parousia)
            # =================================================
            with ui.timeline_entry(
                title='前奏：災後 (Post-tribulation)',
                subtitle='大災難在降臨之前',
                icon='warning',
                color='red-6'
            ):
                with ui.card().classes('bg-red-50 w-full mt-2 border-l-4 border-red-500'):
                    ui.label('大災難 (The Great Tribulation)').classes('font-bold text-red-900')
                    render_verse_chips([
                        '約 16:33', '帖前 5:2-12', '帖後 2:9-10', 
                        '啟 13:10', '啟 14:12', '馬可 13:19-25', 
                        '太 24:21-29', '西 1:24', '啟 1:9'
                    ])
                    
                    ui.separator().classes('my-3 bg-red-200')
                    
                    ui.label('第二次再來之前 (Pre-Second Coming Events)').classes('font-bold text-red-900')
                    render_verse_chips([
                        '帖後 2:1-12', '帖後 2:3', '帖前 4:17', 
                        '約一 4:3', '約二 1:7', '啟 13:1 - 啟 17:18', 
                        '啟 7:1-8, 9, 14'
                    ])

            # =================================================
            # STAGE 2: The Parousia
            # =================================================
            with ui.timeline_entry(
                title='第二階段：降臨 (Parousia)',
                subtitle='信徒復活與彌賽亞統治',
                icon='flight_land',
                color='blue-7'
            ):
                with ui.card().classes('bg-blue-50 w-full mt-2 border-l-4 border-blue-500'):
                    ui.markdown('**i. 突然的降臨**')
                    render_verse_chips(['腓 3:20', '帖前 5:1-4'])

                    ui.separator().classes('my-3 bg-blue-200')

                    ui.markdown('**ii. 已死的信徒復活**')
                    render_verse_chips([
                        '林前 15:51-52', '腓 3:21', '帖前 4:13-17', 
                        '帖前 5:1-4', '啟 20:4-6'
                    ])

                    ui.separator().classes('my-3 bg-blue-200')

                    ui.markdown('**iii. 彌賽亞的過渡統治期 (Messianic Interregnum)**')
                    ui.label('末了權勢的爭戰').classes('text-sm text-gray-700 mb-1')
                    render_verse_chips([
                        '羅 16:20', '林前 15:22-24', '林前 6:3', '啟 20:4'
                    ])

            # =================================================
            # STAGE 3: The End
            # =================================================
            with ui.timeline_entry(
                title='第三階段：末期',
                subtitle='最終的結局',
                icon='public',
                color='purple-6'
            ):
                with ui.card().classes('bg-purple-50 w-full mt-2 border-l-4 border-purple-500'):
                    ui.markdown('**i. 所有人的普遍復活**')
                    render_verse_chips([
                        '約 5:29', '啟 20:4-6', '啟 20:13'
                    ])

                    ui.separator().classes('my-3 bg-purple-200')

                    ui.markdown('**ii. 最後的審判**')
                    render_verse_chips([
                        '羅 14:10', '林後 5:10'
                    ])

                    ui.separator().classes('my-3 bg-purple-200')

                    ui.markdown('**iii. 萬物/被造界的轉變與更新**')
                    render_verse_chips(['羅 8:19-20'])
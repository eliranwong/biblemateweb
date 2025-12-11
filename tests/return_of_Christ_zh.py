from nicegui import ui

def render_verse_chips(verses):
    """Helper to render a list of verses as dense chips."""
    with ui.row().classes('gap-1 flex-wrap'):
        for verse in verses:
            # clickable=True makes them interactive if you add on_click later
            ui.chip(verse).props('dense outline square icon=menu_book') \
                .classes('bg-white text-xs')

def create_parousia_page():
    # Page Container
    with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-6'):
        
        # --- Header ---
        with ui.column().classes('w-full items-center text-center mb-6'):
            ui.label('圍繞降臨 (Parousia) 的事件順序').classes('text-3xl font-bold text-primary')
            ui.label('觀點：前千禧年派 (Premillennialism) & 災後被提 (Post-tribulation)').classes('text-lg font-medium')
            ui.label('主要經文架構：哥林多前書 15:23-27, 保羅書信, 啟示錄 20 章').classes('text-gray-500')

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
                title='背景：災後 (Post-tribulation)',
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
                        '帖後 2:1', '帖後 2:3', '約一 4:3', 
                        '約二 1:7', '啟 13-17', '啟 6-17', 
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
                    ui.markdown('**i. 突然的降臨 (Sudden Arrival)**')
                    render_verse_chips(['腓 3:20', '帖前 5:1-4'])

                    ui.separator().classes('my-3 bg-blue-200')

                    ui.markdown('**ii. 已死和活著的信徒復活**')
                    render_verse_chips([
                        '林前 15:51-52', '腓 3:21', '帖前 4:13-17', 
                        '帖前 5:1-4', '啟 20:4-6'
                    ])

                    ui.separator().classes('my-3 bg-blue-200')

                    ui.markdown('**iii. 彌賽亞的過渡統治期 (Messianic Interregnum)**')
                    ui.label('末了與天使（靈界）權勢的爭戰').classes('text-sm text-gray-700 mb-1')
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

# --- Run the App ---
@ui.page('/')
def main_page():
    #ui.colors(primary='#2B4C7E')
    create_parousia_page()

ui.run(title='Biblemate Parousia Sequence')
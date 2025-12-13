from nicegui import ui
#from nicegui import app
from functools import partial
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

def parousia(gui=None, **_):
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
        with ui.column().classes('w-full items-center text-center mb-2'):
            ui.label('Sequence of Events Surrounding the Parousia').classes('text-3xl font-bold text-primary')
            ui.label('Viewpoint: Premillennialism & Post-tribulation').classes('text-lg font-medium text-gray-600')
            ui.label('Key Scriptural Framework: 1 Cor 15:23-27, Pauline Epistles, Rev 20').classes('text-gray-500')

        # =================================================
        # NEW SECTION: INTRODUCTORY EXPANSIONS
        # =================================================
        
        # --- Expansion 1: The Return of Jesus ---
        with ui.expansion('The Return of Jesus (The Parousia)', icon='auto_awesome') \
                .classes('w-full bg-blue-50 rounded-lg border border-blue-200'):
            with ui.column().classes('p-4 w-full'):
                
                ui.label('● Jesus\' Prayer').classes('font-bold text-blue-900')
                render_verse_chips(['Matt 6:10', 'Luke 11:2'])
                
                ui.separator().classes('mb-2')
                
                ui.label('● New Creation').classes('font-bold text-blue-900')
                render_verse_chips(['Isa 65:17', 'Isa 66:22'])
                
                ui.separator().classes('mb-2')

                ui.label('● The Return').classes('font-bold text-blue-900')
                render_verse_chips([
                    'John 14:3', '1 Cor 15:23', '1 Thess 2:19', '1 Thess 3:13', 
                    '1 Thess 4:15', '1 Thess 5:23', '2 Thess 2:1', '2 Thess 2:8', 
                    'Jas 5:7', '2 Pet 1:16', '2 Pet 3:4', '2 Pet 3:12', '1 John 2:28'
                ])

        # --- Expansion 2: Witnesses surrounding the Parousia ---
        with ui.expansion('Witnesses Surrounding the Parousia Event', icon='verified') \
                .classes('w-full bg-purple-50 rounded-lg border border-purple-200'):
            with ui.column().classes('p-4 w-full'):
                
                ui.label('● One Thousand Years').classes('font-bold text-purple-900')
                render_verse_chips(['Rev 20:6'])

                ui.separator().classes('mb-2')

                ui.label('● God\'s Earthly Reign in the OT').classes('font-bold text-purple-900')
                render_verse_chips([
                    'Ps 72:8-14', 'Isa 2:2-4', 'Dan 2:28-45', 
                    'Mic 4:1-3', 'Zech 14:5-17', 'Isa 11:1-10'
                ])

                ui.separator().classes('mb-2')

                ui.label('● Co-reigning with Humanity').classes('font-bold text-purple-900')
                render_verse_chips(['Gen 1:26-28', 'Ps 8:4-6', 'Heb 2:6-10'])

                ui.separator().classes('mb-2')

                ui.label('● Priestly Kingdom as Light to Nations (OT)').classes('font-bold text-purple-900')
                render_verse_chips(['Exod 19:6', 'Isa 42:6', 'Isa 49:6'])

                ui.separator().classes('mb-2')

                ui.label('● Royal Priesthood').classes('font-bold text-purple-900')
                render_verse_chips([
                    '1 Pet 2:9', 'Rev 1:6', 'Rev 5:10', 'Exod 19:5-6', 
                    'Gen 1:26-28', 'Matt 19:28', 'Luke 22:30', 
                    '2 Tim 2:12', 'Rev 20', 'Rev 5:10', 'Rev 20:4', 'Rev 22:5'
                ])

                ui.separator().classes('mb-2')

                ui.label('● Adam Created to Rule').classes('font-bold text-purple-900')
                render_verse_chips(['Col 1:16', 'Ps 2', 'Ps 110'])

                ui.separator().classes('mb-2')

                ui.label('● Handed Over to the Saints').classes('font-bold text-purple-900')
                render_verse_chips(['Dan 7:27'])

        # =================================================
        # EXISTING TIMELINE SECTION
        # =================================================
        with ui.timeline(side='right').classes('w-full'):

            # --- STAGE 1 ---
            with ui.timeline_entry(
                title='Stage 1: Resurrection of Jesus',
                subtitle='The Firstfruits',
                icon='church',
                color='green-6'
            ):
                with ui.card().classes('bg-green-50 w-full mt-2 border-l-4 border-green-500'):
                    ui.markdown('**(1) The Resurrection of Jesus**')
                    render_verse_chips(['1 Cor 15:23'])

            # --- CONTEXT: Post-tribulation ---
            with ui.timeline_entry(
                title='Prelude: Post-tribulation',
                subtitle='Tribulation before the Parousia',
                icon='warning',
                color='red-6'
            ):
                with ui.card().classes('bg-red-50 w-full mt-2 border-l-4 border-red-500'):
                    ui.label('The Great Tribulation').classes('font-bold text-red-900')
                    render_verse_chips([
                        'John 16:33', '1 Thess 5:2-12', '2 Thess 2:9-10', 
                        'Rev 13:10', 'Rev 14:12', 'Mark 13:19-25', 
                        'Matt 24:21-29', 'Col 1:24', 'Rev 1:9'
                    ])
                    
                    ui.separator().classes('mb-2 bg-red-200')
                    
                    ui.label('Before the Second Coming').classes('font-bold text-red-900')
                    render_verse_chips([
                        '2 Thess 2:1-12', '2 Thess 2:3', '1 Thess 4:17', 
                        '1 John 4:3', '2 John 1:7', 'Rev 13:1 - Rev 17:18',
                        'Rev 7:1-8, 9, 14'
                    ])

            # --- STAGE 2 ---
            with ui.timeline_entry(
                title='Stage 2: The Parousia',
                subtitle='Resurrection & Messianic Reign',
                icon='flight_land',
                color='blue-7'
            ):
                with ui.card().classes('bg-blue-50 w-full mt-2 border-l-4 border-blue-500'):
                    ui.markdown('**i. The Sudden Arrival (Parousia)**')
                    render_verse_chips(['Phil 3:20', '1 Thess 5:1-4'])

                    ui.separator().classes('mb-2 bg-blue-200')

                    ui.markdown('**ii. Resurrection of Dead**')
                    render_verse_chips([
                        '1 Cor 15:51-52', 'Phil 3:21', '1 Thess 4:13-17', 
                        '1 Thess 5:1-4', 'Rev 20:4-6'
                    ])

                    ui.separator().classes('mb-2 bg-blue-200')

                    ui.markdown('**iii. Messianic Interregnum (Millennium)**')
                    ui.label('War against angelic/spiritual powers at the end').classes('text-sm text-gray-700 mb-1')
                    render_verse_chips([
                        'Rom 16:20', '1 Cor 15:22-24', '1 Cor 6:3', 'Rev 20:4'
                    ])

            # --- STAGE 3 ---
            with ui.timeline_entry(
                title='Stage 3: The End',
                subtitle='The Final Conclusion',
                icon='public',
                color='purple-6'
            ):
                with ui.card().classes('bg-purple-50 w-full mt-2 border-l-4 border-purple-500'):
                    ui.markdown('**i. General Resurrection of All**')
                    render_verse_chips([
                        'John 5:29', 'Rev 20:4-6', 'Rev 20:13'
                    ])

                    ui.separator().classes('mb-2 bg-purple-200')

                    ui.markdown('**ii. Final Judgment**')
                    render_verse_chips([
                        'Rom 14:10', '2 Cor 5:10'
                    ])

                    ui.separator().classes('mb-2 bg-purple-200')

                    ui.markdown('**iii. Transformation & Renewal of Creation**')
                    render_verse_chips(['Rom 8:19-20'])
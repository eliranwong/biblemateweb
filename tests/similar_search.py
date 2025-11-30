from nicegui import ui
import difflib

# --- Mock Database of Bible Promises ---
# In your real app, this would query your database or AI backend.
BIBLE_PROMISES = {
    "Peace": [
        {"ref": "John 14:27", "text": "Peace I leave with you; my peace I give you. I do not give to you as the world gives. Do not let your hearts be troubled and do not be afraid."},
        {"ref": "Philippians 4:7", "text": "And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus."}
    ],
    "Anxiety": [
        {"ref": "1 Peter 5:7", "text": "Cast all your anxiety on him because he cares for you."},
        {"ref": "Psalm 94:19", "text": "When anxiety was great within me, your consolation brought me joy."}
    ],
    "Hope": [
        {"ref": "Jeremiah 29:11", "text": "For I know the plans I have for you, declares the LORD, plans to prosper you and not to harm you, plans to give you hope and a future."},
        {"ref": "Romans 15:13", "text": "May the God of hope fill you with all joy and peace as you trust in him, so that you may overflow with hope by the power of the Holy Spirit."}
    ],
    "Healing": [
        {"ref": "Psalm 147:3", "text": "He heals the brokenhearted and binds up their wounds."},
        {"ref": "Jeremiah 17:14", "text": "Heal me, LORD, and I will be healed; save me and I will be saved, for you are the one I praise."}
    ],
    "Love": [
        {"ref": "1 Corinthians 13:4-7", "text": "Love is patient, love is kind... It always protects, always trusts, always hopes, always perseveres."},
        {"ref": "1 John 4:19", "text": "We love because he first loved us."}
    ],
    "Forgiveness": [
        {"ref": "1 John 1:9", "text": "If we confess our sins, he is faithful and just and will forgive us our sins and purify us from all unrighteousness."},
        {"ref": "Ephesians 4:32", "text": "Be kind and compassionate to one another, forgiving each other, just as in Christ God forgave you."}
    ]
}

# --- UI Styling Constants ---
PRIMARY_COLOR = '#5898d4' # Soft Sky Blue
BG_COLOR = '#f8fafc'      # Very light grey/blue background
CARD_BG = 'white'

def search_page():
    # Container for the results
    results_container = ui.column().classes('w-full max-w-3xl mx-auto mt-8 gap-4')

    def display_verses(topic):
        """Renders the verses for a specific topic into the results container."""
        results_container.clear()
        
        # Title of the topic
        with results_container:
            ui.label(f"Promises for: {topic}").classes('text-2xl font-serif text-slate-700 mb-2')
            
            verses = BIBLE_PROMISES.get(topic, [])
            for v in verses:
                with ui.card().classes('w-full p-6 shadow-sm hover:shadow-md transition-shadow border-l-4').style(f'border-left-color: {PRIMARY_COLOR}'):
                    ui.label(v['text']).classes('text-lg text-slate-800 italic font-serif mb-3 leading-relaxed')
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(v['ref']).classes('font-bold text-slate-500 text-sm uppercase tracking-wide')
                        ui.button(icon='content_copy', on_click=lambda text=v['text']: ui.notify('Verse copied!', type='positive')) \
                            .props('flat round size=sm color=grey')

    def handle_fuzzy_selection(selection):
        """Callback when user selects a topic from the fuzzy match dialog."""
        if selection:
            dialog.close()
            search_input.value = selection # Update input to match selection
            display_verses(selection)

    # --- Fuzzy Match Dialog ---
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md'):
        ui.label("Did you mean...").classes('text-xl font-bold text-slate-700 mb-4')
        ui.label("We couldn't find an exact match. Please select one of these topics:").classes('text-slate-500 mb-4')
        
        # This container will hold the radio selection dynamically
        selection_container = ui.column().classes('w-full')
        
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat color=grey')

    def perform_search():
        query = search_input.value.strip()
        if not query:
            ui.notify('Please enter a topic', type='warning')
            return

        # 1. Exact Match Check (Case Insensitive)
        # We create a mapping of lowercase keys to original keys
        keys_map = {k.lower(): k for k in BIBLE_PROMISES.keys()}
        
        if query.lower() in keys_map:
            # Exact match found!
            original_key = keys_map[query.lower()]
            display_verses(original_key)
        else:
            # 2. Fuzzy Match Logic
            # Get top 5 matches using difflib
            matches = difflib.get_close_matches(query, BIBLE_PROMISES.keys(), n=5, cutoff=0.4)
            
            if matches:
                # Populate the dialog with options
                selection_container.clear()
                with selection_container:
                    # We use a radio button for selection
                    radio = ui.radio(matches).classes('w-full').props('color=primary')
                    ui.button('Show Verses', on_click=lambda: handle_fuzzy_selection(radio.value)) \
                        .classes('w-full mt-4 bg-blue-500 text-white shadow-md')
                
                dialog.open()
            else:
                ui.notify('No matching topics found. Try "Hope", "Love", or "Peace".', type='negative')

    # --- Page Layout ---
    ui.colors(primary=PRIMARY_COLOR)
    
    # Header
    with ui.header().classes('bg-white shadow-sm border-b border-slate-200'):
        with ui.row().classes('w-full max-w-5xl mx-auto items-center h-16 px-4'):
            ui.icon('menu_book', size='md').classes('text-blue-500')
            ui.label('BibleMate AI').classes('text-xl font-bold text-slate-700 ml-2')
            ui.space()
            ui.button('Home', icon='home').props('flat color=grey')

    # Main Content Area
    with ui.element('div').classes('w-full min-h-screen p-4 flex flex-col items-center').style(f'background-color: {BG_COLOR}'):
        
        # Hero / Search Section
        ui.label("Find God's Promises").classes('text-4xl font-serif text-slate-800 mt-12 mb-2 text-center')
        ui.label("Search for a feeling, situation, or topic").classes('text-slate-500 mb-8 text-center')

        with ui.row().classes('w-full max-w-xl relative'):
            search_input = ui.input(placeholder='e.g., Anxiety, Peace, Healing...') \
                .classes('w-full text-lg bg-white rounded-full shadow-md px-6 py-2') \
                .props('outlined rounded item-aligned input-class="ml-2"') \
                .on('keydown.enter.prevent', perform_search)
            
            # Search icon inside the bar
            with search_input.add_slot('append'):
                ui.icon('search').classes('cursor-pointer text-slate-400 hover:text-blue-500').on('click', perform_search)

        # Results Area (injected here)
        results_container

    # Footer
    with ui.footer().classes('bg-slate-50 p-4 text-center text-slate-400 text-sm'):
        ui.label('© 2025 BibleMate AI')

# Run the app
if __name__ in {"__main__", "__mp_main__"}:
    search_page()
    ui.run(title='BibleMate Search', favicon='✝️', port=9999)
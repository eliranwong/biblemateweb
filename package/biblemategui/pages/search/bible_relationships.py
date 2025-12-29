from nicegui import ui, app
from biblemategui import BIBLEMATEGUI_DATA, get_translation
import os, apsw, re

# ==========================================
# MAIN PAGE
# ==========================================
def search_bible_relationships(gui=None, q='', **_):
    # State
    current_id = 994 # David
    if q:
        if re.search("^BP[0-9]+?$", q):
            q = q[2:]
        try:
            current_id = int(q)
        except:
            pass

    # ==========================================
    # DATA RETRIEVAL
    # ==========================================
    db_file = os.path.join(BIBLEMATEGUI_DATA, "data", "biblePeople.data")

    def get_person_details(person_id):
        with apsw.Connection(db_file) as connn:
            cursor = connn.cursor()
            cursor.execute("SELECT Name, Sex FROM PEOPLE WHERE PersonID = ?", (person_id,))
            fetch = cursor.fetchone()
        return fetch

    def get_all_people_options():
        with apsw.Connection(db_file) as connn:
            cursor = connn.cursor()
            cursor.execute("SELECT PersonID, Name FROM PEOPLE ORDER BY Name")
            fetch = cursor.fetchall()
        return {row[0]: row[1] for row in fetch}

    def get_family_data(person_id):
        """Categorizes family members for the UI."""
        '''
        SELECT DISTINCT Relationship FROM PEOPLERELATIONSHIP;

        [Reference]
        Father
        Mother
        Husband
        Wife / Concubine
        Brother
        Sister
        Son
        Daughter
        Half-brother [same father]
        Half-brother [same mother]
        Half-sister [same father]
        Half-sister [same mother]
        '''
        rows = []
        with apsw.Connection(db_file) as connn:
            cursor = connn.cursor()
            query = """
                SELECT r.RelatedPersonID, r.Relationship, p.Name, p.Sex
                FROM PEOPLERELATIONSHIP r
                JOIN PEOPLE p ON r.RelatedPersonID = p.PersonID
                WHERE r.PersonID = ?
            """
            cursor.execute(query, (person_id,))
            rows = cursor.fetchall()

        family = {'parents': [], 'spouses': [], 'children': [], 'siblings': [], 'siblings_same_father': [], 'siblings_same_mother': []}
        
        for rel_id, rel_type, rel_name, rel_sex in rows:
            p = {'id': rel_id, 'name': rel_name, 'sex': rel_sex, 'role': rel_type}
            rel_lower = rel_type.lower()
            
            if rel_lower in ('son', 'daughter') and not p in family['parents']: family['parents'].append(p)
            elif rel_lower in ('father', 'mother') and not p in family['children']: family['children'].append(p)
            elif rel_lower in ('husband', 'wife', 'wife / concubine', 'spouse') and not p in family['spouses']: family['spouses'].append(p)
            elif rel_lower in ('brother', 'sister') and not p in family['siblings']: family['siblings'].append(p)
            elif rel_lower in ('half-brother [same father]', 'half-sister [same father]') and not p in family['siblings_same_father']: family['siblings_same_father'].append(p)
            elif rel_lower in ('half-brother [same mother]', 'half-sister [same mother]') and not p in family['siblings_same_mother']: family['siblings_same_mother'].append(p)
        return family

    # ==========================================
    # COMPACT UI COMPONENTS
    # ==========================================

    def relation_chip(person, click_handler):
        """A small, clickable chip for a person. Best for mobile wrapping."""
        # Color logic: Blue for M, Pink for F
        if app.storage.user['dark_mode']:
            bg_color = 'blue-5' if person['sex'] == 'M' else 'pink-3'
            text_color = 'white'
            style = f'rounded unelevated color={bg_color} text-color={text_color} icon='
        else:
            color = 'blue' if person['sex'] == 'M' else 'pink'
            style = f'outline rounded color={color} icon='
        style += 'face' if person['sex'] == 'M' else 'face_3'
        
        # ui.button with 'outline' is cleaner than a card
        # 'no-wrap' ensures names don't break awkwardly
        with ui.button(on_click=lambda: click_handler(person['id'])) \
                .props(style) \
                .classes('px-3 py-1 text-sm capitalize'):
            ui.label(person['name']).classes('ml-1 truncate max-w-[120px]')

    # Handler
    def search_character_action():
        nonlocal gui, current_id
        """Logic when 'Character' button is clicked"""
        app.storage.user["tool_query"] = f"BP{current_id}"
        gui.select_empty_area2_tab()
        gui.load_area_2_content(title='Characters')

    def select_person(new_id):
        nonlocal current_id
        current_id = new_id
        search_dropdown.value = new_id
        view_area.refresh()

    # -- STICKY HEADER --
    with ui.row().classes('w-full items-center'):
        # Compact Search
        search_dropdown = ui.select(
            options=get_all_people_options(),
            value=current_id,
            on_change=lambda e: select_person(e.value),
            with_input=True
        ).props('dense options-dense outlined rounded').classes('w-48')

        # BUTTON 1: Character Search (Refresh/Profile)
        ui.button(icon='person', on_click=search_character_action) \
            .props('round flat dense text-color=white') \
            .tooltip('Go to Character Profile')

        # BUTTON 2: Verse Search
        ui.button(icon='menu_book', on_click=lambda: gui.show_all_verses(f"BP{current_id}")) \
            .props('round flat dense text-color=white') \
            .tooltip('Find Verses')

    # -- MAIN CONTENT AREA --
    # max-w-md makes it look like a mobile app even on desktop
    with ui.column().classes('w-full mx-auto p-2 gap-4 mt-2'):
        
        @ui.refreshable
        def view_area():
            details = get_person_details(current_id)
            if not details: return
            name, sex = details
            family = get_family_data(current_id)

            # 1. PARENTS SECTION (Top)
            # Only show if they exist
            if family['parents']:
                with ui.column().classes('w-full gap-1'):
                    ui.label('Parents').classes('text-xs font-bold text-gray-400 uppercase tracking-wide')
                    # flex-wrap is CRITICAL here: it prevents horizontal scrolling
                    with ui.row().classes('w-full flex-wrap gap-2'):
                        for p in family['parents']:
                            relation_chip(p, select_person)

            # 2. FOCUS PERSON (Hero Card)
            # This visually separates older gen from younger gen
            if app.storage.user['dark_mode']:
                bg_color = 'bg-gray-800'
                border_color = 'border-cyan-500' if sex == 'M' else 'border-fuchsia-500'
                text_color = 'text-cyan-400' if sex == 'M' else 'text-fuchsia-400'
            else:
                bg_color = 'bg-blue-100' if sex == 'M' else 'bg-pink-100'
                border_color = 'border-none'
                text_color = 'text-blue-800' if sex == 'M' else 'text-pink-800'
            
            with ui.card().classes(f'w-full {bg_color} {border_color} shadow-none py-4 items-center'):
                ui.label(name).classes(f'text-2xl font-black {text_color} text-center leading-tight')
                #ui.label('Selected Person').classes('text-xs opacity-50')
                
                # Spouses usually appear "Next" to the person
                if family['spouses']:
                    #ui.separator().classes('my-2 opacity-20')
                    ui.label('Spouse' if len(family['spouses']) == 1 else 'Spouses').classes('text-xs opacity-60 mb-1')
                    with ui.row().classes('justify-center flex-wrap gap-2'):
                        for p in family['spouses']:
                            relation_chip(p, select_person)

            # 3. CHILDREN SECTION
            if family['children']:
                with ui.column().classes('w-full gap-1 mt-2'):
                    ui.label('Children').classes('text-xs font-bold text-gray-400 uppercase tracking-wide')
                    with ui.row().classes('w-full flex-wrap gap-2'):
                        for p in family['children']:
                            relation_chip(p, select_person)

            # 4. SIBLINGS (Collapsible)
            # Collapsed by default to save space, solving "viewability"
            if family['siblings']:
                count = len(family['siblings'])
                with ui.expansion(f'Siblings ({count})', icon='group').classes('w-full rounded'+(' bg-gray-900 border border-gray-700' if app.storage.user['dark_mode'] else ' bg-gray-50 border border-gray-100')):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'+(' bg-[#1a1a1a]' if app.storage.user['dark_mode'] else '')):
                        for p in family['siblings']:
                            relation_chip(p, select_person)

            # 5. HALF-SIBLINGS [same father] (Collapsible)
            # Collapsed by default to save space, solving "viewability"
            if family['siblings_same_father']:
                count = len(family['siblings_same_father'])
                with ui.expansion(f'Half-Siblings [same father] ({count})', icon='group').classes('w-full rounded'+(' bg-gray-900 border border-gray-700' if app.storage.user['dark_mode'] else ' bg-gray-50 border border-gray-100')):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'+(' bg-[#1a1a1a]' if app.storage.user['dark_mode'] else '')):
                        for p in family['siblings_same_father']:
                            relation_chip(p, select_person)

            # 6. HALF-SIBLINGS [same mother] (Collapsible)
            # Collapsed by default to save space, solving "viewability"
            if family['siblings_same_mother']:
                count = len(family['siblings_same_mother'])
                with ui.expansion(f'Half-Siblings [same mother] ({count})', icon='group').classes('w-full rounded'+(' bg-gray-900 border border-gray-700' if app.storage.user['dark_mode'] else ' bg-gray-50 border border-gray-100')):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'+(' bg-[#1a1a1a]' if app.storage.user['dark_mode'] else '')):
                        for p in family['siblings_same_mother']:
                            relation_chip(p, select_person)

        view_area()


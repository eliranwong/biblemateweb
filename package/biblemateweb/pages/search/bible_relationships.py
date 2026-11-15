from nicegui import ui, app
from biblemateweb import BIBLEMATEWEB_DATA, get_translation
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
    db_file = os.path.join(BIBLEMATEWEB_DATA, "data", "biblePeople.data")

    table_map = {
        "tc": ("PEOPLE_TC", "PEOPLERELATIONSHIP_TC"),
        "sc": ("PEOPLE_SC", "PEOPLERELATIONSHIP_SC"),
    }
    people_table, relationship_table = table_map.get(
        app.storage.user.get("ui_language", "eng"),
        ("PEOPLE", "PEOPLERELATIONSHIP"),
    )

    def _primary_name(name):
        return name.split("|")[0] if name else name

    def get_person_details(person_id):
        with apsw.Connection(db_file) as connn:
            cursor = connn.cursor()
            cursor.execute(
                f"""
                SELECT Name, Sex
                FROM {people_table}
                WHERE PersonID = ?
                GROUP BY Name, Sex
                ORDER BY COUNT(*) DESC, MIN(Number) ASC
                LIMIT 1
                """,
                (person_id,),
            )
            fetch = cursor.fetchone()
            if not fetch:
                cursor.execute(
                    f"SELECT Name, Sex FROM {relationship_table} WHERE PersonID = ? LIMIT 1",
                    (person_id,),
                )
                fetch = cursor.fetchone()
                if fetch:
                    fetch = (_primary_name(fetch[0]), fetch[1])
        return fetch

    def get_all_people_options():
        with apsw.Connection(db_file) as connn:
            cursor = connn.cursor()
            cursor.execute(
                f"""
                WITH ranked AS (
                    SELECT
                        PersonID,
                        Name,
                        ROW_NUMBER() OVER (
                            PARTITION BY PersonID
                            ORDER BY COUNT(*) DESC, MIN(Number) ASC
                        ) AS rn
                    FROM {people_table}
                    GROUP BY PersonID, Name
                )
                SELECT PersonID, Name
                FROM ranked
                WHERE rn = 1
                ORDER BY Name
                """
            )
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
        with apsw.Connection(db_file) as connn:
            cursor = connn.cursor()
            query = f"""
                WITH primary_people AS (
                    SELECT PersonID, Name, Sex
                    FROM (
                        SELECT
                            PersonID,
                            Name,
                            Sex,
                            ROW_NUMBER() OVER (
                                PARTITION BY PersonID
                                ORDER BY COUNT(*) DESC, MIN(Number) ASC
                            ) AS rn
                        FROM {people_table}
                        GROUP BY PersonID, Name, Sex
                    )
                    WHERE rn = 1
                ),
                rel_people AS (
                    SELECT PersonID, Name, Sex
                    FROM {relationship_table}
                    GROUP BY PersonID
                )
                SELECT DISTINCT
                    r.RelatedPersonID,
                    r.Relationship,
                    COALESCE(p.Name, rp.Name) AS Name,
                    COALESCE(p.Sex, rp.Sex) AS Sex,
                    r.RelationshipOrder
                FROM {relationship_table} r
                LEFT JOIN primary_people p ON r.RelatedPersonID = p.PersonID
                LEFT JOIN rel_people rp ON r.RelatedPersonID = rp.PersonID
                WHERE r.PersonID = ?
                ORDER BY r.RelationshipOrder, Name
            """
            cursor.execute(query, (person_id,))
            rows = cursor.fetchall()

        family = {
            'parents': [],
            'spouses': [],
            'children': [],
            'siblings': [],
            'siblings_same_father': [],
            'siblings_same_mother': [],
        }
        seen = {k: set() for k in family}
        category_map = {
            'son': 'parents',
            'daughter': 'parents',
            'father': 'children',
            'mother': 'children',
            'husband': 'spouses',
            'wife': 'spouses',
            'wife / concubine': 'spouses',
            'spouse': 'spouses',
            'brother': 'siblings',
            'sister': 'siblings',
            'half-brother [same father]': 'siblings_same_father',
            'half-sister [same father]': 'siblings_same_father',
            'half-brother [same mother]': 'siblings_same_mother',
            'half-sister [same mother]': 'siblings_same_mother',
        }

        for rel_id, rel_type, rel_name, rel_sex, _ in rows:
            category = category_map.get(rel_type.lower())
            if not category or rel_id in seen[category]:
                continue
            seen[category].add(rel_id)
            family[category].append({
                'id': rel_id,
                'name': _primary_name(rel_name),
                'sex': rel_sex,
                'role': rel_type,
            })
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
        if new_id is None:
            return
        current_id = new_id
        if new_id in search_dropdown.options:
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
            .tooltip(get_translation('Go to Character Profile'))

        # BUTTON 2: Verse Search
        ui.button(icon='menu_book', on_click=lambda: gui.show_all_verses(f"BP{current_id}")) \
            .props('round flat dense text-color=white') \
            .tooltip(get_translation('Find Verses'))

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
                    ui.label(get_translation('Parents')).classes('text-xs font-bold text-gray-400 uppercase tracking-wide')
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
                    ui.label(get_translation('Spouse' if len(family['spouses']) == 1 else 'Spouses')).classes('text-xs opacity-60 mb-1')
                    with ui.row().classes('justify-center flex-wrap gap-2'):
                        for p in family['spouses']:
                            relation_chip(p, select_person)

            # 3. CHILDREN SECTION
            if family['children']:
                with ui.column().classes('w-full gap-1 mt-2'):
                    ui.label(get_translation('Children')).classes('text-xs font-bold text-gray-400 uppercase tracking-wide')
                    with ui.row().classes('w-full flex-wrap gap-2'):
                        for p in family['children']:
                            relation_chip(p, select_person)

            # 4. SIBLINGS (Collapsible)
            # Collapsed by default to save space, solving "viewability"
            if family['siblings']:
                count = len(family['siblings'])
                with ui.expansion(f"{get_translation('Siblings')} ({count})", icon='group').classes('w-full rounded'+(' bg-gray-900 border border-gray-700' if app.storage.user['dark_mode'] else ' bg-gray-50 border border-gray-100')):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'+(' bg-[#1a1a1a]' if app.storage.user['dark_mode'] else '')):
                        for p in family['siblings']:
                            relation_chip(p, select_person)

            # 5. HALF-SIBLINGS [same father] (Collapsible)
            # Collapsed by default to save space, solving "viewability"
            if family['siblings_same_father']:
                count = len(family['siblings_same_father'])
                with ui.expansion(f"{get_translation('Half-Siblings [same father]')} ({count})", icon='group').classes('w-full rounded'+(' bg-gray-900 border border-gray-700' if app.storage.user['dark_mode'] else ' bg-gray-50 border border-gray-100')):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'+(' bg-[#1a1a1a]' if app.storage.user['dark_mode'] else '')):
                        for p in family['siblings_same_father']:
                            relation_chip(p, select_person)

            # 6. HALF-SIBLINGS [same mother] (Collapsible)
            # Collapsed by default to save space, solving "viewability"
            if family['siblings_same_mother']:
                count = len(family['siblings_same_mother'])
                with ui.expansion(f"{get_translation('Half-Siblings [same mother]')} ({count})", icon='group').classes('w-full rounded'+(' bg-gray-900 border border-gray-700' if app.storage.user['dark_mode'] else ' bg-gray-50 border border-gray-100')):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'+(' bg-[#1a1a1a]' if app.storage.user['dark_mode'] else '')):
                        for p in family['siblings_same_mother']:
                            relation_chip(p, select_person)

        view_area()


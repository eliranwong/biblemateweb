import sqlite3
from nicegui import ui
import os

# ==========================================
# 1. DATABASE SETUP (Mock Data for Testing)
# ==========================================
# REPLACE ':memory:' with your actual 'bible.db' file
db_file = os.path.expanduser("~/UniqueBible/marvelData/data/biblePeople.data")
db_connection = sqlite3.connect(db_file, check_same_thread=False)
cursor = db_connection.cursor()

'''
# Create tables/data (Same as before, ensuring it runs out-of-the-box)
cursor.execute('CREATE TABLE IF NOT EXISTS "PEOPLE" (PersonID INT, Name TEXT, Sex TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS "PEOPLERELATIONSHIP" (PersonID INT, RelatedPersonID INT, Relationship TEXT)')
# (Skipping re-inserting data if it exists for brevity, but assuming data is there from previous step)
# --- Re-inserting mock data for this run just in case ---
cursor.execute('DELETE FROM PEOPLE'); cursor.execute('DELETE FROM PEOPLERELATIONSHIP')
people_data = [
    (58, 'Abram / Abraham', 'M'), (616, 'Isaac', 'M'), (620, 'Ishbak', 'M'),
    (630, 'Ishmael', 'M'), (1348, 'Hagar', 'F'), (1407, 'Haran', 'M'),
    (1782, 'Keturah', 'F'), (2143, 'Nahor', 'M'), (2473, 'Sarai / Sarah', 'F'),
    (2841, 'Terah', 'M'), (3000, 'Lot', 'M')
]
cursor.executemany('INSERT INTO PEOPLE VALUES (?,?,?)', people_data)
rel_data = [
    (58, 616, 'Father'), (58, 620, 'Father'), (58, 630, 'Father'),
    (58, 1348, 'Husband'), (58, 1407, 'Brother'), (58, 1782, 'Husband'),
    (58, 2143, 'Brother'), (58, 2473, 'Husband'), (58, 2841, 'Son'),
    (1407, 3000, 'Father') # Haran is father of Lot
]
cursor.executemany('INSERT INTO PEOPLERELATIONSHIP VALUES (?,?,?)', rel_data)
db_connection.commit()
'''

# ==========================================
# 2. LOGIC
# ==========================================
def get_person_details(person_id):
    cur = db_connection.cursor()
    cur.execute("SELECT Name, Sex FROM PEOPLE WHERE PersonID = ?", (person_id,))
    return cur.fetchone()

def get_all_people_options():
    cur = db_connection.cursor()
    cur.execute("SELECT PersonID, Name FROM PEOPLE ORDER BY Name")
    return {row[0]: row[1] for row in cur.fetchall()}

def get_family_data(person_id):
    """Categorizes family members for the UI."""
    cur = db_connection.cursor()
    query = """
        SELECT r.RelatedPersonID, r.Relationship, p.Name, p.Sex
        FROM PEOPLERELATIONSHIP r
        JOIN PEOPLE p ON r.RelatedPersonID = p.PersonID
        WHERE r.PersonID = ?
    """
    cur.execute(query, (person_id,))
    rows = cur.fetchall()

    family = {'parents': [], 'spouses': [], 'siblings': [], 'children': []}
    
    for rel_id, rel_type, rel_name, rel_sex in rows:
        p = {'id': rel_id, 'name': rel_name, 'sex': rel_sex, 'role': rel_type}
        rel_lower = rel_type.lower()
        
        if rel_lower in ['son', 'daughter'] and not p in family['parents']: family['parents'].append(p)
        elif rel_lower in ['father', 'mother'] and not p in family['children']: family['children'].append(p)
        elif rel_lower in ['husband', 'wife', 'wife / concubine', 'spouse'] and not p in family['spouses']: family['spouses'].append(p)
        elif rel_lower in ['brother', 'sister'] and not p in family['siblings']: family['siblings'].append(p)
            
    return family

# ==========================================
# 3. COMPACT UI COMPONENTS
# ==========================================

def relation_chip(person, click_handler):
    """A small, clickable chip for a person. Best for mobile wrapping."""
    # Color logic: Blue for M, Pink for F
    color = 'blue' if person['sex'] == 'M' else 'pink'
    icon = 'face' if person['sex'] == 'M' else 'face_3'
    
    # ui.button with 'outline' is cleaner than a card
    # 'no-wrap' ensures names don't break awkwardly
    with ui.button(on_click=lambda: click_handler(person['id'])) \
            .props(f'outline rounded color={color} icon={icon}') \
            .classes('px-3 py-1 text-sm capitalize'):
        ui.label(person['name']).classes('ml-1 truncate max-w-[120px]')

# ==========================================
# 4. MAIN PAGE
# ==========================================
@ui.page('/')
def main_page():
    # State
    current_id = 58 

    # Handler
    def select_person(new_id):
        nonlocal current_id
        current_id = new_id
        search_dropdown.value = new_id
        view_area.refresh()

    # -- STICKY HEADER --
    with ui.header().classes('bg-white border-b shadow-sm p-2'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('BibleMate').classes('font-bold text-gray-700')
            
            # Compact Search
            search_dropdown = ui.select(
                options=get_all_people_options(),
                value=current_id,
                on_change=lambda e: select_person(e.value),
                with_input=True
            ).props('dense options-dense outlined rounded').classes('w-48')

    # -- MAIN CONTENT AREA --
    # max-w-md makes it look like a mobile app even on desktop
    with ui.column().classes('w-full max-w-md mx-auto p-2 gap-4 mt-2'):
        
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
            bg_color = 'bg-blue-100' if sex == 'M' else 'bg-pink-100'
            text_color = 'text-blue-800' if sex == 'M' else 'text-pink-800'
            
            with ui.card().classes(f'w-full {bg_color} border-none shadow-none py-4 items-center'):
                ui.label(name).classes(f'text-2xl font-black {text_color} text-center leading-tight')
                #ui.label('Selected Person').classes('text-xs opacity-50')
                
                # Spouses usually appear "Next" to the person
                if family['spouses']:
                    ui.separator().classes('my-2 opacity-20')
                    ui.label('Spouse(s)').classes('text-xs opacity-60 mb-1')
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
                with ui.expansion(f'Siblings ({count})', icon='group').classes('w-full bg-gray-50 rounded mt-4'):
                    with ui.row().classes('w-full flex-wrap gap-2 p-2'):
                        for p in family['siblings']:
                            relation_chip(p, select_person)

        view_area()


ui.run(port=9999)
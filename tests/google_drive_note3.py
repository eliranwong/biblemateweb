import os
from nicegui import app, ui
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import json
from fastapi import Request
from fastapi.responses import RedirectResponse

# --- Configuration ---
# In production, use environment variables!
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = 'your_random_secret_string'

# --- OAuth Setup ---
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'https://www.googleapis.com/auth/drive.appdata openid email profile'},
)

# --- Google Drive Helpers ---
def get_drive_service(user_token):
    """Builds the Drive service using the user's stored token."""
    creds = Credentials(
        token=user_token['access_token'],
        refresh_token=user_token.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/drive.appdata']
    )
    return build('drive', 'v3', credentials=creds)

def get_filename(verse_id):
    """Standardizes filename, e.g., '43_3_16.json'"""
    return f"{verse_id}.json"

def save_verse_note(verse_id, note_content):
    """Saves a note for a specific verse as a separate file."""
    token = app.storage.user.get('google_token')
    if not token:
        ui.notify('Please log in first!', type='warning')
        return

    try:
        service = get_drive_service(token)
        filename = get_filename(verse_id)
        
        # 1. Search for THIS specific verse file
        results = service.files().list(
            q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
            spaces='appDataFolder',
            fields='files(id, name)'
        ).execute()
        files = results.get('files', [])

        # Content to save
        file_data = {
            "verse_id": verse_id,
            "content": note_content,
            "updated_at": "2023-10-27T10:00:00" # You can add timestamps here
        }
        json_str = json.dumps(file_data)
        media = MediaIoBaseUpload(io.BytesIO(json_str.encode('utf-8')), mimetype='application/json')

        if not files:
            # CREATE new file for this verse
            file_metadata = {
                'name': filename,
                'parents': ['appDataFolder']
            }
            service.files().create(body=file_metadata, media_body=media).execute()
            ui.notify(f'Note created for {verse_id}')
        else:
            # UPDATE existing file for this verse
            file_id = files[0]['id']
            service.files().update(fileId=file_id, media_body=media).execute()
            ui.notify(f'Note updated for {verse_id}')
            
    except Exception as e:
        ui.notify(f'Error saving: {str(e)}', type='negative')

def load_verse_note(verse_id):
    """Loads the note for a specific verse."""
    token = app.storage.user.get('google_token')
    if not token: return ""

    try:
        service = get_drive_service(token)
        filename = get_filename(verse_id)
        
        results = service.files().list(
            q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
            spaces='appDataFolder',
            fields='files(id)'
        ).execute()
        files = results.get('files', [])

        if files:
            file_id = files[0]['id']
            request = service.files().get_media(fileId=file_id)
            file_content = request.execute()
            data = json.loads(file_content)
            return data.get("content", "")
        return "" # No note exists for this verse yet
    except Exception as e:
        print(f"Load error: {e}")
        return ""

class IndexManager:
    def __init__(self, drive_service=None):
        self.service = drive_service
        self.filename = 'bible_index.json'
        self.data = {} # Stores simple list of verse_ids: {"43_3_16": true, ...}
        self.file_id = None # Google Drive ID for the index file

    def load_from_drive(self):
        """Downloads the index file once at startup."""
        if not self.service: return {}
        
        try:
            # Search for existing index
            results = self.service.files().list(
                q=f"name='{self.filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                self.file_id = files[0]['id']
                request = self.service.files().get_media(fileId=self.file_id)
                content = request.execute()
                self.data = json.loads(content)
                print(f"Index loaded: {len(self.data)} notes found.")
            else:
                print("No index found. Starting fresh.")
                self.data = {}
                self.save_to_drive() # Create the file
                
        except Exception as e:
            print(f"Error loading index: {e}")
        
        return self.data

    def save_to_drive(self):
        """Syncs the current index back to Google Drive."""
        if not self.service: return

        content = json.dumps(self.data)
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='application/json')
        
        file_metadata = {
            'name': self.filename,
            'parents': ['appDataFolder']
        }

        try:
            if self.file_id:
                # Update existing
                self.service.files().update(fileId=self.file_id, media_body=media).execute()
            else:
                # Create new
                file = self.service.files().create(body=file_metadata, media_body=media).execute()
                self.file_id = file.get('id')
            print("Index synced to Drive.")
        except Exception as e:
            print(f"Error saving index: {e}")

    def add_verse(self, verse_id):
        """Marks a verse as having a note and syncs if it's new."""
        if verse_id not in self.data:
            self.data[verse_id] = True
            self.save_to_drive() # Sync immediately so we don't lose data

    def has_note(self, verse_id):
        """Instant check if a note exists."""
        return verse_id in self.data

    def get_chapter_notes(self, book, chapter):
        """Returns a list of all Verse IDs with notes in this chapter."""
        prefix = f"{book}_{chapter}_"
        # Fast filter of the keys
        return [vid for vid in self.data.keys() if vid.startswith(prefix)]

# --- UI ---

@ui.page('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@ui.page('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        app.storage.user['google_token'] = token
        
        # Get user info (Optional, but good for display)
        resp = await oauth.google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
        user_info = resp.json()
        app.storage.user['name'] = user_info.get('name')
        print(app.storage.user['name'])
        
        # CORRECT WAY TO REDIRECT:
        return RedirectResponse('/')  
        
    except Exception as e:
        ui.notify(f"Login failed: {e}")
        return RedirectResponse('/')

# ... (Previous imports) ...

@ui.page('/')
def main_page():
    # 1. Auth Check
    token = app.storage.user.get('google_token')
    if not token:
        ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
        return

    # 2. Initialize Drive Service & Index
    # Note: In a real app, you might cache this service or index in app.storage 
    # so you don't reload it on every page refresh.
    service = get_drive_service(token)
    index_mgr = IndexManager(service)
    
    # Load index immediately (First time might take 1 sec, afterwards it's in memory)
    if 'cached_index' not in app.storage.user:
        app.storage.user['cached_index'] = index_mgr.load_from_drive()
    else:
        index_mgr.data = app.storage.user['cached_index']

    # --- UI Components ---
    
    # State
    current_verse = {'b': 43, 'c': 3, 'v': 16}
    
    def get_vid():
        return f"{current_verse['b']}_{current_verse['c']}_{current_verse['v']}"

    # Wrapper to Save Note AND Update Index
    def save_current_note():
        vid = get_vid()
        content = note_editor.value
        
        # 1. Save the actual content file (using our previous function)
        save_verse_note(vid, content) 
        
        # 2. Update the Index
        index_mgr.add_verse(vid)
        app.storage.user['cached_index'] = index_mgr.data # Update session cache
        
        ui.notify('Saved & Indexed!')
        refresh_chapter_stats() # Update the UI counter

    def refresh_chapter_stats():
        """Shows the power of the Index File!"""
        # Finds all notes for current chapter instantly
        notes_in_chapter = index_mgr.get_chapter_notes(current_verse['b'], current_verse['c'])
        count = len(notes_in_chapter)

        stats_label.text = f"Chapter {current_verse['c']} has {count} notes."
        # Optional: Show which verses have notes
        note_list_label.text = f"Verses with notes: {', '.join(notes_in_chapter)}"

    # UI Function to reload note when verse changes
    def load_current_note():
        vid = get_vid()
        content = load_verse_note(vid)
        note_editor.value = content

    def update_nav(b, c, v):
        current_verse['b'] = b
        current_verse['c'] = c
        current_verse['v'] = v
        load_current_note()
        refresh_chapter_stats()

    with ui.column().classes('p-4 gap-4'):
        ui.label('BibleMate AI').classes('text-2xl')

        # Navigation Simulation
        with ui.row():
            ui.button('John 3:16', on_click=lambda: update_nav(43,3,16))
            ui.button('John 3:17', on_click=lambda: update_nav(43,3,17))
        
        # Stats Section (The feature you requested)
        with ui.card().classes('bg-blue-50'):
            stats_label = ui.label()
            note_list_label = ui.label().classes('text-xs text-gray-600')

        # Editor
        note_editor = ui.textarea().classes('w-full')
        ui.button('Save Note', on_click=save_current_note)

    # Initial Render
    refresh_chapter_stats()

ui.run(storage_secret=SECRET_KEY, port=33355)
import os
import json
import io
from nicegui import app, ui
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 1. CONFIGURATION ---
# Replace these with your actual keys or load from .env
# GOOGLE_CLIENT_ID = 'YOUR_CLIENT_ID'
# GOOGLE_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
# SECRET_KEY = 'YOUR_RANDOM_SECRET_KEY'

# FOR TESTING ONLY (Remove these lines if using .env):
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = 'random_secret_string_for_testing'

# --- 2. OAUTH SETUP ---
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/drive.appdata openid email profile',
        'prompt': 'consent',      # <--- FORCE new refresh token
    }, 
    # This is critical for the error you saw:
    authorize_params={'access_type': 'offline'} 
)

# --- 3. GOOGLE DRIVE HELPERS ---

def get_drive_service(user_token):
    """Builds the Drive service with full refresh capabilities."""
    if not user_token: return None
    
    # We manually reconstruct the Credentials object with ALL details
    # so Google can refresh the token automatically when it expires.
    creds = Credentials(
        token=user_token.get('access_token'),
        refresh_token=user_token.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/drive.appdata']
    )
    return build('drive', 'v3', credentials=creds)

def get_filename(verse_id):
    return f"{verse_id}.json"

# --- 4. INDEX MANAGER CLASS ---

class IndexManager:
    def __init__(self, drive_service):
        self.service = drive_service
        self.filename = 'bible_index.json'
        self.data = {} 
        self.file_id = None 

    def load_from_drive(self):
        """Downloads the index file once at startup."""
        if not self.service: return {}
        try:
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
            else:
                self.data = {}
                self.save_to_drive() # Create initial file
        except Exception as e:
            print(f"Index Load Error: {e}")
        return self.data

    def save_to_drive(self):
        """Syncs the current index back to Google Drive."""
        if not self.service: return
        content = json.dumps(self.data)
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='application/json')
        file_metadata = {'name': self.filename, 'parents': ['appDataFolder']}

        try:
            if self.file_id:
                self.service.files().update(fileId=self.file_id, media_body=media).execute()
            else:
                file = self.service.files().create(body=file_metadata, media_body=media).execute()
                self.file_id = file.get('id')
        except Exception as e:
            print(f"Index Save Error: {e}")

    def add_verse(self, verse_id):
        if verse_id not in self.data:
            self.data[verse_id] = True
            self.save_to_drive()

    def remove_verse(self, verse_id):
        if verse_id in self.data:
            del self.data[verse_id]
            self.save_to_drive()

    def get_chapter_notes(self, book, chapter):
        prefix = f"{book}_{chapter}_"
        return [k for k in self.data.keys() if k.startswith(prefix)]

    def get_chapter_count(self, book, chapter):
        return len(self.get_chapter_notes(book, chapter))

# --- 5. UI PAGES ---

@ui.page('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@ui.page('/auth')
async def auth(request: Request):
    try:
        # access_type='offline' in config ensures we get a refresh_token here
        token = await oauth.google.authorize_access_token(request)
        app.storage.user['google_token'] = token
        return RedirectResponse('/')
    except Exception as e:
        ui.notify(f"Login failed: {e}")
        return RedirectResponse('/')

@ui.page('/')
def main_page():
    # 1. Auth Check
    token = app.storage.user.get('google_token')
    if not token:
        with ui.card().classes('absolute-center'):
            ui.label('Welcome to BibleMate AI')
            ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
        return

    # 2. Initialize Service & Index
    service = get_drive_service(token)
    index_mgr = IndexManager(service)
    
    # Cache index in session so we don't download it on every click
    if 'cached_index' not in app.storage.user:
        app.storage.user['cached_index'] = index_mgr.load_from_drive()
    else:
        index_mgr.data = app.storage.user['cached_index']

    # 3. State Management
    current_verse = {'b': 43, 'c': 3, 'v': 16} # Start at John 3:16

    def get_vid(): 
        return f"{current_verse['b']}_{current_verse['c']}_{current_verse['v']}"

    # 4. Note Logic
    def load_current_note():
        vid = get_vid()
        try:
            filename = get_filename(vid)
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])
            
            if files:
                request = service.files().get_media(fileId=files[0]['id'])
                data = json.loads(request.execute())
                return data.get("content", "")
            return ""
        except Exception as e:
            ui.notify(f"Error loading: {e}", type='negative')
            return ""

    def save_current_note():
        vid = get_vid()
        content = note_editor.value
        try:
            filename = get_filename(vid)
            file_data = {"verse_id": vid, "content": content}
            media = MediaIoBaseUpload(io.BytesIO(json.dumps(file_data).encode('utf-8')), mimetype='application/json')
            
            # Find existing
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                service.files().update(fileId=files[0]['id'], media_body=media).execute()
            else:
                meta = {'name': filename, 'parents': ['appDataFolder']}
                service.files().create(body=meta, media_body=media).execute()

            # Update Index
            index_mgr.add_verse(vid)
            app.storage.user['cached_index'] = index_mgr.data
            
            ui.notify('Saved!')
            refresh_ui()
        except Exception as e:
            ui.notify(f"Error saving: {e}", type='negative')

    def delete_current_note():
        vid = get_vid()
        try:
            filename = get_filename(vid)
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                service.files().delete(fileId=files[0]['id']).execute()
                index_mgr.remove_verse(vid)
                app.storage.user['cached_index'] = index_mgr.data
                note_editor.value = ""
                ui.notify('Note deleted.')
                refresh_ui()
            else:
                ui.notify('Nothing to delete.')
        except Exception as e:
            ui.notify(f"Delete error: {e}", type='negative')

    # 5. UI Rendering
    def refresh_ui():
        # Update Stats
        count = index_mgr.get_chapter_count(current_verse['b'], current_verse['c'])
        stats_label.text = f"Chapter {current_verse['c']} has {count} notes."
        # Update Header
        header_label.text = f"Editing Note: John {current_verse['c']}:{current_verse['v']}"

    def update_nav(b, c, v):
        current_verse.update({'b':b, 'c':c, 'v':v})
        note_editor.value = load_current_note()
        refresh_ui()

    with ui.column().classes('w-full items-center p-8 gap-6'):
        ui.label('BibleMate AI - Notes').classes('text-3xl font-bold text-blue-800')
        
        # Navigation
        with ui.row().classes('gap-4'):
            ui.button('John 3:16', on_click=lambda: update_nav(43,3,16))
            ui.button('John 3:17', on_click=lambda: update_nav(43,3,17))
            ui.button('John 3:18', on_click=lambda: update_nav(43,3,18))

        stats_label = ui.label().classes('text-gray-500 font-mono')
        
        # Editor Card
        with ui.card().classes('w-full max-w-2xl bg-gray-50 p-6'):
            header_label = ui.label().classes('text-lg font-bold mb-2')
            note_editor = ui.textarea(placeholder='Type your thoughts here...') \
                .classes('w-full h-48 bg-white').props('outlined')
            
            # Action Buttons
            with ui.row().classes('w-full justify-between mt-4'):
                # Delete + Dialog
                with ui.dialog() as delete_dialog, ui.card():
                    ui.label('Are you sure you want to delete this note?')
                    with ui.row().classes('justify-end w-full'):
                        ui.button(get_translation("Cancel"), on_click=delete_dialog.close).props('flat')
                        ui.button('Delete', color='red', on_click=lambda: [delete_current_note(), delete_dialog.close()])
                
                ui.button('Delete', color='red', icon='delete', on_click=delete_dialog.open).props('flat')
                ui.button('Save Note', icon='save', on_click=save_current_note)
        
        # Logout
        ui.button('Logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('outline')

    # Initial Load
    note_editor.value = load_current_note()
    refresh_ui()

ui.run(storage_secret=SECRET_KEY, port=33355)
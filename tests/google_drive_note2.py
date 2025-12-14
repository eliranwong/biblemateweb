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

@ui.page('/')
def main_page():
    if not app.storage.user.get('google_token'):
        ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
        return

    # User State to track current verse
    # In a real app, this might come from the URL or a state manager
    current_verse = {
        'book': 43, # John (Example ID)
        'chapter': 3,
        'verse': 16
    }
    
    def get_current_id():
        return f"{current_verse['book']}_{current_verse['chapter']}_{current_verse['verse']}"

    # UI Function to reload note when verse changes
    def load_current_note():
        vid = get_current_id()
        content = load_verse_note(vid)
        note_editor.value = content
        status_label.text = f"Editing: {vid}"

    with ui.column().classes('w-full items-center gap-4 p-4'):
        ui.label('BibleMate AI - Verse Notes').classes('text-2xl font-bold')
        
        # --- Verse Selector Simulation ---
        with ui.card().classes('w-full max-w-2xl bg-gray-100'):
            ui.label('Simulate Navigation').classes('text-xs text-gray-500')
            with ui.row().classes('gap-2'):
                # Simple buttons to simulate changing verses
                ui.button('John 3:16', on_click=lambda: update_verse(43,3,16))
                ui.button('Gen 1:1', on_click=lambda: update_verse(1,1,1))
                ui.button('Psalm 23:1', on_click=lambda: update_verse(19,23,1))

        status_label = ui.label(f"Editing: {get_current_id()}").classes('text-sm font-mono')

        # --- Note Editor ---
        note_editor = ui.textarea(placeholder='Type your thoughts here...') \
            .classes('w-full max-w-2xl h-48').props('outlined')

        ui.button('Save Note', 
                  on_click=lambda: save_verse_note(get_current_id(), note_editor.value))

    def update_verse(b, c, v):
        current_verse['book'] = b
        current_verse['chapter'] = c
        current_verse['verse'] = v
        load_current_note()

    # Initial load
    load_current_note()

ui.run(storage_secret=SECRET_KEY, port=33355)
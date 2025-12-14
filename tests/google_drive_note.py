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

def save_note_to_drive(note_content):
    """Saves the note to the hidden App Data folder in Drive."""
    token = app.storage.user.get('google_token')
    if not token:
        ui.notify('Please log in first!')
        return

    try:
        service = get_drive_service(token)
        filename = 'biblemate_notes.json'
        
        # 1. Search for existing file in appDataFolder
        results = service.files().list(
            q=f"name='{filename}' and 'appDataFolder' in parents",
            spaces='appDataFolder',
            fields='files(id, name)'
        ).execute()
        files = results.get('files', [])

        file_metadata = {
            'name': filename,
            'parents': ['appDataFolder'] # Save to hidden folder
        }
        
        # Prepare content (JSON format allows you to add verse refs later)
        content = json.dumps({"notes": note_content})
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='application/json')

        if not files:
            # Create new file
            service.files().create(body=file_metadata, media_body=media).execute()
            ui.notify('Created new notes file in Drive!')
        else:
            # Update existing file
            file_id = files[0]['id']
            service.files().update(fileId=file_id, media_body=media).execute()
            ui.notify('Notes saved to Drive!')
            
    except Exception as e:
        ui.notify(f'Error saving: {str(e)}', type='negative')

def load_note_from_drive():
    """Loads the note from Drive."""
    token = app.storage.user.get('google_token')
    if not token: 
        return ""

    try:
        service = get_drive_service(token)
        filename = 'biblemate_notes.json'
        
        results = service.files().list(
            q=f"name='{filename}' and 'appDataFolder' in parents",
            spaces='appDataFolder',
            fields='files(id)'
        ).execute()
        files = results.get('files', [])

        if files:
            file_id = files[0]['id']
            request = service.files().get_media(fileId=file_id)
            file_content = request.execute()
            data = json.loads(file_content)
            return data.get("notes", "")
        return ""
    except Exception as e:
        print(f"Load error: {e}")
        return ""

# --- UI Pages ---

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
    # Check if logged in
    if not app.storage.user.get('google_token'):
        with ui.card().classes('absolute-center'):
            ui.label('Welcome to BibleMate AI')
            ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
        return

    # User is logged in
    user_name = app.storage.user.get('name', 'User')
    
    with ui.column().classes('w-full items-center gap-4 p-4'):
        ui.label(f'Welcome, {user_name}!').classes('text-2xl')
        
        # Note Taking Area
        with ui.card().classes('w-full max-w-2xl'):
            ui.label('Your Verse Notes').classes('text-lg font-bold')
            
            # Load initial content
            initial_content = load_note_from_drive()
            note_input = ui.textarea(value=initial_content).classes('w-full h-64').props('outlined')
            
            with ui.row():
                ui.button('Save to Drive', on_click=lambda: save_note_to_drive(note_input.value))
                ui.button('Logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/')))

ui.run(storage_secret=SECRET_KEY, port=33355)
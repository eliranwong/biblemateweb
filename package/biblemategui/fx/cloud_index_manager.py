from biblemategui import config
import os, re, json, io
from nicegui import app, ui
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def get_drive_service(user_token):
    """Builds the Drive service with full refresh capabilities."""
    if not user_token: return None
    
    # We manually reconstruct the Credentials object with ALL details
    # so Google can refresh the token automatically when it expires.
    creds = Credentials(
        token=user_token.get('access_token'),
        refresh_token=user_token.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=config.google_client_id,
        client_secret=config.google_client_secret,
        scopes=['https://www.googleapis.com/auth/drive.appdata']
    )
    return build('drive', 'v3', credentials=creds)

class CloudIndexManager:
    def __init__(self, drive_service):
        self.service = drive_service
        self.filename = 'bible_index.json'
        self.file_id = None
        # important - load master index
        if "cached_index" in app.storage.user:
            self.data = app.storage.user['cached_index']
        else:
            ui.timer(0, lambda: loading(self.load_from_drive), once=True)
            app.storage.user['cached_index'] = self.data

    def rebuild_index(self):
        """
        Scans ALL files in the hidden App Data folder and reconstructs 
        the index from scratch. useful if the index file gets corrupted.
        """
        if not self.service: return 0

        print("Starting Index Rebuild...")
        new_index = {}
        page_token = None

        try:
            while True:
                # 1. Search for ALL JSON files in the app folder
                response = self.service.files().list(
                    q="mimeType='application/json' and 'appDataFolder' in parents and trashed=false",
                    spaces='appDataFolder',
                    fields='nextPageToken, files(id, name)',
                    pageToken=page_token
                ).execute()

                files = response.get('files', [])

                for file in files:
                    name = file.get('name')
                    
                    # Skip the index file itself
                    if name == self.filename:
                        # (Optional) Update self.file_id to ensure we overwrite the correct file later
                        self.file_id = file.get('id')
                        continue

                    # Check if file is a verse note (e.g., "43_3_16.json")
                    if name.endswith('.json'):
                        # Remove .json extension to get ID
                        verse_id = name.replace('.json', '')
                        # Simple validation: ensure it looks like numbers_numbers_numbers
                        parts = verse_id.split('_')
                        if len(parts) == 3 and all(p.isdigit() for p in parts):
                            new_index[verse_id] = True

                # 2. Handle Pagination (Google returns max 100 files per page by default)
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

            # 3. Overwrite internal data and sync
            self.data = new_index
            self.save_to_drive()
            print(f"Rebuild Complete. Found {len(self.data)} notes.")
            return len(self.data)

        except Exception as e:
            print(f"Critical Rebuild Error: {e}")
            return -1

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
    
    def get_chapter_notes_verselist(self, book, chapter):
        return [i.split("_")[-1] for i in self.get_chapter_notes(book, chapter) if re.search("_[0-9]+?$", i)]
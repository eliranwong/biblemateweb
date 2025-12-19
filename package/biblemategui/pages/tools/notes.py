import os, re, apsw, zipfile, json, io, markdown2, re, base64
import urllib.parse
from nicegui import ui, app, run
from biblemategui import config, BIBLEMATEGUI_DATA, get_translation, loading
from biblemategui.fx.bible import BibleSelector
from functools import partial
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemategui.fx.cloud_index_manager import get_drive_service, CloudIndexManager
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class CloudNotepad:
    def __init__(self, content=""):
        self.text_content = content
        self.is_editing = True
        self.parser = BibleVerseParser(False, language=app.storage.user['ui_language'])
        
    def setup_ui(self):

        # --- Content Area ---
        # Card must be 'flex flex-col' so the child (textarea) can grow
        with ui.card().classes('w-full h-[75vh] p-0 flex flex-col'):
            
            # 1. Edit Mode: Text Area
            # We apply our custom 'full-height-textarea' class here
            self.textarea = ui.textarea(
                placeholder='Start typing your notes here...',
                value=self.text_content
            ).classes('w-full flex-grow full-height-textarea p-2 border-none focus:outline-none') \
             .props('flat squares resize-none') \
             .bind_visibility_from(self, 'is_editing')

            # 2. Read Mode: HTML Preview
            with ui.scroll_area().classes('w-full flex-grow p-2') \
                    .bind_visibility_from(self, 'is_editing', backward=lambda x: not x):
                self.html_view = ui.html(f'<div class="content-text">{self.text_content}</div>', sanitize=False).classes('w-full prose max-w-none')

    def toggle_mode(self):
        self.is_editing = not self.is_editing
        if not self.is_editing:
            self.update_preview()

    def update_preview(self):
        content = self.textarea.value or ''
        try:
            # Added your requested extras
            html_content = markdown2.markdown(
                content, 
                extras=["tables", "fenced-code-blocks", "toc", "cuddled-lists"]
            )
            html_content = self.parser.parseText(html_content)
            html_content = re.sub(r'''(onclick|ondblclick)="(bdbid|lex|cr|bcv|website)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', html_content)
            html_content = re.sub(r"""(onclick|ondblclick)='(bdbid|lex|cr|bcv|website)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", html_content)
            self.html_view.content = html_content
        except Exception as e:
            self.html_view.content = f"<p class='text-red-500'>Error: {str(e)}</p>"

    def download_file(self):
        content = self.textarea.value or ''
        if not content:
            ui.notify('Nothing to download!', type='warning')
            return
        ui.download(content.encode('utf-8'), 'biblemate_notes.md')
        ui.notify('Downloaded!', type='positive')
    
    async def handle_upload(self, e):
        try:
            content = await e.file.read()
            self.textarea.value = content.decode('utf-8')
            if not self.is_editing: self.update_preview()
            ui.notify('Loaded!', type='positive')
            self.upload.reset()
        except Exception as ex:
            ui.notify(f'Error: {str(ex)}', type='negative')
    
    def clear_text(self):
        self.textarea.value = ''
        self.html_view.content = ''
        ui.notify('Cleared!', type='info')

def notes(gui=None, bt=None, b=1, c=1, v=1, area=2, **_):
    if not bt:
        bt = gui.get_area_1_bible_text()
    elif bt in ("ORB", "OIB", "OPB", "ODB", "OLB"):
        bt = "OHGB"
    
    # Book Note
    if c == 0:
        v = 0

    # 1. Auth Check
    token = app.storage.user.get('google_token', "")
    if not token:
        with ui.card().classes('absolute-center'):
            ui.html('Sign in with Google to securely save and sync your personal Bible notes across all your devices.<br><i><b>Data Policy Note:</b> BibleMate AI does not collect or store your personal notes. Your notes are saved directly within your own Google Account.</i>', sanitize=False)
            with ui.row().classes('w-full justify-center'):
                ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
            with ui.expansion(get_translation("BibleMate AI Data Policy & Privacy Commitment"), icon='privacy_tip').props('header-class="text-secondary"'):
                ui.html("<b>We respect your privacy.</b> BibleMate AI is designed to protect your personal data. We do not collect, store, or share your personal Bible notes. When you log in with your Google Account, your notes are created and stored exclusively on <b>your personal Google Drive/Account</b>, ensuring that you retain full control and ownership of your private data at all times.", sanitize=False)
        return

    bible_selector = None
    service = get_drive_service(token)
    index_mgr = CloudIndexManager(service)
    notepad = CloudNotepad()

    def change_note(version=None, book=1, chapter=1, verse=1):
        nonlocal gui
        _, app.storage.user['tool_book_number'], app.storage.user['tool_chapter_number'], app.storage.user['tool_verse_number'] = version, book, chapter, verse
        gui.load_area_2_content(title='Notes', sync=False)
    bible_selector = BibleSelector(version_options=[bt], on_book_changed=change_note, on_chapter_changed=change_note, on_verse_changed=change_note, chapter_zero=True, verse_zero=True)

    def refresh_ui():
        try:
            nonlocal gui, b, c, v
            active_area1_tab = gui.get_active_area1_tab()
            if active_area1_tab in app.storage.user and app.storage.user[active_area1_tab]["b"] == b and app.storage.user[active_area1_tab]["c"] == c:
                gui.change_area_1_bible_chapter(book=b, chapter=c, verse=v)
        except:
            import traceback
            traceback.print_exc()

    def get_filename(verse_id):
        return f"{verse_id}.json"

    def get_vid(): 
        return f"{b}_{c}_{v}"

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

    def save_note_sync(service, verse_id, content, filename):
        """
        Performs the slow network calls to Google Drive.
        Running this on the main thread would freeze the app.
        """
        import json, io
        from googleapiclient.http import MediaIoBaseUpload
        
        # Prepare the file data
        file_data = {"verse_id": verse_id, "content": content}
        media = MediaIoBaseUpload(
            io.BytesIO(json.dumps(file_data).encode('utf-8')), 
            mimetype='application/json'
        )
        
        # 1. Search for existing file
        results = service.files().list(
            q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
            spaces='appDataFolder',
            fields='files(id)'
        ).execute()
        files = results.get('files', [])

        # 2. Update or Create
        if files:
            service.files().update(fileId=files[0]['id'], media_body=media).execute()
            return "updated"
        else:
            meta = {'name': filename, 'parents': ['appDataFolder']}
            service.files().create(body=meta, media_body=media).execute()
            return "created"

    async def save_current_note():
        # 1. Get Data
        vid = get_vid()
        content = notepad.textarea.value
        filename = get_filename(vid)
        
        # 2. Show Loading Spinner
        # (This prevents the user from clicking save twice)
        n = ui.notification('Saving to Cloud...', timeout=None, spinner=True)
        
        try:
            # 3. Run the heavy network call in a separate thread
            # 'service' is passed explicitly to be thread-safe
            result = await run.io_bound(
                save_note_sync, 
                service, 
                vid, 
                content, 
                filename
            )
            
            # 4. Update Index & UI (Back on the main thread)
            index_mgr.add_verse(vid)
            app.storage.user['cached_index'] = index_mgr.data
            
            n.dismiss()
            ui.notify('Saved successfully!', type='positive')
            refresh_ui()
            
        except Exception as e:
            n.dismiss()
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
                notepad.textarea.value = ""
                ui.notify('Note deleted.')
                refresh_ui()
            else:
                ui.notify('Nothing to delete.')
        except Exception as e:
            ui.notify(f"Delete error: {e}", type='negative')

    async def run_rebuild():
        # Run the rebuild
        n = ui.notification('Rebuilding search index...', timeout=None, spinner=True)
        count = await run.io_bound(index_mgr.rebuild_index)
        n.dismiss()
        if count >= 0:
            app.storage.user['cached_index'] = index_mgr.data # Update session
            refresh_ui() # Refresh stats
            ui.notify(f'Search index rebuilt! Found {count} notes.', type='positive')
        else:
            ui.notify('Rebuild failed. Check console logs.', type='negative')

    def download_index_backup():
        """Generates a downloadable JSON file of the current index."""
        if not index_mgr.data:
            ui.notify('Index is empty!', type='warning')
            return
        try:
            # 1. Convert index data to pretty JSON string
            json_str = json.dumps(index_mgr.data, indent=2)
            # 2. Encode it for the browser (Data URI format)
            encoded_json = urllib.parse.quote(json_str)
            # 3. Trigger download
            ui.download(f'data:application/json,{encoded_json}', 'bible_index_backup.json')
            ui.notify('Download started.')
        except Exception as e:
            ui.notify(f'Download error: {e}', type='negative')

    # ---------------------------------------------------------
    # Import a single json or a zip
    # ---------------------------------------------------------

    def process_import_sync(file_bytes, is_zip, drive_service):
        """
        Parses the uploaded bytes (Zip or JSON) and uploads them to Drive.
        Returns a list of successfully imported verse_ids.
        """
        imported_ids = []
        files_to_process = {} # {filename: json_content_dict}

        try:
            # A. Parse the Input (Zip or Single JSON)
            if is_zip:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    for filename in z.namelist():
                        if filename.endswith('.json') and filename != 'bible_index.json':
                            try:
                                content = z.read(filename)
                                data = json.loads(content)
                                files_to_process[filename] = data
                            except:
                                print(f"Skipping invalid file: {filename}")
            else:
                # Single JSON file
                try:
                    data = json.loads(file_bytes)
                    # Quick check if it's a note file
                    if 'verse_id' in data:
                        filename = f"{data['verse_id']}.json"
                        files_to_process[filename] = data
                except:
                    pass

            # B. Upload Loop
            # Note: This loops through every note. For 100+ notes, this takes time.
            for filename, data in files_to_process.items():
                verse_id = data.get('verse_id')
                if not verse_id: continue

                # Prepare content
                # We strictly re-dump the data to ensure clean JSON
                media = MediaIoBaseUpload(
                    io.BytesIO(json.dumps(data).encode('utf-8')), 
                    mimetype='application/json'
                )
                
                # 1. Check if file exists in Drive
                results = drive_service.files().list(
                    q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                    spaces='appDataFolder',
                    fields='files(id)'
                ).execute()
                existing_files = results.get('files', [])

                if existing_files:
                    # Update existing
                    file_id = existing_files[0]['id']
                    drive_service.files().update(fileId=file_id, media_body=media).execute()
                else:
                    # Create new
                    meta = {'name': filename, 'parents': ['appDataFolder']}
                    drive_service.files().create(body=meta, media_body=media).execute()
                
                imported_ids.append(verse_id)

        except Exception as e:
            print(f"Import process failed: {e}")
        
        return imported_ids

    async def handle_import(e):
        """
        UI Callback for the upload button.
        """
        #print(dir(e))
        # 1. Check login
        if not service:
            ui.notify('Please log in to Google first!', type='warning')
            return

        n = ui.notification('Processing Import... Please wait.', timeout=None, spinner=True)
        
        try:
            # 2. Read file bytes
            file_bytes = await e.file.read() 
            filename = getattr(e.file, 'name', 'unknown.json').lower()
            #print(filename)
            is_zip = filename.endswith('.zip')

            # Run background worker
            imported_ids = await run.io_bound(
                process_import_sync, 
                file_bytes, 
                is_zip, 
                service
            )

            # 4. Update Local Index
            if imported_ids:
                count = len(imported_ids)
                for vid in imported_ids:
                    index_mgr.add_verse(vid) # Updates local memory
                
                # Sync index to Drive once at the end
                index_mgr.save_to_drive() 
                app.storage.user['cached_index'] = index_mgr.data
                
                ui.notify(f'Successfully imported {count} notes!', type='positive')
                refresh_ui() # Update your stats/counters
                change_note(book=b, chapter=c, verse=v)
            else:
                ui.notify('No valid notes found to import.', type='warning')

        except Exception as err:
            ui.notify(f'Import failed: {err}', type='negative')
        finally:
            n.dismiss()

    # ---------------------------------------------------------
    # Download a single (the current) note
    # ---------------------------------------------------------
    
    def download_current_note():
        """
        Exports the currently visible note as a JSON file.
        This format is compatible with the 'Import' feature.
        """
        vid = get_vid() # Uses your existing helper
        content = notepad.textarea.value or ''
        
        if not content.strip():
            ui.notify('Cannot download an empty note.', type='warning')
            return

        try:
            # 1. Structure the data exactly like it is stored in Drive
            note_data = {
                "verse_id": vid,
                "content": content,
                "exported_at": "true" # Optional flag
            }
            
            # 2. Convert to JSON bytes
            json_str = json.dumps(note_data, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            # 3. Encode to Base64 (Safe for all browsers/characters)
            b64_str = base64.b64encode(json_bytes).decode()
            
            # 4. Trigger Download
            filename = f"{vid}.json"
            ui.download(f'data:application/json;base64,{b64_str}', filename)
            ui.notify(f'Downloaded {filename}')
            
        except Exception as e:
            ui.notify(f'Download error: {e}', type='negative')

    # ---------------------------------------------------------
    # 1. The Heavy Lifter (Download ALL)
    # ---------------------------------------------------------
    def generate_zip_sync(data, drive_service):
        """
        Synchronous function to download files and create zip.
        Note: We pass 'data' and 'drive_service' explicitly.
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add Index File
            zip_file.writestr('bible_index.json', json.dumps(data, indent=2))
            
            # Loop through notes
            for verse_id in data:
                try:
                    filename = f"{verse_id}.json" # Recreating get_filename logic here for safety
                    
                    # Search logic
                    results = drive_service.files().list(
                        q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                        spaces='appDataFolder',
                        fields='files(id)'
                    ).execute()
                    files = results.get('files', [])

                    if files:
                        file_id = files[0]['id']
                        request = drive_service.files().get_media(fileId=file_id)
                        file_content = request.execute()
                        zip_file.writestr(filename, file_content)
                except Exception as e:
                    print(f"Error zipping {verse_id}: {e}")

        # Finalize
        zip_buffer.seek(0)
        return base64.b64encode(zip_buffer.getvalue()).decode()

    # ---------------------------------------------------------
    # 2. The UI Function (Runs on main thread)
    # ---------------------------------------------------------
    async def download_all_notes_zip():
        if not index_mgr.data:
            ui.notify('No notes to download!', type='warning')
            return

        # 1. Show Spinner (Now it will actually render!)
        n = ui.notification('Downloading notes from Google Drive... Please wait.', timeout=None, spinner=True)
        
        try:
            # 2. Offload the heavy work to a background thread
            # This allows the UI to keep running while Python waits for the result
            b64_zip = await run.io_bound(generate_zip_sync, index_mgr.data, service)
            
            # 3. Trigger Download
            ui.download(f'data:application/zip;base64,{b64_zip}', 'biblemate_notes_backup.zip')
            
            n.dismiss()
            ui.notify('Download started!', type='positive')

        except Exception as e:
            n.dismiss()
            ui.notify(f'Zip error: {e}', type='negative')
    
    # Dialog to confirm deleting a note
    with ui.dialog() as delete_dialog, ui.card():
        ui.label('Are you sure you want to delete this note?')
        with ui.row().classes('justify-end w-full'):
            ui.button('Cancel', on_click=delete_dialog.close).props('flat text-color=secondary')
            ui.button('Delete', color='red', on_click=lambda: (delete_current_note(), delete_dialog.close()))

    # Bible Selection menu
    def additional_items():
        nonlocal gui, bible_selector, area
        with ui.button(icon='more_vert').props(f'flat round color={"white" if app.storage.user["dark_mode"] else "black"}'):
            with ui.menu():
                ui.menu_item(f'👁️ {get_translation("Read")} / {get_translation("Edit")}', on_click=notepad.toggle_mode)
                ui.separator()
                ui.menu_item(f'💾 {get_translation("Save")}', on_click=save_current_note)
                ui.menu_item(f'❌ {get_translation("Delete")}', on_click=delete_dialog.open)
                ui.menu_item(f'📥 {get_translation("Download")}', on_click=download_current_note)
                ui.menu_item(f'📥 {get_translation("Download All")}', on_click=download_all_notes_zip)
                ui.separator()
                with ui.menu_item(f'📤 {get_translation("Import")}', on_click=lambda: upload_element.run_method('pickFiles')):
                    ui.tooltip('Import a single note (*.json file) or a zip file containing multiple notes.')
                ui.separator()
                with ui.menu_item(f'🛠️ {get_translation("Rebuild Index")}', on_click=run_rebuild):
                    ui.tooltip('Rebuild search index for maintenance or repair.')
                ui.menu_item(f'📥 {get_translation("Download Index")}', on_click=download_index_backup)
                ui.separator()
                with ui.menu_item(f'🔒 {get_translation("Logout")}', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))):
                    ui.tooltip('Log out to keep your account secure, especially on shared devices.')
    bible_selector.create_ui(bt, b, c, v, additional_items=additional_items, show_versions=False)

    upload_element = ui.upload(
        on_upload=handle_import, 
        auto_upload=True
    ).props('accept=.json,.zip').classes('hidden')

    notepad.setup_ui()
    def load_initial_content():
        notepad.textarea.value = load_current_note()
    ui.timer(0, lambda: loading(load_initial_content), once=True)


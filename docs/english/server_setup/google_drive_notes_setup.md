1. Go to the [Google Cloud Console](https://console.cloud.google.com/).

2. Create a project (e.g., "BibleMate AI").

3. Enable API: Search for and enable the Google Drive API.

4. OAuth Consent Screen: Configure it (User Type: External). Add your email as a test user.

5. Credentials: Create "OAuth 2.0 Client IDs".

6. Type: Web Application.

7. Add redirect URIs: http://localhost:33355/auth & http://127.0.0.1:33355/auth (Adjust port if needed).

8. Scopes: You need https://www.googleapis.com/auth/drive.appdata (access to hidden app folder only) or drive.file (access to files created by the app).
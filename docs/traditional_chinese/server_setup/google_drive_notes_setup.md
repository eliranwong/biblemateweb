1. 前往 [Google Cloud Console](https://console.cloud.google.com/)。

2. 建立專案（例如："BibleMate AI"）。

3. 啟用 API：搜尋並啟用 Google Drive API。

4. OAuth 同意畫面：進行配置（使用者類型：外部）。新增您的電子郵件作為測試使用者。

5. 憑證：建立「OAuth 2.0 用戶端 ID」。

6. 類型：網路應用程式（Web Application）。

7. 新增重新導向 URI：http://localhost:33355/auth 與 http://127.0.0.1:33355/auth（如有需要請調整連接埠）。

8. 範圍（Scopes）：您需要 https://www.googleapis.com/auth/drive.appdata（僅存取隱藏的應用程式資料夾）或 drive.file（存取由應用程式建立的檔案）。

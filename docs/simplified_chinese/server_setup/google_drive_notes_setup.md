1. 前往 [Google Cloud Console](https://console.cloud.google.com/)。

2. 创建项目（例如："BibleMate AI"）。

3. 启用 API：搜索并启用 Google Drive API。

4. OAuth 同意屏幕：进行配置（用户类型：外部）。添加您的电子邮件作为测试用户。

5. 凭据：创建“OAuth 2.0 客户端 ID”。

6. 类型：Web 应用程序（Web Application）。

7. 添加重定向 URI：http://localhost:33355/auth 与 http://127.0.0.1:33355/auth（如有需要请调整端口）。

8. 范围（Scopes）：您需要 https://www.googleapis.com/auth/drive.appdata（仅访问隐藏的应用程序文件夹）或 drive.file（访问由应用程序创建的文件）。

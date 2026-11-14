# Google 登录 (google_token)

这不是供您直接编辑的设置：此键用于保存您通过 Google 登录（`/login` → `/auth`）时创建的令牌（Token）。它支持 [Google Drive 笔记](../integrations/google_drive_notes.md) 以及跟踪每位用户的每日配额限制（[使用限制](../ai_features/usage_limits.md)）。

- 仅保存在您的浏览器存储空间中。
- 可通过 `重置所有偏好设定` 清除（请参阅 [用户数据与存储](user_data_and_storage.md)）。
- 需要管理员配置 `config.google_client_id` 与 `config.google_client_secret`（请参阅 [设置指南](../server_setup/google_drive_notes_setup.md)）。

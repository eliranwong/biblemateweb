# Google 登入 (google_token)

這不是供您直接編輯的設定：此鍵用於保存您透過 Google 登入（`/login` → `/auth`）時建立的權杖（Token）。它支援 [Google Drive 筆記](../integrations/google_drive_notes.md) 以及追蹤每位使用者的每日配額限制（[使用限制](../ai_features/usage_limits.md)）。

- 僅保存在您的瀏覽器儲存空間中。
- 可透過 `重置所有偏好設定` 清除（請參閱 [使用者數據與儲存](user_data_and_storage.md)）。
- 需要管理員配置 `config.google_client_id` 與 `config.google_client_secret`（請參閱 [設定指南](../server_setup/google_drive_notes_setup.md)）。

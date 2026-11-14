# 安全與部署

## 公開伺服器安全檢查清單

- 設定安全的 `config.storage_secret`。
- 使用反向代理（Nginx、Apache、Caddy）透過 HTTPS 提供服務。
- 限制代理模式 / 夥伴模式（`config.disable_*`、`config.limit_*_once_daily`）– 請參閱[使用限制](../ai_features/usage_limits.md)。
- 保持 `config.disable_local_api_endpoint=True`，以阻止透過使用者提供的本地 API 端點引發的 SSRF 攻擊。
- 設定 `config.verses_limit` 以防止過量經文查詢。
- 限制 Google OAuth 重新導向 URI（[設定指南](google_drive_notes_setup.md)）。
- 使用 `config.custom_token` 保護私有資源。

## 數據隱私

伺服器不存儲任何使用者帳號。偏好設定儲存在瀏覽器中（[使用者數據與存儲](../user_preferences/user_data_and_storage.md)）；筆記存放在使用者本人的 Google Drive 中。

## 託管選項

使用行程管理工具獨立運行（[啟動與運行伺服器](running_the_server.md)）、反向代理或雲端託管。請參閱 [NiceGUI 部署指南](https://nicegui.io/documentation/section_configuration_deployment#server_hosting)。

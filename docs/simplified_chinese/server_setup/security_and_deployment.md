# 安全与部署

## 公开服务器安全检查清单

- 设置安全的 `config.storage_secret`。
- 使用反向代理（Nginx、Apache、Caddy）通过 HTTPS 提供服务。
- 限制代理模式 / 伙伴模式（`config.disable_*`、`config.limit_*_once_daily`）– 请参阅[使用限制](../ai_features/usage_limits.md)。
- 保持 `config.disable_local_api_endpoint=True`，以阻止通过用户提供的本地 API 端点引发的 SSRF 攻击。
- 设置 `config.verses_limit` 以防止过量经文查询。
- 限制 Google OAuth 重定向 URI（[设定指南](google_drive_notes_setup.md)）。
- 使用 `config.custom_token` 保护私有资源。

## 数据隐私

服务器不存储任何用户账号。偏好设定保存在浏览器中（[用户数据与存储](../user_preferences/user_data_and_storage.md)）；笔记保存在用户本人的 Google Drive 中。

## 托管选项

使用进程管理工具独立运行（[启动与运行服务器](running_the_server.md)）、反向代理或云端托管。请参阅 [NiceGUI 部署指南](https://nicegui.io/documentation/section_configuration_deployment#server_hosting)。

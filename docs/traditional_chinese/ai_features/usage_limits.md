# 使用限制與可用性

管理員可透過伺服器組態檔案（`~/biblemate/biblemateweb.config`；請參閱[配置設定指南](../server_setup/configuration.md)）控制對運算負擔較重之 AI 模式的存取。

| 設定 | 效果 |
|---|---|
| `config.disable_agent_mode` | 代理模式顯示僅限 CLI 的說明資訊頁面 |
| `config.disable_partner_mode` | 夥伴模式顯示僅限 CLI 的說明資訊頁面 |
| `config.limit_agent_mode_once_daily` | 代理模式限制為每日一次 |
| `config.limit_partner_mode_once_daily` | 夥伴模式限制為每日一次 |

## 解除限制

- 若您輸入自己的 API 金鑰，被停用的模式即可恢復使用。
- 若您擁有有效的[自訂 Token](../user_preferences/custom_token.md)或自己的 [API 金鑰](../user_preferences/api_key.md)，則不受每日限制約束。

當套用每日限制時，系統可能會要求您使用 Google 帳號登入以便記錄使用次數；您的資料會保留在您自己的 Google 帳戶中。一旦達到限制上限，系統會顯示訊息說明如何透過「偏好設定」解除該限制。

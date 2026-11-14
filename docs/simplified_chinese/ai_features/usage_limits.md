# 使用限制与可用性

管理员可通过服务器配置文件（`~/biblemate/biblemateweb.config`；请参阅[配置设定指南](../server_setup/configuration.md)）控制对运算负担较重之 AI 模式的访问。

| 设定 | 效果 |
|---|---|
| `config.disable_agent_mode` | 代理模式显示仅限 CLI 的说明信息页面 |
| `config.disable_partner_mode` | 伙伴模式显示仅限 CLI 的说明信息页面 |
| `config.limit_agent_mode_once_daily` | 代理模式限制为每日一次 |
| `config.limit_partner_mode_once_daily` | 伙伴模式限制为每日一次 |

## 解除限制

- 若您输入自己的 API 密钥，被禁用的模式即可恢复使用。
- 若您拥有有效的[自定义 Token](../user_preferences/custom_token.md)或自己的 [API 密钥](../user_preferences/api_key.md)，则不受每日限制约束。

当应用每日限制时，系统可能会要求您使用 Google 账号登录以便记录使用次数；您的数据会保留在您自己的 Google 账户中。一旦达到限制上限，系统会显示信息说明如何通过“偏好设定”解除该限制。

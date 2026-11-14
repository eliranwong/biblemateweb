# AI 后端

决定由哪项 AI 服务来回复您的请求。

## 选项

1. **服务器默认** – 管理员配置的后端。当“AI 后端”设为 `default` 或未设置 API 密钥时使用。
2. **自备密钥 (BYOK)** – 选择提供商（`googleai`、`openai`、`anthropic`、`cohere`、`deepseek`、`mistral`、`xai`、Azure 变体、`ollamacloud`、`custom`），然后输入模型、端点与密钥。请参阅[自备密钥 (BYOK)](../user_preferences/api_key_setup.md)。
3. **订阅型 CLI** – 若管理员已启用（`show_grok_build`、`show_claude_code`、`show_antigravity`），您可以选择 `grok`、`claude` 或 `antigravity`。它们使用服务器上已登录的 CLI 会话，无需密钥。

## 所使用的偏好设定

[AI 后端](../user_preferences/ai_backend.md)、[AI 模型](../user_preferences/ai_model.md)、[API 端点](../user_preferences/api_endpoint.md)、[API 密钥](../user_preferences/api_key.md)、[最大 Token 数](../user_preferences/max_tokens.md)、[温度值](../user_preferences/temperature.md)。

> [!NOTE]
> 只有当您已输入 API 密钥且后端非 `default` 时，自定义的模型、端点、Token 上限和温度值才会生效。

# AI 後端

決定由哪項 AI 服務來回覆您的請求。

## 選項

1. **伺服器預設** – 管理員設定的後端。當「AI 後端」設為 `default` 或未設定 API 金鑰時使用。
2. **自備金鑰 (BYOK)** – 選擇提供者（`googleai`、`openai`、`anthropic`、`cohere`、`deepseek`、`mistral`、`xai`、Azure 變體、`ollamacloud`、`custom`），然後輸入模型、端點與金鑰。請參閱[自備金鑰 (BYOK)](../user_preferences/api_key_setup.md)。
3. **訂閱型 CLI** – 若管理員已啟用（`show_grok_build`、`show_claude_code`、`show_antigravity`），您可以選擇 `grok`、`claude` 或 `antigravity`。它們使用伺服器上已登入的 CLI 工作階段，無需金鑰。

## 所使用的偏好設定

[AI 後端](../user_preferences/ai_backend.md)、[AI 模型](../user_preferences/ai_model.md)、[API 端點](../user_preferences/api_endpoint.md)、[API 金鑰](../user_preferences/api_key.md)、[最大 Token 數](../user_preferences/max_tokens.md)、[溫度值](../user_preferences/temperature.md)。

> [!NOTE]
> 只有當您已輸入 API 金鑰且後端非 `default` 時，自訂的模型、端點、Token 上限和溫度值才會生效。

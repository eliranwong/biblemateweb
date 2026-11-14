# AI Backends

Which AI service answers your requests.

## Options

1. **Server default** – the backend the administrator configured. Used when AI Backend is `default` or no API key is set.
2. **Your own key (BYOK)** – choose a provider (`googleai`, `openai`, `anthropic`, `cohere`, `deepseek`, `mistral`, `xai`, Azure variants, `ollamacloud`, `custom`), then enter model, endpoint and key. See [BYOK](../user_preferences/api_key_setup.md).
3. **Subscription CLIs** – if enabled by the administrator (`show_grok_build`, `show_claude_code`, `show_antigravity`), you can pick `grok`, `claude` or `antigravity`. They use the server's signed-in CLI session and need no key.

## Preferences used

[AI Backend](../user_preferences/ai_backend.md), [AI Model](../user_preferences/ai_model.md), [API Endpoint](../user_preferences/api_endpoint.md), [API Key](../user_preferences/api_key.md), [Max Tokens](../user_preferences/max_tokens.md), [Temperature](../user_preferences/temperature.md).

> [!NOTE]
> Your custom model, endpoint, token limit and temperature are applied only when you have entered an API key and the backend is not `default`.

```
model = "gpt-6.1-sol"
model_provider = "azure"
model_reasoning_effort = "high"
sandbox_mode = "danger-full-access"
approval_policy = "never"
web_search = "live"

[model_providers.azure]
name = "Azure OpenAI"
base_url = "https://<project_name>.openai.azure.com/openai/v1"
experimental_bearer_token = "<token>"
#env_key = "AZURE_OPENAI_API_KEY"
wire_api = "responses"

[sandbox_workspace_write]
network_access = true

[projects."/tmp/codex-research"]
trust_level = "trusted"

[projects."/tmp/macro-codex"]
trust_level = "trusted"

[projects."/tmp/intl-scan"]
trust_level = "trusted"

[projects."/tmp"]
trust_level = "trusted"

[tui]
screen_reader_detection_done = true

[notice.model_migrations]
"gpt-5.3-codex" = "gpt-5.4"
"gpt-5.5" = "gpt-6-sol"
```
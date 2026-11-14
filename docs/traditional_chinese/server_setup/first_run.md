# 首次執行

1. **Storage secret（存儲密鑰）** – 對於超出本機測試的任何使用場景，請生成一個密鑰並填入 `~/biblemate/biblemateweb.config`：
   ```bash
   openssl rand -hex 32
   ```
   ```python
   config.storage_secret="your-generated-secret"
   ```
   它用於保護每位使用者的瀏覽器存儲（詳見[安全設定](security_and_deployment.md)）。
2. **AI 後端**（選用）– 管理員可設定 `config.ai_backend`；使用者亦可在[偏好設定](../user_preferences/README.md)中使用自有金鑰（[BYOK](../user_preferences/api_key_setup.md)）。
3. **通訊埠 / 頭像** – `config.port`（預設為 33355）、`config.avatar`。
4. 編輯設定後**重新啟動**。
5. 開啟 <http://localhost:33355> 並依循[基礎教學指南](../basics/README.md)。

所有選項詳解：[配置設定指南](configuration.md)。

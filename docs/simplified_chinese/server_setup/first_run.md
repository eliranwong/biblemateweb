# 首次运行

1. **Storage secret（存储密钥）** – 对于超出本地测试的任何使用场景，请生成一个密钥并填入 `~/biblemate/biblemateweb.config`：
   ```bash
   openssl rand -hex 32
   ```
   ```python
   config.storage_secret="your-generated-secret"
   ```
   它用于保护每位用户的浏览器存储（详见[安全设定](security_and_deployment.md)）。
2. **AI 后端**（可选）– 管理员可设定 `config.ai_backend`；用户亦可在[偏好设定](../user_preferences/README.md)中使用自有密钥（[BYOK](../user_preferences/api_key_setup.md)）。
3. **端口 / 头像** – `config.port`（默认为 33355）、`config.avatar`。
4. 编辑设定后**重启**。
5. 打开 <http://localhost:33355> 并遵循[基础教程指南](../basics/README.md)。

所有选项详解：[配置设定指南](configuration.md)。

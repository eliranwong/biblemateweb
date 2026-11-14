# 故障排除

| 问题 | 排查步骤 |
|---|---|
| 没有圣经或选单为空 | 运行 `biblematedata`；检查 `~/biblemate/data` 中的文件（[数据与资源](data_and_resources.md)） |
| 语义搜索失败 | 检查 [Ollama 设定](semantic_search_setup.md)、模型是否已拉取、向量数据是否存在 |
| DOCX 下载失败 | 安装 `pandoc`（[指南](docx_export.md)） |
| Google 登录失败 | 检查重定向 URI 与 `config.auth_uri`（[设定指南](google_drive_notes_setup.md)） |
| 代理模式 / 伙伴模式显示仅限 CLI 页面 | `config.disable_*` 已设定；请输入您自带的 API 密钥（[使用限制](../ai_features/usage_limits.md)） |
| AI 未给出回答 | 检查 [AI 后端、密钥与模型](../ai_features/ai_backends.md) |
| 设定变更未生效 | 重启服务器 |
| 显示异常或状态卡住 | 使用“重置所有偏好设定”（[用户数据与存储](../user_preferences/user_data_and_storage.md)） |
| 自定义圣经未显示 | 输入[自定义 Token](../user_preferences/custom_token.md) |
| 端口已被占用 | 修改 `config.port` 或停止其他进程 |
| 本地可正常运作，远程无法访问 | 检查防火墙 / 反向代理设定；Google OAuth 重定向 |

# 故障排除

| 問題 | 排查步驟 |
|---|---|
| 沒有聖經或選單為空 | 執行 `biblematedata`；檢查 `~/biblemate/data` 中的檔案（[數據與資源](data_and_resources.md)） |
| 語義搜索失敗 | 檢查 [Ollama 設定](semantic_search_setup.md)、模型是否已下載、向量數據是否存在 |
| DOCX 下載失敗 | 安裝 `pandoc`（[指南](docx_export.md)） |
| Google 登入失敗 | 檢查重新導向 URI 與 `config.auth_uri`（[設定指南](google_drive_notes_setup.md)） |
| 代理模式 / 夥伴模式顯示僅限 CLI 頁面 | `config.disable_*` 已設定；請輸入您自備的 API 金鑰（[使用限制](../ai_features/usage_limits.md)） |
| AI 未給出回答 | 檢查 [AI 後端、金鑰與模型](../ai_features/ai_backends.md) |
| 設定變更未生效 | 重新啟動伺服器 |
| 顯示異常或狀態卡住 | 使用「重置所有偏好設定」（[使用者數據與存儲](../user_preferences/user_data_and_storage.md)） |
| 自訂聖經未顯示 | 輸入[自訂 Token](../user_preferences/custom_token.md) |
| 通訊埠已被佔用 | 修改 `config.port` 或停止其他行程 |
| 本機可正常運作，遠端無法存取 | 檢查防火牆 / 反向代理設定；Google OAuth 重新導向 |

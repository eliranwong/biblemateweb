# 路由與端點

| 路由 | 類型 | 描述 |
|---|---|---|
| `/` | 頁面 | 主應用程式。接受 [URL 參數](../layout/url_parameters.md) |
| `/settings` | 頁面 | [偏好設定](../user_preferences/README.md)。接受 `t`（本次造訪的自訂權杖） |
| `/login` | 頁面 | 啟動 Google 登入（用於[雲端筆記](../integrations/google_drive_notes.md)與配額限制） |
| `/auth` | 頁面 | Google OAuth 回呼；將權杖儲存於瀏覽器工作階段中並返回 `/` |
| `/api/data` | REST | 查詢聖經數據 —— [REST API](../integrations/rest_api.md)、[API 查詢語法](api_query.md) |
| `/api/tooltip/{word}` | REST | 單詞提示數據 —— [單詞提示](../integrations/word_tooltips.md) |

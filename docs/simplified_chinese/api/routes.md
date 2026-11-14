# 路由与端点

| 路由 | 类型 | 描述 |
|---|---|---|
| `/` | 页面 | 主应用程序。接受 [URL 参数](../layout/url_parameters.md) |
| `/settings` | 页面 | [偏好设定](../user_preferences/README.md)。接受 `t`（本次访问的自定义令牌） |
| `/login` | 页面 | 启动 Google 登录（用于[云端笔记](../integrations/google_drive_notes.md)与配额限制） |
| `/auth` | 页面 | Google OAuth 回调；将令牌存储在浏览器会话中并返回 `/` |
| `/api/data` | REST | 查询圣经数据 —— [REST API](../integrations/rest_api.md)、[API 查询语法](api_query.md) |
| `/api/tooltip/{word}` | REST | 单词提示数据 —— [单词提示](../integrations/word_tooltips.md) |

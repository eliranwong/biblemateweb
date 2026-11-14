# REST API

## `GET /api/data`

| 參數 | 描述 |
|---|---|
| `query` | 必要：`keyword:::options`，例如 `verses:::John 3:16` |
| `language` | `eng`（預設）、`tc`、`sc` |
| `token` | 用於自定資源的選用自定權杖 (token) |

回傳 JSON：`{"query", "custom", "content"}`，其中 `content` 包含 Markdown。

```bash
curl "http://localhost:33355/api/data?query=verses:::John%203:16&language=eng"
```

## 關鍵字

`morphology`、`chapter`、`comparechapter`、`verses`、`literal`、`regex`、`semantic`、`treasury`、`commentary`、`chronology`、`xrefs`、`promises`、`parallels`、`topics`、`characters`、`locations`、`names`、`dictionaries`、`encyclopedias`、`lexicons`。保留字：`.help`、`.resources`。

完整語法：[API 查詢](../api/api_query.md)。

## `GET /api/tooltip/{word}`

回傳[單詞提示框](word_tooltips.md)所使用的提示框數據（詞彙、形態學或筆記）。

> [!NOTE]
> 同一個查詢引擎同時支援網頁使用者介面、AI 工具以及 [API 用戶端](api_client_cli.md)。

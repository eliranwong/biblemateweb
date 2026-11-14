# REST API

## `GET /api/data`

| 参数 | 描述 |
|---|---|
| `query` | 必需：`keyword:::options`，例如 `verses:::John 3:16` |
| `language` | `eng`（默认）、`tc`、`sc` |
| `token` | 用于自定义资源的选用自定义令牌 (token) |

返回 JSON：`{"query", "custom", "content"}`，其中 `content` 包含 Markdown。

```bash
curl "http://localhost:33355/api/data?query=verses:::John%203:16&language=eng"
```

## 关键字

`morphology`、`chapter`、`comparechapter`、`verses`、`literal`、`regex`、`semantic`、`treasury`、`commentary`、`chronology`、`xrefs`、`promises`、`parallels`、`topics`、`characters`、`locations`、`names`、`dictionaries`、`encyclopedias`、`lexicons`。保留字：`.help`、`.resources`。

完整语法：[API 查询](../api/api_query.md)。

## `GET /api/tooltip/{word}`

返回[单词提示框](word_tooltips.md)所使用的提示框数据（词汇、形态学或笔记）。

> [!NOTE]
> 同一个查询引擎同时驱动网页用户界面、AI 工具以及 [API 客户端](api_client_cli.md)。

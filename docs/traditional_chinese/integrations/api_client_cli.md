# API 客戶端 (CLI)

`biblemateapi` 命令用於查詢正在運行的伺服器。

```bash
biblemateapi -h
biblemateapi "verses:::John 3:16"
biblemateapi "chapter:::KJV:::Genesis 1"
biblemateapi "semantic:::love of God"
```

| 選項 | 說明 |
|---|---|
| `-l`, `--language` | `eng`、`tc`、`sc` |
| `-t`, `--token` | 自訂權杖 |
| `-u`, `--url` | 伺服器網址（預設為 `http://localhost:33355/api/data`） |

環境變數：`BM_API_ENDPOINT`、`BM_API_CUSTOM_KEY`。在沒有查詢參數時會輸出 `.help`。輸出內容為渲染後的 Markdown。請參閱 [REST API](rest_api.md)。

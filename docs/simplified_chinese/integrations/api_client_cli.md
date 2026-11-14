# API 客户端 (CLI)

`biblemateapi` 命令用于查询正在运行的服务器。

```bash
biblemateapi -h
biblemateapi "verses:::John 3:16"
biblemateapi "chapter:::KJV:::Genesis 1"
biblemateapi "semantic:::love of God"
```

| 选项 | 说明 |
|---|---|
| `-l`, `--language` | `eng`、`tc`、`sc` |
| `-t`, `--token` | 自定义令牌 |
| `-u`, `--url` | 服务器网址（默认为 `http://localhost:33355/api/data`） |

环境变量：`BM_API_ENDPOINT`、`BM_API_CUSTOM_KEY`。在没有查询参数时会输出 `.help`。输出内容为渲染后的 Markdown。请参阅 [REST API](rest_api.md)。

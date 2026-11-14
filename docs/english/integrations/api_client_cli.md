# API Client (CLI)

The `biblemateapi` command queries a running server.

```bash
biblemateapi -h
biblemateapi "verses:::John 3:16"
biblemateapi "chapter:::KJV:::Genesis 1"
biblemateapi "semantic:::love of God"
```

| Option | Description |
|---|---|
| `-l`, `--language` | `eng`, `tc`, `sc` |
| `-t`, `--token` | Custom token |
| `-u`, `--url` | Server URL (default `http://localhost:33355/api/data`) |

Environment variables: `BM_API_ENDPOINT`, `BM_API_CUSTOM_KEY`. With no query it prints `.help`. Output is rendered Markdown. See [REST API](rest_api.md).

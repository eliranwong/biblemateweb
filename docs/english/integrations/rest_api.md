# REST API

## `GET /api/data`

| Parameter | Description |
|---|---|
| `query` | Required: `keyword:::options`, e.g. `verses:::John 3:16` |
| `language` | `eng` (default), `tc`, `sc` |
| `token` | Optional custom token for custom resources |

Returns JSON: `{"query", "custom", "content"}` with Markdown in `content`.

```bash
curl "http://localhost:33355/api/data?query=verses:::John%203:16&language=eng"
```

## Keywords

`morphology`, `chapter`, `comparechapter`, `verses`, `literal`, `regex`, `semantic`, `treasury`, `commentary`, `chronology`, `xrefs`, `promises`, `parallels`, `topics`, `characters`, `locations`, `names`, `dictionaries`, `encyclopedias`, `lexicons`. Reserved: `.help`, `.resources`.

Full syntax: [API Query](../api/api_query.md).

## `GET /api/tooltip/{word}`

Returns tooltip data (lexical, morphology or note) used by [word tooltips](word_tooltips.md).

> [!NOTE]
> The same query engine powers the web UI, the AI tools and the [API client](api_client_cli.md).

# Enhance (Prompt Engineering)

Automatically rewrites your request into a clearer, more precise prompt before it is answered.

| | |
|---|---|
| Where | `Enhance` checkbox in Chat, Partner and Agent modes |
| Key | `prompt_engineering` |
| Default | On |

## How it works

1. You send a request.
2. A **Prompt Engineering** panel streams the improved prompt.
3. With [Review](chat_review.md) on (Chat mode), you can edit the improved prompt before it continues.
4. The improved prompt is then used for the rest of the pipeline. The panel collapses when finished.

If the improvement fails or returns nothing, the process stops and you can try again.

Turn it off for quick, direct questions or when you want your exact wording used.

# Agent Mode

An autonomous mode: describe a complex Bible task and the AI plans, selects tools and runs multiple rounds on its own, then writes a final report.

## Open

**AI** menu → `Agent Mode`. Some servers disable the web version and show a page pointing to the [BibleMate CLI](https://github.com/eliranwong/biblemate) instead ([availability](usage_limits.md)).

## Workflow

1. **Request** – optionally improved by [Enhance](prompt_engineering.md).
2. **Study Plan** – a master plan is generated.
3. **Rounds** – each round shows a Suggestion, Tool Selection (the first suggested tool is used automatically), Tool Instruction, the output, and Progress. Rounds repeat until the AI decides it is finished.
4. **Final Report** – a combined answer.

## Controls

`Edit Request`, `Edit Plan`, `Edit Rounds`, `Trim Rounds`, `Resume`; **Stop** to interrupt.

## Downloading

Copy, TXT, DOCX per output; `Download the whole Conversation`; `Download the Final Report Only`.

## Daily limit

Administrators can limit Agent Mode to once a day for users without their own key – see [Usage Limits](usage_limits.md).

For step-by-step control use [Partner Mode](partner_mode.md).

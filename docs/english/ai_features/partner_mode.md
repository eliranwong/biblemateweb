# Partner Mode

A collaborative mode for complex, multi-step Bible study. The AI plans and works through steps, but **you stay in control**: you can review and refine the plan, approve tools and edit the instructions for each step.

## Open

**AI** menu → `Partner Mode`. (See [availability](usage_limits.md) – some servers offer only the CLI version.)

## Workflow

1. **Request** – describe what to study (optionally improved by [Enhance](prompt_engineering.md)).
2. **Study Plan** – the AI drafts a master plan. You can review and edit it.
3. **Rounds** – for each round the AI:
   - gives a **Suggestion** for the next step,
   - proposes tools (**Tool Selection**); you pick from the list or choose `More...` for all tools,
   - writes a **Tool Instruction** you can edit,
   - runs the tool or generates content, with a **Progress** note after each round.
4. **Final Report** – a comprehensive report of everything completed.

## Controls after a run

`Edit Request`, `Edit Plan`, `Edit Rounds`, `Trim Rounds` (drop rounds from a chosen point), `Resume` (continue after a stop).

## Downloading

Copy, TXT and DOCX for each output, plus `Download the whole Conversation` and `Download the Final Report Only`.

## Compared with other modes

| | Chat | Partner | Agent |
|---|---|---|---|
| Multi-step plan | No | Yes | Yes |
| You approve tools/instructions | Optional (Review) | Yes | No |

See [Agent Mode](agent_mode.md) and [Chat Mode](chat_mode.md).

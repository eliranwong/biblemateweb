# Toggle Layout

BibleMate has three layout modes. The current mode is remembered in your user storage (`layout`, default `2`).

| Mode | Value | Result |
|---|---|---|
| Bible Only | `1` | Only the Bible Area is shown (splitter at 100%) |
| Bible & Tool | `2` | Both areas shown, split 50/50 |
| Tool Only | `3` | Only the Tool Area is shown (splitter at 0%) |

## Ways to change layout

1. **Swap Layout floating button** (`swap_horiz` icon). Each click cycles `1 → 2 → 3 → 1`. See [Floating Buttons](floating_buttons.md).
2. **Settings menu** (gear icon in the header): choose `Bible Only`, `Tool Only` or `Bible & Tool` directly.
3. **URL parameter** `l=1|2|3`, e.g. `/?l=1`. See [URL Parameters](url_parameters.md).

## Automatic switching

- Loading content into the Bible Area while in **Tool Only** mode switches to **Bible & Tool**.
- Loading content into the Tool Area while in **Bible Only** mode switches to **Bible & Tool**.

So choosing a tool or a Bible from a menu always makes its window visible.

## Tips

- On a phone, use `Bible Only` for reading and `Tool Only` for studying with maximum space.
- You can also drag the splitter manually between the two areas.

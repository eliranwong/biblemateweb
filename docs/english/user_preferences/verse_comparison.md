# Verse Comparison

Controls which Bible versions are opened when triggering **Comparison** from the verse context menu or the **Verse Tools** row in Verse Indexes.

- **Where**: `Preferences` → `Frequently Used Resources` → `Verse Comparison`
- **Storage keys**:
  - `verse_comparison_mode`: `'default'` (default) or `'custom'`
  - `verse_comparison_bibles`: list of selected Bible abbreviations (e.g. `['NET', 'KJV', 'CUV', 'OHGBi']`)

## Behavior

- **Default**: Compares your `Primary Bible`, the active/clicked Bible version, and `OHGBi`.
- **Custom**: Opens a multi-select chip dropdown (`Comparison Versions`) where you can choose your preferred versions. If no versions are selected, it falls back to `Default`.

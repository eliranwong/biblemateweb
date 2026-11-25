# Chapter Comparison

Controls which Bible versions are opened when triggering **Compare Chapter** from the chapter context menu.

- **Where**: `Preferences` → `Frequently Used Resources` → `Chapter Comparison`
- **Storage keys**:
  - `chapter_comparison_mode`: `'default'` (default) or `'custom'`
  - `chapter_comparison_bibles`: list of selected Bible abbreviations (e.g. `['NET', 'KJV', 'CUV', 'OHGBi']`)

## Behavior

- **Default**: Compares the active Bible version first, followed by your `Primary Bible`, `Secondary Bible`, and `OHGBi` (deduplicated).
- **Custom**: Opens a multi-select chip dropdown (`Comparison Versions`) where you can choose your preferred versions. When opened from a specific Bible version, that version is placed first ahead of your selected list. If no versions are selected, it falls back to `Default`.

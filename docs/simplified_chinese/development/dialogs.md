# 可复用对话框

位于 `dialogs/`：

| 对话框 | 用途 |
|---|---|
| `ReviewDialog` | 编辑文本：`await ReviewDialog().open_with_text(text, label="Edit")` 返回编辑后的文本，若取消则返回 `None` |
| `SelectionDialog(big=False)` | 选择单一选项：`await SelectionDialog().open_with_options(options, title)` 返回所选选项，若取消则返回 `None` |
| `FilenameDialog` | `await FilenameDialog().open_with_filename("name")` 返回文件名 |

此外还有 `fx/bible_selection_dialog.py`：位于 [“开启”按钮](../layout/bible_selection_dialog.md) 背后的书卷／篇章／经节选择器。

用户视角：[审查](../ai_features/chat_review.md)、[伙伴模式](../ai_features/partner_mode.md)。

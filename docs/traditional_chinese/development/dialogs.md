# 可重複使用對話框

位於 `dialogs/`：

| 對話框 | 用途 |
|---|---|
| `ReviewDialog` | 編輯文字：`await ReviewDialog().open_with_text(text, label="Edit")` 回傳編輯後的文字，若取消則回傳 `None` |
| `SelectionDialog(big=False)` | 選擇單一選項：`await SelectionDialog().open_with_options(options, title)` 回傳所選項目，若取消則回傳 `None` |
| `FilenameDialog` | `await FilenameDialog().open_with_filename("name")` 回傳檔案名稱 |

此外還有 `fx/bible_selection_dialog.py`：位於 [「開啓」按鈕](../layout/bible_selection_dialog.md) 背後的書卷／篇章／經節選擇器。

使用者視角：[審查](../ai_features/chat_review.md)、[夥伴模式](../ai_features/partner_mode.md)。

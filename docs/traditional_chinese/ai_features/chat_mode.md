# 對話模式

針對聖經相關問題的對話式助手：涵蓋經文、歷史背景、專題探討等豐富內容。

## 開啟

- **AI** 選單 → `對話模式`
- 右鍵點擊經文或章節 → `問 BibleMate`（[指南](ask_biblemate.md)），即可自動預填您的問題。

## 使用方法

1. 在文字方塊中輸入您的需求。
2. 點擊 **發送** 或按下 **Ctrl+S**（macOS 為 **Cmd+S**）。
3. 回答會以格式化文字的形式即時串流顯示。系統會記錄每個回合的對話，方便您提出後續問題。
4. 當任務執行時，發送按鈕會變為 **停止**；確認後即可取消執行。

## 處理流程

根據輸入框下方的核取方塊設定，每個請求會依序經過：

1. [優化用戶要求](prompt_engineering.md)（`優化`）– 選用
2. [選用工具](chat_tool_selection.md)（`工具`）– 選用
3. 回覆生成，可選用[代理](chat_agent_option.md)選項
4. [審查](chat_review.md)節點 – 選用

## 控制項

| 控制項 | 用途 |
|---|---|
| 自動滾動 | 隨著串流輸出自動向下滾動 (`auto_scroll`) |
| 優化 | `prompt_engineering`（預設開啟） |
| 代理 | `use_agent`（預設開啟） |
| 工具 | `auto_tool_selection`（預設關閉） |
| 審查 | `chat_mode_review`（預設關閉） |

核取方塊的狀態會儲存於您的偏好設定中。

## 其他操作

[複製、下載、編輯與匯出](export_edit_responses.md)。歡迎訊息底部的按鈕可切換至[夥伴模式](partner_mode.md)或[代理模式](agent_mode.md)。

## 必要條件

使用您所設定的 [AI 後端](ai_backends.md)。

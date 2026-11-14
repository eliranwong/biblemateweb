# BibleMate AI (CLI 與 MCP)

BibleMate AI Web 結合了 [BibleMate AI](https://github.com/eliranwong/biblemate) 的網頁介面與 [UniqueBible](https://github.com/eliranwong/UniqueBible) 的豐富資源。

- 配套專案 **BibleMate AI** 提供了 CLI 版本、MCP 伺服器、完整的代理模式後端以及聖經數據（可透過 `biblematedata` 安裝數據）。
- 在禁用網頁版本的伺服器上，代理模式會引導使用者使用 CLI（[可用性](../ai_features/usage_limits.md)）。
- 網頁應用程式複用了 BibleMate 的工具定義（[MCP 工具整合](../ai_features/chat_tool_selection.md)），使 AI 代理與使用者介面能夠存取完全相同的資源。

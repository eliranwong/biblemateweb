# 測試與原型

本專案沒有統一的測試執行器。`tests/` 存放了用於原型設計或展示功能的獨立腳本（標籤頁、同步滾動、右鍵選單、工具提示、索引、筆記、搜索模式、訂閱後端、API 用戶端等）。您可以直接執行其中一個腳本：

```bash
python tests/api_client.py
```

其中許多是 NiceGUI 範例：執行腳本並開啟輸出顯示的 URL。`tests/sync_scrolling.md` 說明了同步滾動的設計（[使用者視角](../integrations/synchronised_windows.md)）。

發布前的手動檢查：啟動 `biblemateweb`、開啟聖經／工具標籤頁、在每種模式下執行經文搜索、嘗試 [API](../integrations/rest_api.md)，並測試行動裝置版面。

# 語義搜索

按含義搜索。嵌入模型將您的用語與已儲存的向量比對，即使用詞不同，也會返回最接近的結果。它使用 Ollama（`paraphrase-multilingual`），而不是對話、夥伴或代理模式的後端。

## 經文搜索

**搜索** 選單 → `搜索經文`，然後選擇 **語義**（與字面、模式並列）。

輸入短語或概念，例如 `God's forgiveness` 或 `trusting in difficult times`，然後按 Enter。結果為最接近的經文，數量上限為 **Similar Verses**（預設 20，範圍 5–100），位於 `偏好設定` → `語義搜索`。

您可以在該頁面限制書卷與聖經版本。當已選擇語義模式時，快速搜索中的自由文字也使用同一模式。

API：`semantic:::{bibles_books}*:::{search_string}`，例如 `semantic:::love of God` 或 `semantic:::KJV:::Jesus love`。請參閱 [API 查詢語法](../api/api_query.md)。

向量數據：`~/biblemate/data/vectors/bible.db`。

經文搜索指南：[經文搜索](../search/search_bible_verses.md)。

## 其他搜索

這些搜索先查找完全符合的條目。若沒有符合，則按含義搜索，並返回最接近的條目，數量上限為 **Similar Entries**（預設 5，範圍 3–30）：

| 搜索 | 向量數據 |
|---|---|
| 主題、人物、地點、名字 | `~/biblemate/data/vectors/exlb.db` |
| 平行經文、聖經應許 | `~/biblemate/data/vectors/collection.db` |
| 聖經字典 | `~/biblemate/data/vectors/dictionary.db` |
| 百科全書 | `~/biblemate/data/vectors/encyclopedia.db` |

地圖、人物關係與原文詞典不使用此回退。

## 設定

Ollama 必須正在執行並已載入嵌入模型，且向量資料庫必須存在。[語義搜索設定](../server_setup/semantic_search_setup.md)。

未完成此項設定時，字面與模式經文搜索仍然可用。

偏好設定：[相似經文數量](../user_preferences/top_similar_verses.md)、[相似條目數量](../user_preferences/top_similar_entries.md)、[搜索模式](../user_preferences/search_mode.md)。

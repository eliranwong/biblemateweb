# 语义搜索

按含义搜索。嵌入模型将您的用语与已存储的向量比对，即使用词不同，也会返回最接近的结果。它使用 Ollama（`paraphrase-multilingual`），而不是对话、伙伴或代理模式的后端。

## 经文搜索

**搜索** 菜单 → `搜索经文`，然后选择 **语义**（与字面、模式并列）。

输入短语或概念，例如 `God's forgiveness` 或 `trusting in difficult times`，然后按 Enter。结果为最接近的经文，数量上限为 **Similar Verses**（默认 20，范围 5–100），位于 `偏好设定` → `语义搜索`。

您可以在该页面限制书卷与圣经版本。当已选择语义模式时，快速搜索中的自由文本也使用同一模式。

API：`semantic:::{bibles_books}*:::{search_string}`，例如 `semantic:::love of God` 或 `semantic:::KJV:::Jesus love`。请参阅 [API 查询语法](../api/api_query.md)。

向量数据：`~/biblemate/data/vectors/bible.db`。

经文搜索指南：[经文搜索](../search/search_bible_verses.md)。

## 其他搜索

这些搜索先查找完全匹配的条目。若没有匹配，则按含义搜索，并返回最接近的条目，数量上限为 **Similar Entries**（默认 5，范围 3–30）：

| 搜索 | 向量数据 |
|---|---|
| 主题 | `~/biblemate/data/vectors/exlbt.db`、`exlbt_tc.db`、`exlbt_sc.db` |
| 人物 | `~/biblemate/data/vectors/exlbp.db` |
| 地点 | `~/biblemate/data/vectors/exlbl.db` |
| 名字 | `~/biblemate/data/vectors/exlbn.db` |
| 平行经文、圣经应许 | `~/biblemate/data/vectors/collection.db` |
| 圣经字典 | `~/biblemate/data/vectors/dictionary.db` |
| 百科全书 | `~/biblemate/data/vectors/encyclopedia.db` |

地图、人物关系与原文词典不使用此回退。

## 设定

Ollama 必须正在运行并已加载嵌入模型，且向量数据库必须存在。[语义搜索设定](../server_setup/semantic_search_setup.md)。

未完成此项设定时，字面与模式经文搜索仍然可用。

偏好设定：[相似经文数量](../user_preferences/top_similar_verses.md)、[相似条目数量](../user_preferences/top_similar_entries.md)、[搜索模式](../user_preferences/search_mode.md)。

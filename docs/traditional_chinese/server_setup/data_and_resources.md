# 數據與資源

資源存放在套件外部，位於 `~/biblemate/`。

| 路徑 | 內容 |
|---|---|
| `~/biblemate/biblemateweb.config` | 伺服器[配置設定](configuration.md) |
| `~/biblemate/data/bibles/` | 聖經文本（`.bible`，SQLite） |
| `~/biblemate/data/original/` | 原文聖經（ORB、OIB、OPB、ODB、OLB） |
| `~/biblemate/data/commentaries/` | 聖經註釋（`.commentary`） |
| `~/biblemate/data/lexicons/` | 原文詞典（`.lexicon`） |
| `~/biblemate/data/audio/bibles/` | 聖經篇章語音，以及單詞級 `BHS5/default` 和 `OGNT/default` 音訊（手抄本及 `lex_` 原型 MP3） |
| `~/biblemate/data/morphology.sqlite` | 希伯來文與希臘文單詞形態學、音譯、發音、簡注與翻譯 |
| `~/biblemate/data/vectors/bible.db` | 用於語義搜索的向量嵌入 |
| `~/biblemate/data_custom/` | [自訂資源](../integrations/custom_resources.md)（聖經、參考書籍）– 需要自訂 Token |

使用 `biblematedata` 下載或更新。應用程式中的資源清單（聖經選單、偏好設定、[API `.resources`](../api/api_query.md)）皆根據這些資料夾中的內容建構。

套件隨附的靜態參考數據（歷史事件、聖經地點、聖經時間軸、聖經名字、詞彙數據）位於 `package/biblemateweb/data`。

隨附希伯來文與希臘文字型（Ezra SIL、KoineGreek），以確保正確顯示。

# API 查詢語法

指令 `.help` 與 `.resources` 保留用於特定功能：

`.help`：獲取幫助文檔與使用指南。

`.resources`：列出所有可用的聖經版本與資源。

## 標準查詢

所有其他 API 查詢都必須遵循特定格式，由一個關鍵字及其相關選項組成，並以三冒號 `:::` 分隔。

## 語法約定：

`{option}`：表示必填參數。

`{option}*`：表示選填參數。

多個值：如果參數接受多個值，請使用逗號分隔（例如 KJV,NET）。

## 關鍵字 - morphology
* 獲取聖經經文中的單詞形態學分析
* 語法：morphology:::{verse_reference[s]}
* 範例：morphology:::John 3:16

## 關鍵字 - chapter
* 獲取聖經全章經文
* 語法：chapter:::{bible}*:::{chapter_reference[s]}
* 範例：chapter:::John 3, chapter:::KJV:::John 3

## 關鍵字 - comparechapter
* 對比聖經全章經文
* 語法：comparechapter:::{bibles}*:::{chapter_reference[s]}
* 範例：comparechapter:::KJV,CUV:::John 3

## 關鍵字 - verses
* 獲取指定聖經經文
* 語法：verses:::{bibles}*:::{verse_reference[s]}
* 範例：verses:::John 3:16; Rm 5:8, verses:::KJV:::John 3:16; Rm 5:8, verses:::KJV,CUV:::John 3:16; Rm 5:8

## 關鍵字 - literal
* 字面字串搜索聖經經文
* 語法：literal:::{bibles_books}*:::{search_string}
* 範例：literal:::Jesus love, literal:::KJV:::Jesus love, literal:::Matt,KJV:::love

## 關鍵字 - regex
* 正則表達式（模式）搜索聖經經文
* 語法：regex:::{bibles_books}*:::{regex_pattern}
* 範例：regex:::Jesus.*?love, regex:::KJV:::Jesus.*?love, regex:::Matt,KJV:::Jesus.*?love

## 關鍵字 - semantic
* 語義搜索聖經經文
* 語法：semantic:::{bibles_books}*:::{search_string}
* 範例：semantic:::Jesus love, semantic:::KJV:::Jesus love , semantic:::Matt,KJV:::Jesus love

## 關鍵字 - treasury
* 獲取聖經經文的經文寶庫 (Treasury of Scripture Knowledge)
* 語法：treasury:::{verse_reference[s]}
* 範例：treasury:::John 3:16

## 關鍵字 - commentary
* 獲取聖經註釋
* 語法：commentary:::{commentary}*:::{verse_reference[s]}
* 範例：commentary:::John 3:16, commentary:::AICTC:::John 3:16

## 關鍵字 - chronology
* 獲取或搜索聖經時序
* 語法：chronology:::{search_string}*
* 範例：chronology:::, chronology:::70 AD, chronology:::Jesus, chronology:::Acts 15

## 關鍵字 - xrefs
* 獲取聖經經文串珠
* 語法：xrefs:::{bible}*:::{verse_reference[s]}
* 範例：xrefs:::John 3:16, xrefs:::KJV:::John 3:16

## 關鍵字 - promises
* 獲取聖經應許
* 語法：promises:::{bible}*:::{promise_entry}
* 範例：promises:::1.1, promises:::KJV:::1.1

## 關鍵字 - parallels
* 獲取平行經文段落
* 語法：parallels:::{bible}*:::{parallel_entry}
* 範例：parallels:::1.1, parallels:::KJV:::1.1

## 關鍵字 - topics
* 獲取聖經主題研讀
* 語法：topics:::{topic_entry}
* 範例：topics:::NAV100

## 關鍵字 - characters
* 獲取聖經人物研讀
* 語法：characters:::{character_entry}
* 範例：characters:::BP100

## 關鍵字 - locations
* 獲取聖經地點研讀
* 語法：locations:::{location_entry}
* 範例：locations:::BP100

## 關鍵字 - names
* 搜索聖經名字及其含義
* 語法：names:::{name}
* 範例：names:::Joshua

## 關鍵字 - dictionaries
* 獲取聖經字典條目
* 語法：dictionaries:::{dictionary_entry}
* 範例：dictionaries:::EAS100

## 關鍵字 - encyclopedias
* 獲取聖經百科全書條目
* 語法：encyclopedias:::{encyclopedia_entry}
* 範例：encyclopedias:::ISBE100

## 關鍵字 - lexicons
* 獲取聖經原文詞典條目
* 語法：lexicons:::{lexicon}*:::{lexicon_entry}
* 範例：lexicons:::H100, lexicons:::Morphology:::G100

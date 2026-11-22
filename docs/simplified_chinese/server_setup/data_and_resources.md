# 数据与资源

资源存放在软件包外部，位于 `~/biblemate/`。

| 路径 | 内容 |
|---|---|
| `~/biblemate/biblemateweb.config` | 服务器[配置设定](configuration.md) |
| `~/biblemate/data/bibles/` | 圣经文本（`.bible`，SQLite） |
| `~/biblemate/data/original/` | 原文圣经（ORB、OIB、OPB、ODB、OLB） |
| `~/biblemate/data/clauses/` | OPB 平行子句译本模块（`.clause`，SQLite） |
| `~/biblemate/data/commentaries/` | 圣经注释（`.commentary`） |
| `~/biblemate/data/lexicons/` | 原文词典（`.lexicon`） |
| `~/biblemate/data/audio/bibles/` | 圣经篇章语音，以及单词级 `BHS5/default` 和 `OGNT/default` 音频（手抄本及 `lex_` 原型 MP3） |
| `~/biblemate/data/morphology.sqlite` | 希伯来文与希腊文单词形态学、音译、发音、简注与翻译 |
| `~/biblemate/data/vectors/bible.db` | 用于语义搜索的向量嵌入 |
| `~/biblemate/data_custom/` | [自定义资源](../integrations/custom_resources.md)（圣经、参考书籍、子句模块）– 需要自定义 Token |

使用 `biblematedata` 下载或更新。应用程序中的资源列表（圣经选单、偏好设定、[API `.resources`](../api/api_query.md)）均根据这些文件夹中的内容构建。

软件包随附的静态参考数据（历史事件、圣经地点、圣经时间轴、圣经名字、词汇数据）位于 `package/biblemateweb/data`。

随附希伯来文与希腊文字体（Ezra SIL、KoineGreek），以确保正确显示。

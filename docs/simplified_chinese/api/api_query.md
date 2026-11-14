# API 查询语法

指令 `.help` 与 `.resources` 保留用于特定功能：

`.help`：获取帮助文档与使用指南。

`.resources`：列出所有可用的圣经版本与资源。

## 标准查询

所有其他 API 查询都必须遵循特定格式，由一个关键字及其相关选项组成，并以三冒号 `:::` 分隔。

## 语法约定：

`{option}`：表示必填参数。

`{option}*`：表示选填参数。

多个值：如果参数接受多个值，请使用逗号分隔（例如 KJV,NET）。

## 关键字 - morphology
* 获取圣经经文中的单词形态学分析
* 语法：morphology:::{verse_reference[s]}
* 示例：morphology:::John 3:16

## 关键字 - chapter
* 获取圣经全章经文
* 语法：chapter:::{bible}*:::{chapter_reference[s]}
* 示例：chapter:::John 3, chapter:::KJV:::John 3

## 关键字 - comparechapter
* 对比圣经全章经文
* 语法：comparechapter:::{bibles}*:::{chapter_reference[s]}
* 示例：comparechapter:::KJV,CUV:::John 3

## 关键字 - verses
* 获取指定圣经经文
* 语法：verses:::{bibles}*:::{verse_reference[s]}
* 示例：verses:::John 3:16; Rm 5:8, verses:::KJV:::John 3:16; Rm 5:8, verses:::KJV,CUV:::John 3:16; Rm 5:8

## 关键字 - literal
* 字面字符串搜索圣经经文
* 语法：literal:::{bibles_books}*:::{search_string}
* 示例：literal:::Jesus love, literal:::KJV:::Jesus love, literal:::Matt,KJV:::love

## 关键字 - regex
* 正则表达式（模式）搜索圣经经文
* 语法：regex:::{bibles_books}*:::{regex_pattern}
* 示例：regex:::Jesus.*?love, regex:::KJV:::Jesus.*?love, regex:::Matt,KJV:::Jesus.*?love

## 关键字 - semantic
* 语义搜索圣经经文
* 语法：semantic:::{bibles_books}*:::{search_string}
* 示例：semantic:::Jesus love, semantic:::KJV:::Jesus love , semantic:::Matt,KJV:::Jesus love

## 关键字 - treasury
* 获取圣经经文的经文宝库 (Treasury of Scripture Knowledge)
* 语法：treasury:::{verse_reference[s]}
* 示例：treasury:::John 3:16

## 关键字 - commentary
* 获取圣经注释
* 语法：commentary:::{commentary}*:::{verse_reference[s]}
* 示例：commentary:::John 3:16, commentary:::AICTC:::John 3:16

## 关键字 - chronology
* 获取或搜索圣经时序
* 语法：chronology:::{search_string}*
* 示例：chronology:::, chronology:::70 AD, chronology:::Jesus, chronology:::Acts 15

## 关键字 - xrefs
* 获取圣经经文串珠
* 语法：xrefs:::{bible}*:::{verse_reference[s]}
* 示例：xrefs:::John 3:16, xrefs:::KJV:::John 3:16

## 关键字 - promises
* 获取圣经应许
* 语法：promises:::{bible}*:::{promise_entry}
* 示例：promises:::1.1, promises:::KJV:::1.1

## 关键字 - parallels
* 获取平行经文段落
* 语法：parallels:::{bible}*:::{parallel_entry}
* 示例：parallels:::1.1, parallels:::KJV:::1.1

## 关键字 - topics
* 获取圣经主题研读
* 语法：topics:::{topic_entry}
* 示例：topics:::NAV100

## 关键字 - characters
* 获取圣经人物研读
* 语法：characters:::{character_entry}
* 示例：characters:::BP100

## 关键字 - locations
* 获取圣经地点研读
* 语法：locations:::{location_entry}
* 示例：locations:::BP100

## 关键字 - names
* 搜索圣经名字及其含义
* 语法：names:::{name}
* 示例：names:::Joshua

## 关键字 - dictionaries
* 获取圣经字典条目
* 语法：dictionaries:::{dictionary_entry}
* 示例：dictionaries:::EAS100

## 关键字 - encyclopedias
* 获取圣经百科全书条目
* 语法：encyclopedias:::{encyclopedia_entry}
* 示例：encyclopedias:::ISBE100

## 关键字 - lexicons
* 获取圣经原文词典条目
* 语法：lexicons:::{lexicon}*:::{lexicon_entry}
* 示例：lexicons:::H100, lexicons:::Morphology:::G100

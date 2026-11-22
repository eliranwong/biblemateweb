# 原文语法结构圣经 (ODB)

附带语法结构注释的原文文本，便于掌握句子与段落之间的衔接脉络。

## 开启方式

- **“圣经”**菜单 → 原文语法结构圣经（Original Discourse Bible，圣经区域），或**“平行圣经”**菜单（工具区域）。
- [快速搜索](../basics/quick_search.md)：输入 `ODB`，或 `ODB:::John 3:16` 格式的经文引用。

## 功能特点

- 与其他圣经相同，具备[选择器](../integrations/bible_selectors.md)、[三点菜单](../integrations/three_dot_menu.md)（提供书卷／全章／单节工具的 💡 图标）以及[经文菜单](../integrations/verse_menu.md)。
- 原文字词支持交互操作：将鼠标悬停于（或轻触）任何希伯来文或希腊文字词，即可打开[弹出窗口](../integrations/word_tooltips.md)，显示其**手抄本形式**（包含音译、发音及内嵌**手抄本形式音频播放器**）、**词元形式**（包含内嵌**词元形式音频播放器**）、**形态学分析**、**逐字对照释义**与**翻译**。在弹出窗口内点击手抄本字词或词元，可打开[原文词典](../search/search_lexicons.md)。
- 经文译文会从可用的 `.bible` 模块（`~/biblemate/data/bibles/`，以及启用有效[自定义令牌](../user_preferences/custom_token.md)时的 `~/biblemate/data_custom/bibles/`）动态加载。可在[偏好设定](../user_preferences/README.md)中设定旧约与新约译本（`ODB OT Translation` 默认 `NET`、`ODB NT Translation` 默认 `NET`）。带有标注的译文字词支持与原文之间的双向悬停高亮，并在悬停时显示字词提示框。
- 内置希伯来文和希腊文字体，以确保正确显示。
- 支持[同步](../layout/sync.md)与同步滚动。

数据文件：`~/biblemate/data/original/ODB.bible`（[数据与资源](../server_setup/data_and_resources.md)）。另请参见[形态学分析](../tools/tool_morphology.md)。

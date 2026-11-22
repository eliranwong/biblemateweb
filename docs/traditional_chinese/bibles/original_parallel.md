# 原文平行聖經 (OPB)

原文文本與譯本並排呈現，方便對照原文與翻譯表達。

## 開啟方式

- **「聖經」**選單 → 原文平行聖經（Original Parallel Bible，聖經區域），或**「平行聖經」**選單（工具區域）。
- [快速搜索](../basics/quick_search.md)：輸入 `OPB`，或 `OPB:::John 3:16` 格式的經文引用。

## 功能特點

- 與其他聖經相同，具備[選擇器](../integrations/bible_selectors.md)、[三點選單](../integrations/three_dot_menu.md)（提供書卷／全章／單節工具的 💡 圖示）以及[經文選單](../integrations/verse_menu.md)。
- 原文字詞支援互動操作：將滑鼠懸停於（或輕觸）任何希伯來文或希臘文字詞，即可開啟[快顯視窗](../integrations/word_tooltips.md)，顯示其**手抄本形式**（包含音譯、發音及內嵌**手抄本形式音訊播放器**）、**詞元形式**（包含內嵌**詞元形式音訊播放器**）、**形態學分析**、**逐字對照釋義**與**翻譯**。在快顯視窗內點擊手抄本字詞或詞元，可開啟[原文詞典](../search/search_lexicons.md)。
- 平行子句譯文（`<trans1>`、`<trans2>`）會從 `~/biblemate/data/clauses/`（以及啟用有效[自訂權杖](../user_preferences/custom_token.md)時的 `~/biblemate/data_custom/clauses/`）動態載入。可在[偏好設定](../user_preferences/README.md)中分別設定舊約與新約的子句譯本（`OPB OT Translation 1` 預設 `KJV`、`OPB OT Translation 2` 預設 `NET`、`OPB NT Translation 1` 預設 `KJV`、`OPB NT Translation 2` 預設 `NET`）。帶有標註的譯文字詞支援與原文之間的雙向懸停高亮，並在懸停時顯示字詞提示框。
- 內建希伯來文和希臘文字型，以確保正確顯示。
- 支援[同步](../layout/sync.md)與同步滾動。

資料檔案：`~/biblemate/data/original/OPB.bible` 與 `~/biblemate/data/clauses/*.clause`（[數據與資源](../server_setup/data_and_resources.md)）。另請參見[形態學分析](../tools/tool_morphology.md)。

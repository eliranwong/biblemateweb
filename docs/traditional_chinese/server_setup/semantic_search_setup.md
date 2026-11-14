# 語義搜索設定

語義（基於含義）搜索透過比對嵌入向量進行。它需要由 Ollama 提供的嵌入模型。

1. 安裝 Ollama：<https://ollama.com/download>。
2. 下載模型：
   ```bash
   ollama pull paraphrase-multilingual
   ```
3. 確保 Ollama 伺服器正在執行。
4. `config.embedding_model` 預設為 `paraphrase-multilingual`（請參閱[配置設定指南](configuration.md)）。
5. 向量數據必須存在於 `~/biblemate/data/vectors/bible.db`（[數據與資源](data_and_resources.md)）。

若未進行此項設定，字面與模式搜索仍然可以正常運作（[搜索模式](../user_preferences/search_mode.md)）。

Android：[install_ollama.md](../android_termux/install_ollama.md)。

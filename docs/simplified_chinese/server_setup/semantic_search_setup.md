# 语义搜索设定

语义（基于含义）搜索通过比对嵌入向量进行。它需要由 Ollama 提供的嵌入模型。

1. 安装 Ollama：<https://ollama.com/download>。
2. 下载模型：
   ```bash
   ollama pull paraphrase-multilingual
   ```
3. 确保 Ollama 服务器正在运行。
4. `config.embedding_model` 默认为 `paraphrase-multilingual`（请参阅[配置设定指南](configuration.md)）。
5. 向量数据必须存在于 `~/biblemate/data/vectors/bible.db`（[数据与资源](data_and_resources.md)）。

若未进行此项设定，字面与模式搜索仍然可以正常运作（[搜索模式](../user_preferences/search_mode.md)）。使用方法：[语义搜索](../ai_features/semantic_search.md)。

Android：[install_ollama.md](../android_termux/install_ollama.md)。

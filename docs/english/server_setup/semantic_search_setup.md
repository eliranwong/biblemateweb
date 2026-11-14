# Semantic Search Setup

Semantic (meaning-based) search compares embeddings. It needs an embedding model served by Ollama.

1. Install Ollama: <https://ollama.com/download>.
2. Download the model:
   ```bash
   ollama pull paraphrase-multilingual
   ```
3. Make sure the Ollama server is running.
4. `config.embedding_model` defaults to `paraphrase-multilingual` (see [Configuration](configuration.md)).
5. Vector data must be present at `~/biblemate/data/vectors/bible.db` ([Data & Resources](data_and_resources.md)).

Without this setup the Literal and Regex modes still work ([Search Mode](../user_preferences/search_mode.md)).

Android: [install_ollama.md](../android_termux/install_ollama.md).

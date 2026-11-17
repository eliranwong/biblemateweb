# 安裝指南

## 系統需求

- Python 3.10 – 3.14
- Linux、macOS 或 Windows
- 選用：用於 DOCX 匯出的 `pandoc`（[指南](docx_export.md)）；用於語義搜索的 Ollama（[指南](semantic_search_setup.md)）

## 安裝

```bash
pip install --upgrade --no-cache-dir biblemateweb
```

如有需要，可以使用虛擬環境：

```bash
python3 -m venv ai
source ai/bin/activate
pip install --upgrade --no-cache-dir biblemateweb
```

## 下載數據

```bash
biblematedata
```

此一次性命令會將聖經資料庫與資源下載至 `~/biblemate/data`（[數據與資源](data_and_resources.md)）。

## 啟動

```bash
biblemateweb
```

開啟 <http://localhost:33355>。請參閱[啟動與運行伺服器](running_the_server.md)與[首次執行](first_run.md)。

## 升級

重新執行 `pip install --upgrade` 命令並重新啟動伺服器。若需要更新數據，請再次執行 `biblematedata`。

## Docker

請參閱 [Docker 部署](docker.md)。

## Android

請參閱 [Android Termux 設定](../android_termux/README.md)。

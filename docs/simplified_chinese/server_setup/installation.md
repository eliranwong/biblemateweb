# 安装指南

## 系统需求

- Python 3.10 – 3.14
- Linux、macOS 或 Windows
- 可选：用于 DOCX 导出的 `pandoc`（[指南](docx_export.md)）；用于语义搜索的 Ollama（[指南](semantic_search_setup.md)）

## 安装

```bash
pip install --upgrade --no-cache-dir biblemateweb
```

如有需要，可以使用虚拟环境：

```bash
python3 -m venv ai
source ai/bin/activate
pip install --upgrade --no-cache-dir biblemateweb
```

## 下载数据

```bash
biblematedata
```

此一次性命令会将圣经数据库与资源下载至 `~/biblemate/data`（[数据与资源](data_and_resources.md)）。

## 启动

```bash
biblemateweb
```

打开 <http://localhost:33355>。请参阅[启动与运行服务器](running_the_server.md)与[首次运行](first_run.md)。

## 升级

重新运行 `pip install --upgrade` 命令并重启服务器。若需要更新数据，请再次运行 `biblematedata`。

## Android

请参阅 [Android Termux 设定](../android_termux/README.md)。

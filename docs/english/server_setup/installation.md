# Installation

## Requirements

- Python 3.10 – 3.14
- Linux, macOS or Windows
- Optional: `pandoc` for DOCX export ([guide](docx_export.md)); Ollama for semantic search ([guide](semantic_search_setup.md))

## Install

```bash
pip install --upgrade --no-cache-dir biblemateweb
```

Use a virtual environment if you like:

```bash
python3 -m venv ai
source ai/bin/activate
pip install --upgrade --no-cache-dir biblemateweb
```

## Download data

```bash
biblematedata
```

This one-time command downloads the Bible databases and resources into `~/biblemate/data` ([Data & Resources](data_and_resources.md)).

## Start

```bash
biblemateweb
```

Open <http://localhost:33355>. See [Running the Server](running_the_server.md) and [First Run](first_run.md).

## Upgrade

Re-run the `pip install --upgrade` command and restart the server. Run `biblematedata` again if new data is required.

## Android

See [Android Termux Setup](../android_termux/README.md).

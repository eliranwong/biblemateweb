# 在 Android Termux 上設定 BibleMateWeb

本文說明如何透過 Termux 應用程式在 Android 手機上設定 BibleMateWeb。

備註：整個設定過程稍微複雜，但這是一次性的工作。設定完成後，您即可在 Android 裝置上享受 BibleMateWeb 及其所有可用資源。

## 前置需求

請按照 [install_termux.md](install_termux.md) 中的說明安裝 Termux。

### 安裝 Ubuntu 環境 [Claude Code 與 Codex CLI 必要]

請按照 [install_ubuntu.md](install_ubuntu.md) 中的說明安裝 Ubuntu。

### 安裝編程代理：

* Antigravity CLI：請按照 [install_antigravity_cli.md](install_antigravity_cli.md) 中的說明安裝 Antigravity CLI。
* Claude Code：請按照 [install_claude_code.md](install_claude_code.md) 中的說明安裝 Claude Code。
* Codex CLI：請按照 [install_codex_cli.md](install_codex_cli.md) 中的說明安裝 Codex CLI。

### 安裝 Ollama

請按照 [install_ollama.md](install_ollama.md) 中的說明安裝 Ollama。

## 安裝 BibleMateWeb

在 Termux 中啟動 Ubuntu 環境，執行：

```
ubuntu
```

在 Ubuntu 內部執行：

```
cd ~
python3 -m venv ai
source ai/bin/activate
pip install --upgrade --no-cache-dir biblemateweb

# One-time data setup (downloads Bible databases)
biblematedata

# Start the server
biblemateweb
```

## 在 Ubuntu 啟動時自動啟動 BibleMateWeb

在 ~/.bashrc 中新增以下區塊

```
start_bmweb() {
  echo "Starting BibleMate AI WEB server ..."
  nohup "$HOME/ai/bin/biblemateweb" &
  echo "BibleMate AI WEB server started."
}
### Check if BibleMate WEB server is already running
if ! pgrep -f "/bin/biblemateweb" > /dev/null; then
  start_bmweb
else
  echo "BibleMate AI WEB server is already running."
fi
```

## 像應用程式一樣安裝

使用 Chrome 瀏覽器開啟以下網址以啟動 BibleMateWeb：

http://localhost:33355

接著，在 Chrome 的選單（三個圓點）中，選擇「安裝並建立捷徑」。

這將在主畫面上為 BibleMateWeb 建立一個圖示。

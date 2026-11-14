# 在 Android Termux 上设定 BibleMateWeb

本文说明如何通过 Termux 应用程序在 Android 手机上设定 BibleMateWeb。

备注：整个设定过程稍微复杂，但这是一次性的工作。设定完成后，您即可在 Android 设备上享受 BibleMateWeb 及其所有可用资源。

## 前提条件

请按照 [install_termux.md](install_termux.md) 中的说明安装 Termux。

### 安装 Ubuntu 环境 [Claude Code 与 Codex CLI 必要]

请按照 [install_ubuntu.md](install_ubuntu.md) 中的说明安装 Ubuntu。

### 安装编程代理：

* Antigravity CLI：请按照 [install_antigravity_cli.md](install_antigravity_cli.md) 中的说明安装 Antigravity CLI。
* Claude Code：请按照 [install_claude_code.md](install_claude_code.md) 中的说明安装 Claude Code。
* Codex CLI：请按照 [install_codex_cli.md](install_codex_cli.md) 中的说明安装 Codex CLI。

### 安装 Ollama

请按照 [install_ollama.md](install_ollama.md) 中的说明安装 Ollama。

## 安装 BibleMateWeb

在 Termux 中启动 Ubuntu 环境，运行：

```
ubuntu
```

在 Ubuntu 内部运行：

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

## 在 Ubuntu 启动时自动启动 BibleMateWeb

在 ~/.bashrc 中添加以下代码块

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

## 像应用程序一样安装

使用 Chrome 浏览器打开以下网址以启动 BibleMateWeb：

http://localhost:33355

接着，在 Chrome 的菜单（三个圆点）中，选择“安装并创建快捷方式”。

这将在主屏幕上为 BibleMateWeb 创建一个图标。

# BibleMateWeb Setup on Android Termux

This file describes how to set up BibleMateWeb on Android mobile phone via Termux app.

Remarks: The whole setup is a bit complex but this is a one-time job. After setup, you can enjoy BibleMateWeb and all available resources on your Android device.

## Prerequisites

Install termux following the instructions at [install_termux.md](install_termux.md).

### Install Ubuntu Environment [Required for Claude Code and Codex CLI]

Install ubuntu following the instructions at [install_ubuntu.md](install_ubuntu.md).

### Install Coding Agents:

* Antigravity CLI: Install antigravity cli following the instructions at [install_antigravity_cli.md](install_antigravity_cli.md).
* Claude Code: Install claude code following the instructions at [install_claude_code.md](install_claude_code.md).
* Codex CLI: Install codex cli following the instructions at [install_codex_cli.md](install_codex_cli.md).

### Install Ollama

Install ollama following the instructions at [install_ollama.md](install_ollama.md).

## Install BibleMateWeb

Launch Ubuntu environment in Termux, run:

```
ubuntu
```

Inside ubuntu, run:

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

## Auto-start BibleMateWeb when Ubuntu starts

Add the following block in ~/.bashrc

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

## Install like an App

Launch the BibleMateWeb with Chrome browser by opening:

http://localhost:33355

Then, in Chrome's menu (three dots), select "Install and create shortcut".

This will create a home screen icon for BibleMateWeb.
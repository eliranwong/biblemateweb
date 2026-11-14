# 安裝 Claude Code

Claude Code 可在 BibleMate AI Web 中作為基於訂閱的 AI 後端（`claude`）使用 – 請參閱 [AI 後端](../ai_features/ai_backends.md) 以及 [配置設定指南](../server_setup/configuration.md) 中的 `config.show_claude_code`。

它在 Ubuntu 環境中運行（[install_ubuntu.md](install_ubuntu.md)）。

```
ubuntu
```

在 Ubuntu 內部安裝 Node.js 和 Claude Code：

```
apt install -y nodejs npm
npm install -g @anthropic-ai/claude-code
```

登入一次（需要 Claude 訂閱）：

```
claude auth login
```

使用 `claude --version` 驗證。

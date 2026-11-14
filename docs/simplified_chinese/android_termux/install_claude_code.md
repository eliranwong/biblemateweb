# 安装 Claude Code

Claude Code 可在 BibleMate AI Web 中作为基于订阅的 AI 后端（`claude`）使用 – 请参阅 [AI 后端](../ai_features/ai_backends.md) 以及 [配置设定指南](../server_setup/configuration.md) 中的 `config.show_claude_code`。

它在 Ubuntu 环境中运行（[install_ubuntu.md](install_ubuntu.md)）。

```
ubuntu
```

在 Ubuntu 内部安装 Node.js 和 Claude Code：

```
apt install -y nodejs npm
npm install -g @anthropic-ai/claude-code
```

登录一次（需要 Claude 订阅）：

```
claude auth login
```

使用 `claude --version` 验证。

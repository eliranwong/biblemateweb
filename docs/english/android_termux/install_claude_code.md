# Install Claude Code

Claude Code can be used as a subscription-based AI backend (`claude`) in BibleMate AI Web – see [AI Backends](../ai_features/ai_backends.md) and `config.show_claude_code` in the [Configuration Guide](../server_setup/configuration.md).

It runs inside the Ubuntu environment ([install_ubuntu.md](install_ubuntu.md)).

```
ubuntu
```

Inside Ubuntu, install Node.js and Claude Code:

```
apt install -y nodejs npm
npm install -g @anthropic-ai/claude-code
```

Sign in once (requires a Claude subscription):

```
claude auth login
```

Verify with `claude --version`.

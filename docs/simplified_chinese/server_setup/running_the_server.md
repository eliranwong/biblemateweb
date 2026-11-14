# 启动与运行服务器

## 命令

以下命令均可启动相同的 Web 服务器（以及 API 服务器）：

| 命令 | 说明 |
|---|---|
| `biblemateweb` | 主要命令 |
| `bmweb` | 简短别名 |
| `biblemategui` | 别名 |

API 客户端命令：`biblemateapi`、`bmapi`（[API 客户端](../integrations/api_client_cli.md)）。数据下载命令：`biblematedata`。

服务器监听 `config.port`（默认为 `33355`）。仅在开发期间将 `config.hot_reload` 设为 `True`。

## 保持持续运行

带自动检查的后台启动（如 [`scripts/auto_start.sh`](../../scripts/auto_start.sh) 所示）：

```bash
if ! pgrep -f "/bin/biblemateweb" > /dev/null; then
  nohup biblemateweb &
fi
```

将其添加到 `~/.bashrc` 或登录脚本中，以便在登录时自动启动。对于服务器，建议使用 systemd 或 supervisor。

### systemd 示例

```ini
[Unit]
Description=BibleMate AI Web
After=network.target

[Service]
User=youruser
ExecStart=/home/youruser/ai/bin/biblemateweb
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## 停止与重启

停止进程（`pkill -f biblemateweb`），然后再次启动。每次更改设定后都需要重启。

## 路由

请参阅[路由与端点](../api/routes.md)。

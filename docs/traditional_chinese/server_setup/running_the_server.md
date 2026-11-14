# 啟動與運行伺服器

## 命令

以下命令皆可啟動相同的 Web 伺服器（以及 API 伺服器）：

| 命令 | 說明 |
|---|---|
| `biblemateweb` | 主要命令 |
| `bmweb` | 簡短別名 |
| `biblemategui` | 別名 |

API 客戶端命令：`biblemateapi`、`bmapi`（[API 客戶端](../integrations/api_client_cli.md)）。數據下載命令：`biblematedata`。

伺服器監聽 `config.port`（預設為 `33355`）。僅在開發期間將 `config.hot_reload` 設為 `True`。

## 保持持續運行

帶自動檢查的背景啟動（如 [`scripts/auto_start.sh`](../../scripts/auto_start.sh) 所示）：

```bash
if ! pgrep -f "/bin/biblemateweb" > /dev/null; then
  nohup biblemateweb &
fi
```

將其新增至 `~/.bashrc` 或登入指令檔中，以便在登入時自動啟動。對於伺服器，建議使用 systemd 或 supervisor。

### systemd 範例

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

## 停止與重啟

停止行程（`pkill -f biblemateweb`），然後再次啟動。每次更改設定後都需要重新啟動。

## 路由

請參閱[路由與端點](../api/routes.md)。

# Running the Server

## Commands

All of these start the same web server (and API server):

| Command | Notes |
|---|---|
| `biblemateweb` | Main command |
| `bmweb` | Short alias |
| `biblemategui` | Alias |

API client commands: `biblemateapi`, `bmapi` ([API Client](../integrations/api_client_cli.md)). Data download: `biblematedata`.

The server listens on `config.port` (default `33355`). Set `config.hot_reload=True` only during development.

## Keep it running

Background start with auto-check (as in [`scripts/auto_start.sh`](../../scripts/auto_start.sh)):

```bash
if ! pgrep -f "/bin/biblemateweb" > /dev/null; then
  nohup biblemateweb &
fi
```

Add it to `~/.bashrc` or a login script to start on login. For servers use systemd or supervisor.

### systemd example

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

## Stop / restart

Stop the process (`pkill -f biblemateweb`), then start it again. Restart after every config change.

## Routes

See [Routes & Endpoints](../api/routes.md).

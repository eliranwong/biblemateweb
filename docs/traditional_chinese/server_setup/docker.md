# Docker 部署

使用 `python:3.12-slim`（Debian）與 `uv` 在 Docker 容器中運行 BibleMate AI Web，實現快速、穩定的依賴解析與部署。

> [!NOTE]
> `python:3.12-slim`（`glibc`）為 BibleMate AI Web 的依賴項提供了預編譯的 `manylinux` wheel，而 `uv` 可以避免 `pip` 出現 `resolution-too-deep` 依賴回溯超時錯誤。

## Dockerfile

建立一個 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

## get UID/GID of host user for remapping to access bindmounts on host
ARG USER=biblemate
ARG UID=1000

ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV="/home/${USER}/.biblemate" \
    PATH="/home/${USER}/.biblemate/bin:/home/${USER}/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      net-tools \
      iproute2 \
      ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN \
  groupadd -g "${UID}" "${USER}" && \
  useradd -m -u "${UID}" -g "${USER}" -G sudo -s /bin/bash "${USER}"

USER ${USER}
WORKDIR /home/${USER}

RUN \
  python3 -m venv "${VIRTUAL_ENV}" && \
  pip install --no-cache-dir --upgrade pip uv && \
  uv pip install --no-cache "biblemateweb"

# Set the default command to start an interactive shell (useful for debugging)
#CMD ["/bin/bash"]

CMD ["biblemateweb"]
```

如需固定特定版本，可將 `"biblemateweb"` 替換為例如 `"biblemateweb==1.0.9"`。

## 建置映像檔

傳入宿主機的使用者名稱與 UID，以確保掛載目錄（bind mount）的檔案權限與宿主機使用者一致：

```bash
docker build \
  --build-arg USER="$USER" \
  --build-arg UID="$(id -u)" \
  -t biblemateweb .
```

## 運行容器

掛載 `~/biblemate` 以持久化已下載的數據與設定檔（[數據與資源](data_and_resources.md)、[配置設定指南](configuration.md)），並映射連接埠 `33355`：

```bash
mkdir -p ~/biblemate
docker run -d \
  --name biblemateweb \
  -p 33355:33355 \
  -v ~/biblemate:/home/"$USER"/biblemate \
  biblemateweb
```

在瀏覽器中開啟 <http://localhost:33355>。

## 下載數據 / 進入容器

如需預先下載聖經資料庫（`biblematedata`）或進入容器操作：

```bash
docker exec -it biblemateweb biblematedata
```

## Antigravity CLI（`agy`）與持久化登入（Docker Compose）

專案已內建 [Dockerfile](../../../scripts/Dockerfile) 與 [docker-compose.yml](../../../scripts/docker-compose.yml)，並透過以下指令安裝 Antigravity CLI（`agy`）：

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

由於容器檔案系統會在重建時重置，系統會將以下三個主機目錄綁定掛載到容器中，以保存 `agy` 的登入憑證與 CLI 狀態：

- `~/.gemini/antigravity-cli`（CLI 設定、`installation_id`、狀態與對話紀錄）
- `~/.gemini/antigravity`（共用 Antigravity 狀態）
- `~/.config/antigravity`（`credential-user-scope`）

### 1. 建立主機目錄並啟動容器

請先在主機建立目錄（避免 Docker 以 `root` 權限自動建立），再以主機的 `USER` 與 `UID` 建置並啟動：

```bash
mkdir -p ~/biblemate ~/docker-agy/.gemini/antigravity-cli ~/docker-agy/.gemini/antigravity ~/docker-agy/.config/antigravity
USER="$(whoami)" UID="$(id -u)" docker compose -f scripts/docker-compose.yml up -d --build
```

> [!TIP]
> 若希望與主機共用現有的 `agy` 登入狀態，而不是使用獨立的 Docker 登入目錄，可直接掛載主機的 `~/.gemini/antigravity-cli`、`~/.gemini/antigravity` 與 `~/.config/antigravity` 取代 `~/docker-agy/...`。

### 2. 一次性手動登入

在運行中的容器內啟動互動式 `agy` 工作階段：

```bash
docker compose -f scripts/docker-compose.yml exec biblemateweb agy
```

依畫面上的驗證提示完成帳號與訂閱登入，之後輸入 `/exit` 或按 `Ctrl+D Ctrl+D` 離開 `agy`。

由於驗證與設定目錄皆保存在主機上，之後無論執行 `docker compose restart`、`docker compose down && up` 或重新建置映像檔，登入與訂閱狀態都會持續保留。

另請參閱：[安裝指南](installation.md)、[啟動與運行伺服器](running_the_server.md)、[安全與部署](security_and_deployment.md)。


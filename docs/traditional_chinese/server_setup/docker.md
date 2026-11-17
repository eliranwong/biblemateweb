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

另請參閱：[安裝指南](installation.md)、[啟動與運行伺服器](running_the_server.md)、[安全與部署](security_and_deployment.md)。


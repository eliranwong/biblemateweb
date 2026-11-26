# Docker 部署

使用 `python:3.12-slim`（Debian）与 `uv` 在 Docker 容器中运行 BibleMate AI Web，实现快速、稳定的依赖解析与部署。

> [!NOTE]
> `python:3.12-slim`（`glibc`）为 BibleMate AI Web 的依赖项提供了预编译的 `manylinux` wheel，而 `uv` 可以避免 `pip` 出现 `resolution-too-deep` 依赖回溯超时错误。

## Dockerfile

创建一个 `Dockerfile`：

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

如需固定特定版本，可将 `"biblemateweb"` 替换为例如 `"biblemateweb==1.0.9"`。

## 构建镜像

传入宿主机的用户名和 UID，以确保挂载目录（bind mount）的文件权限与宿主机用户一致：

```bash
docker build \
  --build-arg USER="$USER" \
  --build-arg UID="$(id -u)" \
  -t biblemateweb .
```

## 运行容器

挂载 `~/biblemate` 以持久化已下载的数据与配置文件（[数据与资源](data_and_resources.md)、[配置设定指南](configuration.md)），并映射端口 `33355`：

```bash
mkdir -p ~/biblemate
docker run -d \
  --name biblemateweb \
  -p 33355:33355 \
  -v ~/biblemate:/home/"$USER"/biblemate \
  biblemateweb
```

在浏览器中打开 <http://localhost:33355>。

## 下载数据 / 进入容器

如需预先下载圣经数据库（`biblematedata`）或进入容器操作：

```bash
docker exec -it biblemateweb biblematedata
```

## Antigravity CLI（`agy`）与持久化登录（Docker Compose）

项目已内置 [Dockerfile](../../../scripts/Dockerfile) 与 [docker-compose.yml](../../../scripts/docker-compose.yml)，并通过以下命令安装 Antigravity CLI（`agy`）：

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

由于容器文件系统会在重建时重置，系统会将以下三个主机目录绑定挂载到容器中，以保存 `agy` 的登录凭据与 CLI 状态：

- `~/.gemini/antigravity-cli`（CLI 配置、`installation_id`、状态与对话记录）
- `~/.gemini/antigravity`（共享 Antigravity 状态）
- `~/.config/antigravity`（`credential-user-scope`）

### 1. 创建主机目录并启动容器

请先在主机创建目录（避免 Docker 以 `root` 权限自动创建），再以主机的 `USER` 与 `UID` 构建并启动：

```bash
mkdir -p ~/biblemate ~/docker-agy/.gemini/antigravity-cli ~/docker-agy/.gemini/antigravity ~/docker-agy/.config/antigravity
USER="$(whoami)" UID="$(id -u)" docker compose -f scripts/docker-compose.yml up -d --build
```

> [!TIP]
> 若希望与主机共享现有的 `agy` 登录状态，而不是使用独立的 Docker 登录目录，可直接挂载主机的 `~/.gemini/antigravity-cli`、`~/.gemini/antigravity` 与 `~/.config/antigravity` 替代 `~/docker-agy/...`。

### 2. 一次性手动登录

在运行中的容器内启动交互式 `agy` 会话：

```bash
docker compose -f scripts/docker-compose.yml exec biblemateweb agy
```

按屏幕上的认证提示完成账号与订阅登录，之后输入 `/exit` 或按 `Ctrl+D Ctrl+D` 退出 `agy`。

由于认证与配置目录均保存在主机上，此后无论执行 `docker compose restart`、`docker compose down && up` 还是重新构建镜像，登录与订阅状态都会持续保留。

另请参阅：[安装指南](installation.md)、[启动与运行服务器](running_the_server.md)、[安全与部署](security_and_deployment.md)。


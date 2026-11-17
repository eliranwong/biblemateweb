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

另请参阅：[安装指南](installation.md)、[启动与运行服务器](running_the_server.md)、[安全与部署](security_and_deployment.md)。


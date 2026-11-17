# Docker Setup

Run BibleMate AI Web in a Docker container using `python:3.12-slim` (Debian) and `uv` for fast, reliable dependency resolution.

> [!NOTE]
> `python:3.12-slim` (`glibc`) provides pre-built `manylinux` wheels for BibleMate AI Web's dependencies, and `uv` avoids `pip`'s `resolution-too-deep` backtracking errors.

## Dockerfile

Create a `Dockerfile`:

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

To pin a specific release, replace `"biblemateweb"` with e.g. `"biblemateweb==1.0.9"`.

## Build

Pass your host username and UID so bind-mounted directories stay owned by your user:

```bash
docker build \
  --build-arg USER="$USER" \
  --build-arg UID="$(id -u)" \
  -t biblemateweb .
```

## Run

Mount `~/biblemate` to persist downloaded data and configuration ([Data & Resources](data_and_resources.md), [Configuration Guide](configuration.md)), and expose port `33355`:

```bash
mkdir -p ~/biblemate
docker run -d \
  --name biblemateweb \
  -p 33355:33355 \
  -v ~/biblemate:/home/"$USER"/biblemate \
  biblemateweb
```

Open <http://localhost:33355>.

## Download Data / Shell Access

If you want to pre-download Bible databases (`biblematedata`) or inspect the container:

```bash
docker exec -it biblemateweb biblematedata
```

See also [Installation](installation.md), [Running the Server](running_the_server.md), and [Security & Deployment](security_and_deployment.md).


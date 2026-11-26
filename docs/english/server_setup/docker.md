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

## Antigravity CLI (`agy`) & Persistent Login (Docker Compose)

The repository includes a ready-to-use [Dockerfile](../../../scripts/Dockerfile) and [docker-compose.yml](../../../scripts/docker-compose.yml) that install the Antigravity CLI (`agy`) via:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Because container filesystems are ephemeral, `agy` login credentials and CLI state are persisted by bind-mounting three host directories into the container:

- `~/.gemini/antigravity-cli` (CLI settings, `installation_id`, state, conversations)
- `~/.gemini/antigravity` (shared Antigravity state)
- `~/.config/antigravity` (`credential-user-scope`)

### 1. Create host directories & start the container

Pre-create the host directories so Docker does not create them as `root`, then build and start with your host `USER` and `UID`:

```bash
mkdir -p ~/biblemate ~/docker-agy/.gemini/antigravity-cli ~/docker-agy/.gemini/antigravity ~/docker-agy/.config/antigravity
USER="$(whoami)" UID="$(id -u)" docker compose -f scripts/docker-compose.yml up -d --build
```

> [!TIP]
> If you prefer to share your existing host `agy` login instead of keeping a separate Docker login, mount `~/.gemini/antigravity-cli`, `~/.gemini/antigravity`, and `~/.config/antigravity` directly in place of `~/docker-agy/...`.

### 2. One-time manual login

Open an interactive `agy` session inside the running container:

```bash
docker compose -f scripts/docker-compose.yml exec biblemateweb agy
```

Follow the on-screen authentication prompt to sign in to your account/subscription, then exit `agy` (`/exit` or `Ctrl+D Ctrl+D`).

Because the auth and config directories live on the host, your login and subscription persist across `docker compose restart`, `docker compose down && up`, and image rebuilds.

See also [Installation](installation.md), [Running the Server](running_the_server.md), and [Security & Deployment](security_and_deployment.md).


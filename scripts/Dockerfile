FROM python:3.12-slim

ARG USER
ARG UID

ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV="/home/${USER}/.biblemate" \
    BIBLEMATE_WORKSPACE_DIR="/home/${USER}/biblemate" \
    CLAUDE_CONFIG_DIR="/home/${USER}/.claude" \
    PATH="/home/${USER}/.biblemate/bin:/home/${USER}/.local/bin:${PATH}"
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    sudo \
    net-tools \
    iproute2 \
    ffmpeg \
    pandoc && \
    rm -rf /var/lib/apt/lists/*
RUN \
    groupadd -g "${UID}" "${USER}" && \
    useradd -m -u "${UID}" -g "${USER}" -G sudo -s /bin/bash "${USER}"
USER ${USER}
RUN mkdir -p "/home/${USER}/biblemate" \
    "/home/${USER}/.gemini/antigravity-cli" \
    "/home/${USER}/.gemini/antigravity" \
    "/home/${USER}/.config/antigravity" \
    "/home/${USER}/.claude" \
    "/home/${USER}/.grok" \
    "/home/${USER}/.codex"
WORKDIR /home/${USER}/biblemate
RUN curl -fsSL https://antigravity.google/cli/install.sh | bash && \
    curl -fsSL https://claude.ai/install.sh | bash && \
    curl -fsSL https://x.ai/cli/install.sh | bash && \
    curl -fsSL https://chatgpt.com/codex/install.sh | sh
RUN \
    python3 -m venv "${VIRTUAL_ENV}" && \
    pip install --no-cache-dir --upgrade pip uv && \
    uv pip install --no-cache "biblemateweb>=1.7.8" google-antigravity
# Mount your workspace and agy auth/config at runtime (see scripts/docker-compose.yml):
#   -v ~/biblemate:/home/${USER}/biblemate
#   -v ~/docker-agy/.gemini/antigravity-cli:/home/${USER}/.gemini/antigravity-cli
#   -v ~/docker-agy/.gemini/antigravity:/home/${USER}/.gemini/antigravity
#   -v ~/docker-agy/.config/antigravity:/home/${USER}/.config/antigravity
# Set the default command to start an interactive shell (useful for debugging)
#CMD ["/bin/bash"]
CMD ["biblemateweb"]
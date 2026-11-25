FROM python:3.12-slim

ARG USER
ARG UID

ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV="/home/${USER}/.biblemate" \
    BIBLEMATE_WORKSPACE_DIR="/home/${USER}/biblemate" \
    PATH="/home/${USER}/.biblemate/bin:/home/${USER}/.local/bin:${PATH}"
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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
RUN mkdir -p "/home/${USER}/biblemate"
WORKDIR /home/${USER}/biblemate
RUN \
    python3 -m venv "${VIRTUAL_ENV}" && \
    pip install --no-cache-dir --upgrade pip uv && \
    uv pip install --no-cache "biblemateweb>=1.7.8" google-antigravity
# Mount your workspace at runtime:
#   -v ~/biblemate:/home/${USER}/biblemate
# Set the default command to start an interactive shell (useful for debugging)
#CMD ["/bin/bash"]
CMD ["biblemateweb"]
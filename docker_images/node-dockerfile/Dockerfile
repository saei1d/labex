FROM codercom/code-server:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

USER coder
WORKDIR /workspace

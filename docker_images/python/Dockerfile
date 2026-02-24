FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install code-server
RUN wget -qO- https://github.com/coder/code-server/releases/download/v4.19.1/code-server-4.19.1-amd64.tar.gz | tar xz -C /tmp && \
    mv /tmp/code-server-4.19.1-amd64 /usr/local/lib/code-server && \
    ln -s /usr/local/lib/code-server/bin/code-server /usr/local/bin/code-server

# Create user directory
RUN mkdir -p /home/coder/project && \
    useradd -m -s /bin/bash coder && \
    chown -R coder:coder /home/coder

# Set working directory
WORKDIR /home/coder/project

# Install Python tools
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    black==23.11.0 \
    flake8==6.1.0 \
    mypy==1.7.1 \
    requests==2.31.0 \
    numpy==1.24.3

# Set environment variables
ENV PASSWORD=labex
ENV USER=coder
ENV HOME=/home/coder

# Switch to non-root user
USER coder

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start code-server
CMD ["code-server", "--host", "0.0.0.0", "--port", "8080", "--auth", "password"]

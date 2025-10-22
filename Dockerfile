ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

# Install system dependencies including FFmpeg for streaming
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    x11vnc \
    fluxbox \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

FROM base AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKERIZED=true \
    DISPLAY=:99 \
    STREAMING_ENABLED=false

WORKDIR /app

# Install Python dependencies in final stage
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from builder
COPY --from=builder /app .

# Create startup script for X11 display
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'Xvfb :99 -screen 0 1280x720x24 &' >> /app/start.sh && \
    echo 'export DISPLAY=:99' >> /app/start.sh && \
    echo 'sleep 2' >> /app/start.sh && \
    echo 'fluxbox &' >> /app/start.sh && \
    echo 'sleep 1' >> /app/start.sh && \
    echo 'exec gunicorn -w 1 -b 0.0.0.0:3000 --timeout 300 main:app' >> /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

ENTRYPOINT ["/app/start.sh"]
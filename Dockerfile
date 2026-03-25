# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.12-slim

# Stage 1: Build stage
FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_PREFER_BINARY=1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt

# Copy application code to the build stage
COPY main.py .
COPY core ./core
COPY modules ./modules
COPY scripts ./scripts
COPY utils ./utils

# Stage 2: Runtime stage
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    METTA_GAME_INPUT_MODE=websocket \
    METTA_GAME_WEBSOCKET_HOST=0.0.0.0 \
    METTA_GAME_WEBSOCKET_PORT=8765

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

# Expose WebSocket port
EXPOSE 8765

HEALTHCHECK --interval=5s --timeout=3s --retries=5 --start-period=10s \
  CMD python /app/scripts/websocket_healthcheck.py

# Command to run the WebSocket server
CMD ["python", "main.py"]

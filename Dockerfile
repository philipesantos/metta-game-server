# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/usr/local -r requirements.txt

# Copy application code to the build stage
COPY main.py .
COPY core ./core
COPY modules ./modules
COPY scripts ./scripts
COPY utils ./utils

# Stage 2: Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Set environment variables
ENV METTA_GAME_INPUT_MODE=websocket
ENV METTA_GAME_WEBSOCKET_HOST=0.0.0.0
ENV METTA_GAME_WEBSOCKET_PORT=8765

# Expose WebSocket port
EXPOSE 8765

HEALTHCHECK --interval=5s --timeout=3s --retries=5 --start-period=10s \
  CMD python /app/scripts/websocket_healthcheck.py

# Command to run the WebSocket server
CMD ["python", "main.py"]

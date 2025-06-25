# Build stage - Install dependencies and build tools
FROM python:3.12-slim AS builder

# Install only essential build dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libc6-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install with CPU-only PyTorch
COPY api_requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r /tmp/api_requirements.txt \
    && find /opt/venv -name "*.pyc" -delete \
    && find /opt/venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -name "*.pyo" -delete \
    && find /opt/venv -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -name "test" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Final runtime stage - Minimal production image
FROM python:3.12-slim

# Install only essential runtime libraries (no build tools needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy the optimized virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app

WORKDIR /app

# Copy application files selectively (excludes unnecessary files via .dockerignore)
COPY --chown=app:app global_variables/ /app/global_variables/
COPY --chown=app:app logger/ /app/logger/
COPY --chown=app:app middleware/ /app/middleware/
COPY --chown=app:app routes/ /app/routes/
COPY --chown=app:app saved_models/ /app/saved_models/
COPY --chown=app:app schema/ /app/schema/
COPY --chown=app:app App.py /app/App.py
COPY --chown=app:app Server.py /app/Server.py

# Final cleanup of copied files
RUN find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /app -name "*.pyo" -delete

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Switch to non-root user
USER app

# Environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    MODEL_PATH=/app/saved_models/mnist_cnn_pruned_only.pth

EXPOSE 8000

# Lightweight health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "Server.py"]
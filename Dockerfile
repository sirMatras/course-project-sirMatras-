# Build stage
FROM python:3.11-slim AS build
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Run tests in build stage
RUN pytest -q

# Runtime stage
FROM python:3.11-slim

# Create non-root user with specific UID/GID
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser -m -d /app -s /bin/bash appuser

WORKDIR /app

# Copy Python environment from build stage
COPY --from=build --chown=appuser:appuser /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build --chown=appuser:appuser /usr/local/bin /usr/local/bin

# Copy application code with correct ownership
COPY --chown=appuser:appuser . .

# Set environment variables for security
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Expose only necessary port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Switch to non-root user
USER appuser

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

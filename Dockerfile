# Moodify AI Audio Infrastructure Dockerfile
# Multi-stage build for production deployment

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY moodify-core-package/pyproject.toml moodify-core-package/requirements.txt /tmp/
WORKDIR /tmp
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user
RUN groupadd -r moodify && useradd -r -g moodify moodify

# Set working directory
WORKDIR /app

# Copy application code
COPY moodify-core-package/src/ /app/src/
COPY moodify-core-package/pyproject.toml /app/
COPY moodify-core-package/README.md /app/

# Install the package in editable mode
RUN pip install -e /app --no-deps

# Create directories for data
RUN mkdir -p /app/data /app/logs /app/temp /app/models && \
    chown -R moodify:moodify /app

# Switch to non-root user
USER moodify

# Environment variables
ENV PYTHONPATH=/app/src
ENV MOODIFY_ENV=production
ENV MOODIFY_LOG_LEVEL=INFO
ENV MOODIFY_DATA_PATH=/app/data
ENV MOODIFY_TEMP_PATH=/app/temp
ENV MOODIFY_MODEL_PATH=/app/models
ENV MOODIFY_CASES_ROOT=/app/data/cases
ENV MOODIFY_NODE_STATE_DIR=/app/data/node
ENV MOODIFY_NODE_OUTPUT_ROOT=/app/data/output

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import moodify; print('OK')" || exit 1

# Expose API port
EXPOSE 8000

# Default command: Start API server
CMD ["uvicorn", "moodify.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

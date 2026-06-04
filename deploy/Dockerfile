# Dockerfile — Moodify Studio OS Alpha API Server
# Build:  docker build -t moodify-studio-os:alpha -f deploy/Dockerfile .
# Run:    docker run -p 8700:8700 -v $(pwd)/data:/app/data moodify-studio-os:alpha

FROM python:3.12-slim

LABEL org.moodify.service="studio-os-api"
LABEL org.moodify.version="0.2.0-alpha"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY moodify_runtime/ /app/moodify_runtime/
COPY moodify-core-package/ /app/moodify-core-package/

# Runtime config (override with volume mount or env var)
ENV MOODIFY_RUNTIME_CONFIG=/app/data/runtime_config.json
ENV PYTHONUNBUFFERED=1

EXPOSE 8700

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8700/health')" || exit 1

CMD ["python3", "-m", "uvicorn", "moodify_runtime.operator_api:app", \
     "--host", "0.0.0.0", "--port", "8700"]

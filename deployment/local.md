# Local Deployment Guide

Get Moodify running locally in 30 minutes.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- 8GB RAM minimum
- 10GB free disk space

## Step 1: Clone Repository

```bash
git clone https://github.com/huliye24/moodify-ai.git
cd moodify-ai
```

## Step 2: Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
MOODIFY_ENV=development
MOODIFY_LOG_LEVEL=DEBUG
```

## Step 3: Create Directories

```bash
mkdir -p data/cases data/node data/output temp models
```

## Step 4: Build and Start

```bash
docker-compose up --build -d
```

This will:
- Build the Docker image
- Start API service on port 8000
- Start Worker service on port 8001
- Create persistent volumes for data

## Step 5: Verify Installation

Check services are running:

```bash
docker-compose ps
```

Test API health:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

## Step 6: Test Audio Analysis

Upload a test audio file:

```bash
curl -X POST \
  http://localhost:8000/api/v1/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@/path/to/your/audio.wav"
```

## View Logs

```bash
# API logs
docker-compose logs -f moodify-api

# Worker logs
docker-compose logs -f moodify-worker

# All logs
docker-compose logs -f
```

## Stop Services

```bash
docker-compose down
```

To remove all data:

```bash
docker-compose down -v
```

## Development Mode

For development with hot reload:

```bash
# Edit docker-compose.yml to mount source code
# Add to moodify-api service volumes:
#   - ./moodify-core-package/src:/app/src:ro

# Restart
docker-compose restart moodify-api
```

## Troubleshooting

### Port Already in Use

If port 8000 is taken, edit `.env`:

```bash
MOODIFY_API_PORT=8001
```

Then update docker-compose.yml ports mapping.

### Out of Memory

Reduce worker threads in `.env`:

```bash
MOODIFY_WORKER_THREADS=2
```

### Permission Denied

On Linux, fix volume permissions:

```bash
sudo chown -R $USER:$USER ./data ./temp ./models
```

## Next Steps

- Read [API Documentation](../moodify-core-package/src/moodify/api/README.md)
- Explore [Cloud Deployment](./cloud.md)
- Review [Production Requirements](./production.md)

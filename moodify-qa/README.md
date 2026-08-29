# Moodify QA API v0.2

**AI Audio Quality Assurance Infrastructure**

Moodify QA is a standalone B2B audio quality analysis API service, extracted from Moodify Engine's detection capabilities. It provides professional-grade audio quality assessment for businesses via REST API.

---

## 🎯 Product Positioning

**Moodify QA = AI Audio Quality Assurance API**

**Target Users:**
- 🤖 **AI Music Platforms** - Automated quality gates for generated audio
- 🎵 **Music Companies** - Quality control for catalogs and releases
- 📀 **Copyright Owners** - Asset quality verification
- 🎙️ **Recording Studios** - Technical validation for masters

**NOT a consumer app** - This is pure quality assurance infrastructure.

---

## 🚀 Quick Start

### Run with Docker

```bash
# Clone and start
git clone https://github.com/moodify-ai/moodify-qa.git
cd moodify-qa
docker-compose up

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn api.main:app --reload

# Or use the startup script
python api/main.py
```

---

## 📡 API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.2.0",
  "uptime_seconds": 3600,
  "queue_size": 0
}
```

### Analyze Single Audio

```bash
curl -X POST \
  http://localhost:8000/api/v1/qa/analyze \
  -F "file=@song.wav" \
  -F "webhook_url=https://your-app.com/webhook"
```

Response:
```json
{
  "task_id": "qa_a1b2c3d4e5f6",
  "status": "processing",
  "created_at": "2026-08-24T10:30:00",
  "estimated_seconds": 30,
  "message": "Analysis started. Use GET /qa/report/{task_id} to check status."
}
```

### Get Analysis Report

```bash
curl http://localhost:8000/api/v1/qa/report/qa_a1b2c3d4e5f6
```

Response:
```json
{
  "task_id": "qa_a1b2c3d4e5f6",
  "status": "completed",
  "file": {
    "name": "song.wav",
    "duration_seconds": 180.5,
    "sample_rate_hz": 44100,
    "channels": 2,
    "size_bytes": 31824044,
    "sha256": "a1b2c3d4..."
  },
  "qa_score": 86.5,
  "technical_score": 88.0,
  "musical_score": 84.0,
  "issues": [
    {
      "category": "dynamics",
      "severity": "warning",
      "message": "Low dynamic range (6.2 dB). Audio may sound compressed.",
      "metric": "dynamic_range_db",
      "value": 6.2,
      "threshold": 8.0
    }
  ],
  "recommendations": [
    {
      "issue_category": "dynamics",
      "priority": 1,
      "action": "Increase dynamic range",
      "details": "Current: 6.2 dB. Target: >8 dB. Reduce compression or use parallel processing."
    }
  ],
  "breakdown": {
    "technical": {
      "loudness": 95.0,
      "dynamics": 65.0,
      "clipping": 100.0,
      "noise": 90.0,
      "stereo": 95.0
    },
    "musical": {
      "balance": 85.0,
      "frequency": 80.0,
      "energy": 90.0
    }
  },
  "created_at": "2026-08-24T10:30:00",
  "completed_at": "2026-08-24T10:30:25"
}
```

### Batch Analysis

```bash
curl -X POST \
  http://localhost:8000/api/v1/qa/batch \
  -F "files=@song1.wav" \
  -F "files=@song2.wav" \
  -F "files=@song3.wav"
```

Response:
```json
{
  "batch_id": "batch_20260824_103000_a1b2c3d4",
  "task_ids": ["qa_001", "qa_002", "qa_003"],
  "total": 3,
  "status": "processing",
  "created_at": "2026-08-24T10:30:00",
  "estimated_seconds": 60
}
```

### Get Batch Report

```bash
curl http://localhost:8000/api/v1/qa/batch/batch_20260824_103000_a1b2c3d4
```

---

## 📊 QA Score Model v0.2

### Scoring Dimensions

**Technical Quality (60% weight):**
- **Loudness (15%)** - ITU-R BS.1770-5 integrated LUFS
- **Dynamics (15%)** - Dynamic range, crest factor, LRA
- **Clipping (15%)** - Sample and true peak detection
- **Noise (10%)** - Noise floor analysis
- **Stereo (5%)** - Correlation, M/S balance, phase

**Musical Quality (40% weight):**
- **Balance (15%)** - Frequency band energy distribution
- **Frequency Distribution (15%)** - Spectral flatness, rolloff
- **Energy Curve (10%)** - Silence detection, continuity

### Score Interpretation

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Excellent | Professional quality, ready for distribution |
| 80-89 | Good | Minor issues, acceptable for most use cases |
| 70-79 | Acceptable | Some issues that may need attention |
| 60-69 | Fair | Significant issues, review recommended |
| <60 | Poor | Major issues, not suitable for distribution |

---

## 🔗 Webhook Integration

Configure webhook URL to receive completion notifications:

```bash
curl -X POST \
  http://localhost:8000/api/v1/qa/analyze \
  -F "file=@song.wav" \
  -F "webhook_url=https://your-app.com/webhook"
```

Webhook payload:
```json
{
  "task_id": "qa_a1b2c3d4e5f6",
  "status": "completed",
  "qa_score": 86.5,
  "message": "Analysis completed successfully",
  "completed_at": "2026-08-24T10:30:25"
}
```

---

## 🏗️ Architecture

```
moodify-qa/
├── api/
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   └── qa.py            # API endpoints
│   ├── schemas/
│   │   └── report.py        # Pydantic models
│   ├── services/
│   │   └── analyzer_service.py  # Business logic
│   └── storage/
│       └── database.py      # SQLite/PostgreSQL storage
├── core/                    # Core analysis modules
│   ├── analyzer.py          # Audio analysis orchestrator
│   ├── metrics.py           # Individual metric calculators
│   ├── scoring.py           # QA Score model
│   └── report.py            # Report generation
├── cli.py                   # CLI interface
├── Dockerfile               # Container image
├── docker-compose.yml       # Orchestration
└── requirements.txt         # Dependencies
```

---

## 📋 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/version` | Version info |
| POST | `/api/v1/qa/analyze` | Analyze single audio |
| GET | `/api/v1/qa/report/{task_id}` | Get analysis report |
| POST | `/api/v1/qa/batch` | Batch analyze |
| GET | `/api/v1/qa/batch/{batch_id}` | Get batch report |
| GET | `/api/v1/qa/tasks` | List tasks |

### Rate Limits

- Single file: 100MB max
- Batch: 50 files max, 500MB total
- Rate: 100 requests/minute per IP

### Supported Formats

- WAV
- MP3
- FLAC
- AIFF
- OGG
- M4A

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t moodify-qa:latest .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  moodify-qa:latest
```

### Docker Compose

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 💼 Commercial Use Cases

### AI Music Platform Integration

```python
import requests

def quality_gate(audio_file_path: str) -> bool:
    """Quality gate for AI-generated music."""
    with open(audio_file_path, "rb") as f:
        response = requests.post(
            "http://moodify-qa:8000/api/v1/qa/analyze",
            files={"file": f}
        )

    result = response.json()

    # Poll for completion
    while result["status"] == "processing":
        time.sleep(1)
        result = requests.get(
            f"http://moodify-qa:8000/api/v1/qa/report/{result['task_id']}"
        ).json()

    # Quality gate: QA score >= 80
    return result["qa_score"] >= 80
```

### Music Catalog Processing

```python
def batch_process_catalog(audio_files: list[str]) -> dict:
    """Process entire music catalog."""
    files = [("files", open(f, "rb")) for f in audio_files]

    response = requests.post(
        "http://moodify-qa:8000/api/v1/qa/batch",
        files=files,
        data={"webhook_url": "https://my-app.com/batch-complete"}
    )

    return response.json()
```

---

## 🛣️ Roadmap

### v0.2 (Current)
- ✅ FastAPI service
- ✅ Async processing with BackgroundTasks
- ✅ SQLite storage
- ✅ Batch analysis
- ✅ Webhook support
- ✅ Docker deployment

### v0.3 (Planned)
- 📋 PostgreSQL support
- 📋 Redis task queue
- 📋 Celery workers
- 📋 Authentication (API keys)
- 📋 Rate limiting

### v0.4 (Planned)
- 📋 Historical trending
- 📋 Comparative analysis
- 📋 Custom scoring profiles
- 📋 Enterprise SSO
- 📋 Usage analytics

---

## 📄 License

GPL-3.0-only

Copyright (c) 2024-2026 荣景文川

---

## 📞 Contact

For business inquiries:
- Email: business@moodify.ai
- Website: https://moodify.ai

---

**Moodify QA** - *Professional audio quality assurance, powered by AI.*

# Moodify SDK Design

## Overview

This document describes the SDK architecture for Moodify auditory intelligence platform.

## Architecture

```
External Application
        ↓
    Moodify SDK
        ↓
    Moodify API
        ↓
Auditory Intelligence Engine
```

## Design Principles

### 1. Developer Experience

- Simple, intuitive API
- Clear documentation
- Type hints throughout
- Helpful error messages

### 2. Future Compatibility

- Extensible models
- Versioned API support
- Backward compatibility
- Graceful degradation

### 3. Language Support

**Phase 1**: Python (current)
**Phase 2**: JavaScript/TypeScript
**Phase 3**: Go, Rust
**Phase 4**: Mobile SDKs (iOS, Android)

## SDK Structure

### Python SDK

```
sdk/python/
├── __init__.py          # Package exports
├── client.py            # Main client classes
├── models.py            # Data models
└── exceptions.py          # Error handling
```

### Client Design

```python
class MoodifyClient:
    """Synchronous client."""

    def analyze_audio(self, path) -> AudioAnalysisResult
    def evaluate_audio(self, path) -> MRSResult
    def process_audio(self, path, operation) -> ProcessingResult
```

```python
class AsyncMoodifyClient:
    """Asynchronous client (future)."""

    async def analyze_audio(self, path) -> AudioAnalysisResult
    async def evaluate_audio(self, path) -> MRSResult
    async def process_audio(self, path, operation) -> ProcessingResult
```

## Data Models

### AudioAnalysisResult

```python
@dataclass
class AudioAnalysisResult:
    id: str
    audio_path: str
    duration: float
    sample_rate: int
    features: Dict[str, Any]
    metadata: Dict[str, Any]
```

### MRSResult

```python
@dataclass
class MRSResult:
    id: str
    audio_path: str
    overall: float      # 0-100
    fidelity: float     # 0-100
    balance: float      # 0-100
    clarity: float      # 0-100
    version: str
```

### ProcessingResult

```python
@dataclass
class ProcessingResult:
    id: str
    input_path: str
    output_path: str
    operation: str
    status: str         # pending/processing/completed/failed
    progress: float     # 0-100
```

## Error Handling

### Exception Hierarchy

```
MoodifyError (base)
├── APIError
│   ├── RateLimitError
│   ├── ServerError
│   ├── NotFoundError
│   └── ConflictError
├── ValidationError
├── AuthenticationError
├── TimeoutError
├── ConnectionError
└── ProcessingError
```

### Usage

```python
from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError

client = MoodifyClient(api_key="xxx")

try:
    result = client.analyze_audio("audio.wav")
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e.status_code}")
```

## Authentication

### API Key

```python
client = MoodifyClient(api_key="mk_live_xxx")
```

### Environment Variable

```bash
export MOODIFY_API_KEY="mk_live_xxx"
```

```python
client = MoodifyClient()  # Reads from env
```

## Configuration

### Client Options

```python
client = MoodifyClient(
    api_key="xxx",
    base_url="https://api.moodify.ai",
    timeout=30.0,
    max_retries=3
)
```

## API Mapping

| SDK Method | API Endpoint | Method |
|------------|--------------|--------|
| `analyze_audio()` | `/api/v1/analyze` | POST |
| `evaluate_audio()` | `/api/v1/evaluate` | POST |
| `process_audio()` | `/api/v1/process` | POST |
| `health_check()` | `/health` | GET |

## Future Enhancements

### Batch Operations

```python
results = client.analyze_batch([
    "file1.wav",
    "file2.wav",
    "file3.wav"
])
```

### Webhooks

```python
client.register_webhook(
    url="https://my-app.com/webhook",
    events=["processing.completed"]
)
```

### Streaming

```python
for chunk in client.stream_analysis("large-file.wav"):
    print(chunk.progress)
```

### Caching

```python
client = MoodifyClient(
    cache_enabled=True,
    cache_ttl=3600
)
```

## Versioning

### SDK Version

- Semantic versioning (MAJOR.MINOR.PATCH)
- Version in `__version__`
- Changelog maintained

### API Version

- SDK supports multiple API versions
- Default to latest stable
- Version can be specified:

```python
client = MoodifyClient(
    api_key="xxx",
    api_version="v1"
)
```

## Testing

### Unit Tests

```python
def test_analyze_audio():
    client = MoodifyClient(api_key="test")
    result = client.analyze_audio("test.wav")
    assert result.duration > 0
```

### Mock Client

```python
from moodify.testing import MockMoodifyClient

client = MockMoodifyClient()
result = client.analyze_audio("test.wav")
# Returns mock data
```

## Documentation

### Code Documentation

- Docstrings for all public methods
- Type hints
- Examples in docstrings

### User Documentation

- README with quick start
- Examples directory
- API reference
- Migration guides

## Distribution

### PyPI

```bash
pip install moodify-sdk
```

### Conda

```bash
conda install -c moodify moodify-sdk
```

### Source

```bash
git clone https://github.com/huliye24/moodify-ai.git
cd moodify-ai/sdk/python
pip install -e .
```

## References

- [Python SDK README](../sdk/python/README.md)
- [Examples](../sdk/examples/)
- [API Documentation](../docs/api-reference.md) (future)

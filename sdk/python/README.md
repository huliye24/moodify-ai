# Moodify Python SDK

## Installation

```bash
# Future: pip install moodify-sdk
# Current: Copy this directory to your project
```

## Requirements

- Python 3.10+
- httpx (for HTTP client)
- pydantic (for data models)

## Quick Start

```python
from moodify import MoodifyClient

# Create client
client = MoodifyClient(
    api_key="your-api-key",
    base_url="https://api.moodify.ai"
)

# Analyze audio
result = client.analyze_audio("audio.wav")
print(result)
```

## Client Configuration

```python
from moodify import MoodifyClient

# With custom settings
client = MoodifyClient(
    api_key="mk_live_xxx",
    base_url="https://api.moodify.ai",
    timeout=30.0,
    max_retries=3
)
```

## Error Handling

```python
from moodify import MoodifyClient
from moodify.exceptions import APIError, ValidationError

client = MoodifyClient(api_key="xxx")

try:
    result = client.analyze_audio("audio.wav")
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

## Async Support (Future)

```python
from moodify import AsyncMoodifyClient

async def main():
    client = AsyncMoodifyClient(api_key="xxx")
    result = await client.analyze_audio("audio.wav")
```

## Models

See [models.py](./models.py) for data model definitions.

## Exceptions

See [exceptions.py](./exceptions.py) for error types.

## License

Copyright © 2024-2026 荣景文川
SPDX-License-Identifier: GPL-3.0-only

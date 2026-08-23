# Moodify SDK

## Overview

Moodify SDK provides developer-friendly access to auditory intelligence capabilities.

## Target Users

- AI music developers
- Music software companies
- Audio researchers
- Creative tools developers

## Core Capabilities

### Audio Analysis

Extract deep auditory features from audio:

- Temporal texture analysis
- Multi-scale representation
- Acoustic balance metrics
- Spectral characteristics

### MRS Evaluation

Moodify Reconstruction Score for quality assessment:

- Overall quality score
- Fidelity assessment
- Balance evaluation
- Clarity metrics

### Audio Processing

Apply intelligent audio processing:

- Reconstruction processing
- Quality enhancement
- Format conversion
- Batch operations

## SDK Structure

```
sdk/
├── README.md              # This file
├── python/               # Python SDK
│   ├── README.md
│   ├── client.py         # Main client
│   ├── models.py         # Data models
│   └── exceptions.py     # Error handling
└── examples/             # Usage examples
    ├── analyze_audio.py
    ├── evaluate_audio.py
    └── process_audio.py
```

## Quick Start

### Installation

```bash
# Future: pip install moodify-sdk
# Current: Copy sdk/python to your project
```

### Basic Usage

```python
from moodify import MoodifyClient

# Initialize client
client = MoodifyClient(api_key="your-api-key")

# Analyze audio
result = client.analyze_audio("path/to/audio.wav")
print(f"Duration: {result.duration}")
print(f"Features: {result.features}")

# Evaluate quality
mrs = client.evaluate_audio("path/to/audio.wav")
print(f"MRS Score: {mrs.overall}")
```

## Authentication

### API Key (Future)

```python
client = MoodifyClient(api_key="mk_live_xxxxxxxx")
```

### Environment Variable (Future)

```bash
export MOODIFY_API_KEY="mk_live_xxxxxxxx"
```

```python
client = MoodifyClient()  # Reads from env
```

## API Reference

See [Python SDK README](./python/README.md) for detailed API documentation.

## Examples

See [examples/](./examples/) for complete working examples.

## Status

**Current**: SDK structure and interface design

**Future**: Full implementation when API is ready

## Contributing

Contributions welcome. See main project contributing guidelines.

## License

Copyright © 2024-2026 荣景文川
SPDX-License-Identifier: GPL-3.0-only

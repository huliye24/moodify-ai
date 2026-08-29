# Dataset Schema

This document defines the data structures for the Moodify Audio Benchmark framework.

## Audio Sample

The fundamental unit of the benchmark dataset.

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AudioSample",
  "type": "object",
  "required": ["id", "audio_path", "source", "duration"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier for the sample",
      "pattern": "^[a-zA-Z0-9_-]+$")
    },
    "audio_path": {
      "type": "string",
      "description": "Relative path to the audio file (not stored in repo)"
    },
    "source": {
      "type": "string",
      "description": "Origin of the audio",
      "enum": ["original", "ai_generated", "processed", "synthetic", "unknown"]
    },
    "genre": {
      "type": "string",
      "description": "Musical genre or style",
      "examples": ["pop", "classical", "jazz", "electronic", "rock"]
    },
    "duration": {
      "type": "number",
      "description": "Duration in seconds",
      "minimum": 0
    },
    "sample_rate": {
      "type": "integer",
      "description": "Audio sample rate in Hz",
      "examples": [44100, 48000, 96000]
    },
    "channels": {
      "type": "integer",
      "description": "Number of audio channels",
      "minimum": 1,
      "maximum": 2
    },
    "technical_features": {
      "type": "object",
      "description": "Extracted technical audio features",
      "properties": {
        "loudness_lufs": {
          "type": "number",
          "description": "Integrated loudness in LUFS"
        },
        "true_peak_db": {
          "type": "number",
          "description": "True peak level in dB"
        },
        "dynamic_range_db": {
          "type": "number",
          "description": "Dynamic range in dB"
        },
        "spectral_centroid_hz": {
          "type": "number",
          "description": "Spectral centroid in Hz"
        },
        "spectral_rolloff_hz": {
          "type": "number",
          "description": "Spectral rolloff frequency in Hz"
        },
        "zero_crossing_rate": {
          "type": "number",
          "description": "Zero crossing rate"
        },
        "rms_energy": {
          "type": "number",
          "description": "Root mean square energy"
        }
      }
    },
    "mrs_score": {
      "type": "object",
      "description": "Moodify Reconstruction Score (if applicable)",
      "properties": {
        "overall": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "fidelity": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "balance": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "clarity": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "version": {
          "type": "string",
          "description": "MRS algorithm version"
        }
      }
    },
    "human_rating": {
      "type": "object",
      "description": "Aggregated human evaluation scores",
      "properties": {
        "mean_rating": {
          "type": "number",
          "minimum": 1,
          "maximum": 5
        },
        "std_dev": {
          "type": "number",
          "description": "Standard deviation of ratings"
        },
        "num_ratings": {
          "type": "integer",
          "minimum": 0
        },
        "preference_rank": {
          "type": "integer",
          "description": "Rank in preference comparison"
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata",
      "properties": {
        "created_at": {
          "type": "string",
          "format": "date-time"
        },
        "processed_at": {
          "type": "string",
          "format": "date-time"
        },
        "pipeline_version": {
          "type": "string"
        },
        "model_name": {
          "type": "string",
          "description": "Name of AI model if AI-generated"
        },
        "model_version": {
          "type": "string"
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

## Dataset Collection

### Collection Manifest

```json
{
  "dataset_id": "string",
  "name": "string",
  "description": "string",
  "version": "string",
  "created_at": "ISO-8601 timestamp",
  "num_samples": integer,
  "sources": ["array of sources"],
  "license": "string",
  "audio_location": "path or URL to audio files",
  "samples": ["array of AudioSample objects"]
}
```

## Data Storage Policy

1. **Audio Files**: Not stored in this repository. Referenced by `audio_path` only.
2. **Metadata**: Stored as JSON in `samples/` directory.
3. **Human Ratings**: Anonymized and aggregated before storage.
4. **Copyright Compliance**: Only public domain or properly licensed audio.

## Validation Rules

- All `id` values must be unique within a dataset
- `audio_path` must be resolvable relative to the dataset root
- `duration` must be positive and reasonable (< 3600s for most cases)
- `technical_features` should be computed using standardized methods
- `human_rating` requires minimum 3 ratings for statistical validity

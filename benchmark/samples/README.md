# Samples Directory

This directory contains metadata for audio samples used in the Moodify Audio Benchmark.

## Structure

Each sample is represented by a JSON file following the schema defined in `../dataset_schema.md`.

## Audio File Policy

**Important**: Audio files are NOT stored in this repository.

- Only metadata JSON files are committed
- Audio files are referenced by `audio_path` relative to a dataset root
- Dataset maintainers must ensure proper licensing

## Sample Metadata Example

```json
{
  "id": "sample_001",
  "audio_path": "audio/pop/sample_001.wav",
  "source": "original",
  "genre": "pop",
  "duration": 30.0,
  "sample_rate": 44100,
  "channels": 2,
  "technical_features": {
    "loudness_lufs": -14.2,
    "true_peak_db": -1.1,
    "spectral_centroid_hz": 2500
  },
  "metadata": {
    "created_at": "2026-08-23T10:00:00Z",
    "tags": ["vocal", "stereo"]
  }
}
```

## Adding Samples

1. Ensure audio file is properly licensed
2. Run baseline evaluation: `python ../baseline.py evaluate -i <audio>`
3. Save metadata to this directory
4. Update dataset manifest

## License

Sample metadata follows the project license.
Audio files must be separately licensed.

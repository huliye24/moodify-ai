# CLI DAW PROJECT SCHEMA v1.0.0

## Core Model

```yaml
schema_version: "1.0.0"
project_id: string
sample_rate: 44100
tempo: 120.0  # optional
tracks:
  - track_id: string
    name: string
    source: {path: string, hash: string}
    clips: [{clip_id, source_offset_s, position_s, duration_s, fade_in_s, fade_out_s, gain_db, pan, mute, solo}]
buses:
  - bus_id: string
    name: string
    sends: [{track_id, gain_db}]
master:
  processing: [{node_id, type: gain|eq|compressor|limiter, params: {}}]
processing:
  track_id: [{node_id, type, order, params}]
render:
  sample_rate: 44100
  bit_depth: 24
  format: wav
```

## Rules
- source.hash validated against disk before render
- Unknown node type → fail closed
- Cyclic bus routing → fail closed
- Duplicate clip_id/track_id → fail closed

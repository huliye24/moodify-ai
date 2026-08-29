# Moodify Products

> Industry-facing product modules built on the Moodify Intelligence Engine.

## Product Modules

| Product | Full Name | Responsibility |
|---------|-----------|---------------|
| `qa` | AI Music Quality Assurance | Audio quality detection, LUFS analysis, spectral analysis, MRS scoring |
| `master` | AI Music Mastering Engine | AI mastering, sound optimization, commercial release standardization |
| `rating` | AI Music Asset Rating | Music value scoring, commercial potential, emotion tags, asset grading |
| `supply` | AI Music Supply Chain | Music search, scene matching, stem separation, commercial use fulfillment |

## Architecture

Each product:
- Depends on `engine/` for AI auditory capabilities
- Exposes its own API namespace (`/api/v1/{product}/...`)
- Has its own configuration (`config.yaml`)
- Maintains its own presets and standards

## Migration Status

New directory structure. Modules will be progressively migrated from `moodify-core-package/`. See `docs/MOODIFY_ARCHITECTURE_V1.md`.

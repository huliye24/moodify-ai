# Moodify Supply — AI Music Supply Chain

> Music search, scene matching, and commercial use fulfillment infrastructure.

## Responsibilities

- **Music Search** — Audio similarity search, metadata search, semantic search
- **Scene Matching** — Match music to game, film, advertising, and streaming contexts
- **Supply Pipeline** — Intake → Process → Deliver → Verify
- **Stem Separation** — AI-powered source separation (vocals, drums, bass, other)
- **License Matching** — Rights and licensing compatibility
- **Commercial Use Fulfillment** — End-to-end music supply for commercial projects

## Module Structure

```
products/supply/
├── search/            # Audio & metadata search
├── matching/          # Scene, mood, tempo, license matching
├── pipeline/          # Intake, process, deliver, verify
├── stems/             # Stem separation & storage
└── api/               # Supply API routes
```

## Migration Source

| Supply Module | Source (moodify-core-package) |
|---------------|------------------------------|
| `stems/separator.py` | `stems/service.py` |
| `stems/store.py` | `stems/store.py` |
| `pipeline/intake.py` | `data_factory/case_runner.py` |
| `pipeline/process.py` | `data_factory/runner.py` |
| `pipeline/deliver.py` | `data_plane/delivery.py` |
| `pipeline/verify.py` | `data_factory/verification_contract.py` |

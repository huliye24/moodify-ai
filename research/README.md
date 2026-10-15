# Moodify Research

> Research papers, benchmarks, whitepapers, and experimental modules.

## Structure

```
research/
├── papers/            # Published research papers
├── benchmarks/        # Benchmark datasets & results
├── hear_judge/        # Replaceable HEAR providers and Judge evaluation work
├── matlab/            # MATLAB R2023b studies, campaigns, charts, and data
├── whitepapers/       # Industry whitepapers
└── experimental/      # Experimental modules (MAMSE-001..016)
```

## Current Papers

- `WSE-AIM-001_Wave-Spectral_Evolution.pdf` — Wave-Spectral Evolution research
- `WSE-AIM-002_MIDI-Score-Anchored_Post-Production.pdf` — MIDI/Score-anchored post-production
- `Moodify_Three_Layer_Research_Architecture_Edition_0.1.pdf` — Three-layer research architecture

## HEAR / Judge

External audio models are absorbed as replaceable sensors, representations,
hands, or evaluation baselines.  They do not acquire Moodify Judge authority.
See [`hear_judge/README.md`](hear_judge/README.md).

## Three production research questions

[`THREE_PRODUCTION_RESEARCH_QUESTIONS.md`](THREE_PRODUCTION_RESEARCH_QUESTIONS.md)
organizes the current finishing research into three evidence domains: vocal
authenticity, accompaniment coherence, and production completion.  These are
research questions under one Core and one Judge, not three products or three
independent scoring authorities.

## MATLAB laboratory

[`matlab/`](matlab/README.md) is an **EXPERIMENTAL** evidence-producing laboratory.
It contains reproducible studies and a long-running campaign runner; it does not
replace Moodify Core or promote experimental measurements to production truth.

## Migration

Experimental modules (`moodify_experimental/` with MAMSE-001..016) will be migrated to `research/experimental/` in Phase C.

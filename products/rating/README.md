# Moodify Rating — AI Music Asset Rating

> Music asset intelligence: value scoring, commercial potential, and emotion tagging.

## Responsibilities

- **Music Value Scoring** — Commercial, artistic, and technical value assessment
- **Commercial Potential Analysis** — Market fit, licensing potential, monetization paths
- **Emotion & Mood Tagging** — Automated emotional characterization
- **Asset Grading** — S/A/B/C/D tier classification
- **Risk Assessment** — Copyright risk, quality risk, originality assessment
- **Scene & Usage Tags** — Game, film, advertising, streaming suitability

## Module Structure

```
products/rating/
├── evaluation/        # Value scoring & grading
├── tagging/           # Emotion, scene, genre, quality tags
├── analysis/          # Market fit, risk, identity ranking
└── api/               # Rating API routes
```

## Migration Source

| Rating Module | Source (moodify-core-package) |
|---------------|------------------------------|
| `evaluation/value_scorer.py` | `mrs/scoring.py` |
| `evaluation/judge_panel.py` | `evaluation/judges.py` |
| `tagging/emotion_tags.py` | `knowledge/emotion_targets.py` |
| `analysis/risk_assessment.py` | `knowledge/risk_model.py` |
| `analysis/identity_ranking.py` | `identity_guard/ranking.py` |

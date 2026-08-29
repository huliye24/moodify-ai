# Engine / Report Schema

Unified **Moodify Intelligence Report** contract (`moodify.intelligence-report.v1`).

Every Moodify product consumes and produces this shape:

| Product   | Usage                                            |
|-----------|--------------------------------------------------|
| QA        | Fill `issues` + `quality_score` as the QA verdict |
| Master    | Read `issues`/`recommendations` as mastering objectives |
| Rating    | Extend `commercial_insight` for asset grading     |
| Supply    | Use `audio_features` for similarity/matching      |
| Demo      | End-to-end showcase of the full report            |

## Files

- `schema.py` — Python dataclasses + serializer + structural validator (no external deps)
- `moodify_intelligence_report.schema.json` — formal JSON Schema (draft 2020-12) for
  API contracts and third-party integration

## Usage

```python
from engine.report_schema.schema import (
    IntelligenceReport, validate_report_dict
)

report_dict = report.to_dict()
problems = validate_report_dict(report_dict)   # [] == valid
```

## Stability

Fields are append-only within a schema version. Breaking changes require a new
schema id (`...v2`) and a migration note in `docs/canon/CANON_CHANGELOG.md`
(schema is an evidence contract — see AGENTS.md).

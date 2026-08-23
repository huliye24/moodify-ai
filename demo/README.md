# Moodify Demo — Intelligence Pipeline

One upload → one professional AI audio intelligence report.
The smallest closed loop that demonstrates the value of the Moodify
Intelligence Engine.

```text
song.mp3  →  moodify analyze song.mp3  →  Moodify Intelligence Report
```

## Quick Start

```bash
# Option 1: install the CLI
pip install -e demo
moodify analyze demo/input/example.mp3

# Option 2: run without installing (repo root)
python -m demo.cli analyze demo/input/example.mp3
```

Outputs (written to `demo/output/<track name>/` by default):

| File | Content |
|---|---|
| `report.json` | Machine-readable report (unified schema, for API/product use) |
| `report.md` | Full human-readable report |
| terminal | Compact summary with overall score, issues, recommendations |

## Architecture — the demo owns nothing

The demo module contains **zero analysis logic**. It only orchestrates the
engine and renders the report:

```text
demo/cli.py ──▶ demo/analyzer/pipeline.py ──▶ engine/  (Moodify Intelligence Engine)
                                             ├─ acoustic_analysis   measurement + issue detection
                                             ├─ scoring_engine      MRS baseline scoring + recommendations
                                             ├─ music_understanding commercial insight
                                             └─ report_schema       unified report contract
                                                     │
                                                     ▼
                                        moodify-core-package  (existing, tested implementation)
                                        ▼
demo/report/generator.py ──▶ report.json / report.md / terminal summary
```

Because every capability lives in the engine, the future products reuse the
exact same chain:

- **Moodify QA** — `analyze_track` + `detect_issues` + `quality_score`
- **Moodify Master** — `issues` + `recommendations` as mastering objectives
- **Moodify Rating** — `commercial_insight` + scores for asset grading
- **Moodify Supply** — `audio_features` for search / scene matching

## Directory

```text
demo/
├── input/       example.mp3 — bundled demo track
├── analyzer/    pipeline.py — engine orchestration (no math)
├── report/      generator.py — JSON / Markdown / terminal rendering
├── tests/       end-to-end + rendering tests
├── cli.py       `moodify analyze` entry point
└── pyproject.toml
```

See `docs/MOODIFY_DEMO_PIPELINE.md` for design rationale and the
product-mapping plan.

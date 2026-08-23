# Moodify Intelligence Demo Pipeline

**Status:** Live (Phase B T0.5) · **Engine version:** 0.1.0 · **Report schema:** `moodify.intelligence-report.v1`

One upload → one professional AI audio intelligence report. The smallest closed
loop that demonstrates the value of the Moodify Intelligence Engine — built
**before** Phase B module migration (T1+) so every migrated module lands into a
working, externally showable pipeline instead of a dead directory structure.

```bash
moodify analyze demo/input/example.mp3     # or: python -m demo.cli analyze ...
```

```text
==========================================================
             Moodify Intelligence Report
==========================================================
  Track          : example.mp3
  Overall Score  : 63 / 100
  Loudness       : -15.6 LUFS (LRA 3.3 LU)
  ...
  Moodify Analysis:
   "This track has strong emotional potential but requires additional
    mastering optimization for commercial release."
==========================================================
```

---

## 1. Why a Demo Pipeline (before migration)

| Problem without it | What the demo solves |
|---|---|
| `engine/` and `products/` are empty shells after Phase A | Engine facade is now **live code** with real measurements |
| Migrating code with no consumer = migration without verification | Every migrated module gets an immediate end-to-end consumer test |
| Nothing to show investors / industry partners | A 30-second demo: upload a song, get a professional report |
| Report format would be invented per-product later | One report contract (`engine/report_schema`) designed once, reused by all |

Principle (from the task brief): *这是 Moodify 从"项目代码"向"产业基础设施"的第一个外部展示节点。*
The demo is deliberately small — one file in, one report out, complete.

## 2. Technical Flow

```text
demo/cli.py  "moodify analyze song.mp3"
   │
   ▼
demo/analyzer/pipeline.py          (orchestration only — no math)
   │
   ▼  engine/  — Moodify Intelligence Engine
   ├─ acoustic_analysis/analyzer.py ──▶ moodify-core-package
   │     ├─ moodify.v01_analyzer            band spectrum · peak · crest · dyn range · L/R corr
   │     └─ moodify.auditory.loudness       ITU-R BS.1770-5 LUFS · EBU Tech 3342 LRA
   ├─ acoustic_analysis/issue_detection.py  transparent rule-based diagnosis (evidence-cited)
   ├─ scoring_engine/quality.py             measurement → MRSFeatures → RuleBasedMRSScorer
   ├─ scoring_engine/recommendations.py     issue → recommendation mapping
   ├─ music_understanding/commercial_insight.py   release-readiness verdict
   └─ report_schema/                        unified Intelligence Report contract
   │
   ▼
demo/report/generator.py           report.json · report.md · terminal summary
```

Key properties:

- **Demo owns no analysis logic.** `demo/analyzer/pipeline.py` only composes
  engine calls. The same chain is what QA / Master / Rating will call.
- **Engine owns no duplicate math.** All measurement delegates to the existing,
  tested implementation in `moodify-core-package` (via `engine/_compat.py`,
  a temporary bootstrap that T1's shim mechanism will replace).
- **Scoring is the legacy MRS baseline.** `engine/scoring_engine/quality.py`
  normalizes measurements into the `MRSFeatures` contract and calls the
  existing `RuleBasedMRSScorer` — no second scoring implementation
  (AGENTS.md: no second authority).
- **Overall score combination is explicit:**
  `overall = MRS quality − severity penalties (high 12 / medium 5 / low 1)`,
  documented here so it is auditable, not magical.

## 3. The Report Contract

`engine/report_schema/` defines `moodify.intelligence-report.v1`:

| Section | Content | Primary consumer |
|---|---|---|
| `track_info` | file, format, duration, sr, channels | all |
| `audio_features` | LUFS / LRA / peak / crest / spectrum bands / dynamics / stereo | QA, Supply |
| `quality_score` | overall, audio quality, dynamic range, raw MRS result | QA, Rating |
| `issues` | id / severity / title / detail / **evidence** | QA, Master |
| `recommendations` | action / target / rationale / priority | Master |
| `commercial_insight` | summary / release readiness / strengths / risks | Rating, Sales |
| `meta` | schema id, engine version, timestamp | evidence chain |

Both a Python API (`schema.py`, dataclasses + structural validator, zero deps)
and a formal JSON Schema (`moodify_intelligence_report.schema.json`) are
published. Fields are append-only within v1; breaking changes require a v2
schema id and a Canon changelog entry (the schema is an evidence contract).

## 4. Future Product Mapping

| Product | Reuses | Adds |
|---|---|---|
| **Moodify QA** | `analyze_track` + `detect_issues` + `quality_score` | verdict UI, batch QA jobs, distribution-standard gates (-14 LUFS etc.) |
| **Moodify Master** | `issues` + `recommendations` as objectives | actual intervention chain (identity gate, safety bounds), A/B verify |
| **Moodify Rating** | `commercial_insight` + scores | S/A/B/C/D asset tiers, market-fit tags, valuation inputs |
| **Moodify Supply** | `audio_features` | similarity search, scene matching, licensing pipeline |

Migration targets (Phase B): each row migrates the listed engine calls into
its `products/<name>/` module while the demo keeps running unchanged — the
report contract is the stability guarantee.

## 5. Commercial Uses

- **Investor / partner demo:** one command, one professional report — the
  fastest way to show what "auditory intelligence infrastructure" means.
- **Lead generation:** embed the loop on the website ("upload a track, get a
  free quality report") — every upload is a qualified music-industry lead.
- **Sales enablement:** the `report.md` format is a deliverable a mastering
  engineer or label manager can read without any Moodify context.
- **Evidence discipline:** every issue carries evidence; every score is
  traceable to measurements — matching AGENTS.md's judgment-authority rules.

## 6. Limits (honest scope)

- MRS baseline is rule-based, `listening_score` is deliberately `null` —
  no claim of human-preference measurement without validation.
- Rule thresholds (e.g. harshness at presence−mid > 2 dB) are transparent
  defaults, to be calibrated by the Asset Loop as evidence accumulates.
- `engine/_compat.py` is temporary; T1 replaces it with a proper shim/adapter.

## 7. Files

```text
engine/
├── _compat.py                                # temp bootstrap to core-package
├── acoustic_analysis/analyzer.py             # measurement facade
├── acoustic_analysis/issue_detection.py      # rule-based diagnosis
├── scoring_engine/quality.py                 # MRS adapter + scoring
├── scoring_engine/recommendations.py         # issue → fix mapping
├── music_understanding/commercial_insight.py # readiness verdict
└── report_schema/                            # unified report contract (py + json)

demo/
├── input/example.mp3        # bundled demo track ("Silk and Ruin2")
├── analyzer/pipeline.py     # engine orchestration (no analysis logic)
├── report/generator.py      # json / markdown / terminal rendering
├── cli.py                   # `moodify analyze`
├── tests/                   # 9 tests: schema + end-to-end pipeline
└── pyproject.toml           # console_scripts entry: moodify
```

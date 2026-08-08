# Complexity Inventory — DSK-MFY-ONE-POINT-006

## Purpose

Classify every Moodify internal concept against the singular center: **让这首音乐成为它自己（成全市不是改造）**.

## Classification Key

| Label | Meaning | Default behavior |
|---|---|---|
| `VISIBLE` | Operator must understand to complete the task | Rendered in default surface |
| `PROGRESSIVE` | Needed for depth but not for first reading | Expandable on request |
| `INTERNAL` | Required for correctness but not for narrative | Saved in evidence, hidden from default |
| `DEFER` | Not yet stable enough for default surface | Documented, withheld from default |

## Inventory

### 1. Input Identity

| Concept | Contribution to center | Classification | Evidence path |
|---|---|---|---|
| Source asset (path, SHA-256, bytes) | "What this work is" — the thing itself | `VISIBLE` | evidence/ledger |
| Rights status | "What must be respected" | `VISIBLE` | evidence/rights |
| Asset kind (audio/stem/midi/lyrics) | Structural honesty about input shape | `PROGRESSIVE` | evidence/assets |
| Case ID | Traceability anchor | `PROGRESSIVE` | evidence/case |

### 2. Essence & Protection

| Concept | Contribution to center | Classification | Evidence path |
|---|---|---|---|
| essence (plain-language description) | "This work is..." — what already exists | `VISIBLE` | result.json, summary.md |
| must_preserve | "This must survive" — identity contract | `VISIBLE` | result.json, summary.md |
| must_avoid | "This must not happen" — negative constraints | `VISIBLE` | result.json, summary.md |
| desired_change | "What is being sought" — the ask | `VISIBLE` | result.json, summary.md |
| human_owner | "Who decides" — human sovereignty anchor | `VISIBLE` | result.json, summary.md |

### 3. Action & Evidence

| Concept | Contribution to center | Classification | Evidence path |
|---|---|---|---|
| WSE — Waveform Sound Evidence | "What the sound actually is" — measurement, not judgment | `INTERNAL` | evidence/wse |
| MSE — Music Structure Evidence | "What the musical form is" — structural measurement | `INTERNAL` | evidence/mse |
| PPE — Production Process Evidence | "How the production was conducted" — process, not product | `INTERNAL` | evidence/ppe |
| Treatment Plan | "What the system intends to do" — planned action | `PROGRESSIVE` | evidence/plan |
| Candidate | "What was tried" — versions, not verdicts | `PROGRESSIVE` | evidence/candidates |
| Gate (six-gate evaluation) | "What gates were checked" — technical safety | `PROGRESSIVE` | evidence/gates |
| MRS — Moodify Rating System | Technical scoring, not aesthetic judgment | `INTERNAL` | evidence/mrs |
| Craft / Craft Memory | "What was learned" — reusable knowledge | `PROGRESSIVE` | evidence/craft |
| MeasurementRecord | "What was measured" — raw data, not conclusions | `INTERNAL` | evidence/measurements |
| Comparison metrics | "How outputs differ" — deltas, not rankings | `INTERNAL` | evidence/comparisons |

### 4. Process & Audit

| Concept | Contribution to center | Classification | Evidence path |
|---|---|---|---|
| Ledger (DuckDB) | Immutable event log | `INTERNAL` | evidence/ledger |
| Rule state transitions | "How rules mature" — governance, not output | `INTERNAL` | evidence/rules |
| Human Approval (explicit record) | "Who approved what" — jurisdictional evidence | `PROGRESSIVE` | evidence/approvals |
| ValidationResult | "What checks passed or failed" | `PROGRESSIVE` | evidence/validations |
| Environment info | "Under what conditions" — reproducibility | `PROGRESSIVE` | evidence/environment |
| Run manifest | "What happened in this run" | `PROGRESSIVE` | run_manifest.json |
| Regression / Golden replay | "Can we reproduce it" | `INTERNAL` | evidence/regression |

### 5. Deferred from Default Surface

| Concept | Reason for DEFER | Where it lives |
|---|---|---|
| Experiment tracking | Not yet production-hardened | schemas, future Stage |
| MIDI/Score reconstruction | Research-phase, fragile | MSE experimental |
| Operator Console | Internal debug only | Runtime, hidden |
| Workspace UI | Internal verification | Runtime, hidden |
| Cloud worker / queue | Infrastructure, not product language | Runtime |
| Atomic pair writer | Infrastructure detail | Runtime |
| Learning surface / data loop | Experimental, not production-ready | Runtime experimental |
| Fusion scorer | Alpha, not validated | Runtime experimental |

## Summary

| Classification | Count |
|---|---|
| VISIBLE | 9 |
| PROGRESSIVE | 9 |
| INTERNAL | 7 |
| DEFER | 8 |
| **Total classified** | **33** |

The default surface expresses 9 concepts. All complexity remains findable through evidence paths. No concept is deleted.

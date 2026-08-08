# Subtraction Ledger — DSK-MFY-ONE-POINT-006

## Principle

Every concept hidden from the default surface was a deliberate choice. Each entry records what was removed from view, why, and where it can still be found.

## Hidden Concepts (removed from default surface but preserved in evidence)

| Concept | Where hidden | Reason |
|---|---|---|
| WSE — Waveform Sound Evidence | `evidence/` | Internal measurement layer; not needed for human reading |
| MSE — Music Structure Evidence | `evidence/` | Research/experimental layer |
| PPE — Production Process Evidence | `evidence/` | Process metadata, not product narrative |
| MRS — Moodify Rating System | `evidence/` | Technical scoring, not aesthetic judgment |
| Gate IDs and statuses | `evidence/gates.json`, `result.json > gate_summary` | Technical checks, expanded on demand |
| MeasurementRecord values | `evidence/ledger` | Raw data, not conclusions |
| DuckDB ledger | `evidence/ledger/` | Immutable log, not reading material |
| Candidate IDs and parameters | `evidence/` | Versions, not verdicts |
| Rule state transitions | `evidence/` | Governance mechanics |
| Environment info (Python, packages) | `evidence/` | Reproducibility, not narrative |

## Merged Concepts (previously competing synonyms, now unified)

| Old terms | New unified term | Reason |
|---|---|---|
| enhance / improve / optimize / process / master | **refine** | Single honest action verb |
| input / raw / source / original | **source** | Identity anchor |
| output / result / final / deliverable | **candidate** or **result** (depending on context) | No premature finality |
| constraint / lock / preset / rule | **protect** | What must survive |
| risk / warning / error / side-effect | **avoid** | What must not occur |

## Deferred from Default (not yet stable)

| Concept | Reason deferred |
|---|---|
| Experiment tracking | Not production-hardened |
| Craft Memory writeback | Requires human approval gate |
| MIDI/Score reconstruction | Research-phase |
| Cloud worker / queue | Infrastructure, not product language |
| Operator Console | Internal debug only |
| Learning surface | Experimental |

## Rejected Additions

| Proposed concept | Reason rejected |
|---|---|
| Auto-generated "quality score" (single number) | Violates honesty: one number cannot represent identity |
| "Better/Worse" comparative rating | Subjective, no human evaluation baseline |
| "AI Confidence" percentage | Meaningless without calibrated reference |
| "Recommended" badge | Auto-final by another name |
| Dashboard with metric walls | Technology self-promotion, not artist service |

## Net Effect

| Metric | Count |
|---|---|
| Concepts hidden from default surface | 10 |
| Concepts merged (competing synonyms eliminated) | 10 |
| Concepts deferred | 6 |
| Rejected additions | 5 |
| **New concepts added to default surface** | **0** |
| **Default surface external words** | **12** (from LANGUAGE_CANON) |

The default surface expresses no new concepts. It reveals only what was always essential: what the work is, what must be protected, what may change, what was done, and who decides.

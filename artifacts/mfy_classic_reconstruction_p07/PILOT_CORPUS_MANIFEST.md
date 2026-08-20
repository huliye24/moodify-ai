# P07 Pilot Corpus Manifest

## Gate A (executed 2026-08-17) — SYNTHETIC STAND-IN

Real authorized corpus is pending human-provided material. Gate A used three
30-second synthetic tracks to verify pipeline stability, failure semantics and
outcome diversity (NOT a real corpus; never presented as one).

| Alias | Era hint | Character | Source hash (sha256, first 12) | Outcome |
|---|---|---|---|---|
| SYNTH_T01 | 1980s | high noise, limited bandwidth | (in GATE_A_SYNTHETIC.json) | IMPROVED |
| SYNTH_T02 | 1990s | moderate noise | (in GATE_A_SYNTHETIC.json) | SUBTLE_IMPROVEMENT |
| SYNTH_T03 | modern | clean, wide | (in GATE_A_SYNTHETIC.json) | SOURCE_WINS |

Healthy distribution: not all tracks "need fixing" — SOURCE_WINS is preserved.

## Target 10-track corpus (human-provided, per task §4)

| # | Intended character |
|---|---|
| T01 | vocal-centered 1980s |
| T02 | vocal-centered 1990s |
| T03 | dense arrangement |
| T04 | narrow stereo |
| T05 | high noise floor |
| T06 | limited bandwidth |
| T07 | dynamic recording |
| T08 | already-good source (expect SOURCE_WINS) |
| T09 | early digital character |
| T10 | ambiguous / difficult case |

Status: PENDING_HUMAN_MATERIAL. Repo stores only alias + hash + rights +
metadata + evidence, never audio bodies.

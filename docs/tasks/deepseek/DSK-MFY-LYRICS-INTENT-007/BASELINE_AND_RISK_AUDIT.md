# BASELINE_AND_RISK_AUDIT — DSK-MFY-LYRICS-INTENT-007

**Date:** 2026-08-01 UTC

## Environment

| Item | Value |
|---|---|
| Branch | `codex/mainline-cloud-dev-20260603` |
| HEAD | `df3a8a3c8ead4eae0675733169614efe59bf395d` |
| Python | 3.12.3 |
| Tests | 72 passed (bridge full suite) |
| Ruff | Clean |
| Mypy | Clean |

## Attack Surface (before any code change)

| Surface | Risk | Mitigation |
|---|---|---|
| CLI args | Path traversal to sensitive files | Reject paths with `..`, resolve+validate, check is_file |
| Lyrics file read | Exfiltration via error messages | Never include body in error/exception/CLI |
| Lyrics file read | Large file DoS | Hard cap on byte size |
| Lyrics file read | Binary/non-UTF-8 injection | Validate UTF-8, reject NUL bytes |
| JSON/YAML output | Accidental body leak | Body only in evidence/; result/summary/CLI use summaries |
| HTML output | XSS via lyrics body | Always escape HTML; body only in evidence |
| log/stderr | Body in stack traces | No traceback with body; stable error codes only |
| Symlink/junction | Escape evidence dir | Resolve paths, check containment |
| Multi-language text | Assumption violations | Explicit language field; uncertainty for mixed/unknown |
| Declared intent | Misinterpreted as machine inference | Separate field, never auto-generate |

## Privacy & Copyright

| Asset | Risk | Rule |
|---|---|---|
| Lyrics text (full) | Copyright violation if stored without rights | Fail-closed if rights_basis absent |
| Lyrics metadata | Low risk | Always safe to record |
| Author identity inference | Privacy violation | PROHIBITED |
| Psychological inference | Harm | PROHIBITED |
| Political/social stance inference | Harm | PROHIBITED |

## Compatibility Risk

| Existing feature | Risk if changed |
|---|---|
| `refine prepare` without lyrics | Must produce identical result as 006 |
| OnePointSpec schema | Must accept missing lyrics field |
| summary.md structure | Must stay at exactly 5 centers |
| 006 tests | Must all pass unchanged |

## Readonly Baseline

13 files hashed. No modification to any readonly asset is authorized.

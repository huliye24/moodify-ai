# DEFAULT_SURFACE_AUDIT — DSK-MFY-LYRICS-INTENT-007

## Audit Scope

Every element visible in default output with AND without lyrics.

## Five Centers: Preserved

| Center | Without lyrics | With lyrics | Changed? |
|---|---|---|---|
| Essence | Unchanged | Unchanged | No |
| Protect | Unchanged | Unchanged | No |
| Allow | Unchanged | Unchanged | No |
| Action | 1 sentence | 1 sentence + "Lyrics structural evidence was collected." | Appended only |
| Entrust | 1 sentence | 1 sentence (lyrics conflicts noted) | Appended only if conflict |

No sixth center added. No internal acronyms. No body text.

## Leak Scan Results

| Output | Lyrics body present? |
|---|---|
| CLI stdout | No |
| CLI stderr | No |
| result.json | No |
| summary.md | No |
| summary.html | No |
| FINAL_STATUS.txt | No |
| Exception messages | No (stable error codes only) |

## Evidence Visibility

Lyrics data lives in `evidence/lyrics/`:
- `original.txt` — authorized copy
- `original.txt.sha256` — hash
- `lyrics_evidence.json` — structured evidence

All covered by `package_manifest.json` hash inventory.

## Verdict: PASS

Default surface remains exactly 5 centers. Zero body text leakage. Evidence accessible but not on the default surface.

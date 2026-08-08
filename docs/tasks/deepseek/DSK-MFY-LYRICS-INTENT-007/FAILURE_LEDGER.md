# FAILURE_LEDGER — DSK-MFY-LYRICS-INTENT-007

## By-Design Failures (all contract-compliant)

| ID | Scenario | Exit | Error Code | Traceback? | Partial State? |
|---|---|---|---|---|---|
| FL-01 | Unknown rights | 1 | — | No | No |
| FL-02 | Missing file | 1 | — | No | No |
| FL-03 | Directory as path | 1 | — | No | No |
| FL-04 | Path traversal (`..`) | 2 | LYRICS_REJECTED | No | No |
| FL-05 | NUL bytes in file | 2 | LYRICS_REJECTED | No | No |
| FL-06 | Unknown spec field | 2 | SPEC_INVALID | No | No |
| FL-07 | Missing rights_basis | 2 | SPEC_INVALID | No | No |
| FL-08 | Non-empty output dir | 2 | OUTPUT_DIR_NOT_EMPTY | No | No |
| FL-09 | Missing spec file | 2 | SPEC_FILE_MISSING | No | No |
| FL-10 | Empty file | 1 | — | No | No |
| FL-11 | Body leak (stdout) | — | — | — | CLEAN |
| FL-12 | Body leak (result) | — | — | — | CLEAN |

## Implementation Issues (resolved)

| ID | Issue | Resolution |
|---|---|---|
| FL-FIX-01 | `has_explicit_section_labels` always false | Added `re.MULTILINE` to regex |
| FL-FIX-02 | Path/format errors mapped to NEEDS_EVIDENCE | Rejections now exit 2 via `[LYRICS_REJECTED]` |

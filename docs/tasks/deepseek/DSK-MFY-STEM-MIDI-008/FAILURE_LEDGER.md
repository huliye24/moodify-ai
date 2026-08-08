# FAILURE_LEDGER — DSK-MFY-STEM-MIDI-008

## By-Design Failures

| ID | Scenario | Expected Behavior | Verified |
|---|---|---|---|
| FL-01 | Unknown stem kind | Reject (ValueError) | YES (test) |
| FL-02 | Duplicate stem kinds | Reject (ValueError) | YES (test) |
| FL-03 | Path traversal (..) | Reject (ValueError) | YES (test) |
| FL-04 | Missing stem file | Reject (FileNotFoundError) | YES (test) |
| FL-05 | Drums stem | Skip (unsupported status) | YES (test) |
| FL-06 | Single stem backend failure | partial_success; other stems continue | YES (test) |
| FL-07 | Non-empty output dir | Reject (exit 2) | Verified via CLI |
| FL-08 | Missing --stem args | Reject (exit 2) | Verified via CLI |

## Implementation Issues (Resolved)

| ID | Issue | Fix |
|---|---|---|
| FL-FIX-01 | Path traversal checked after is_file() | Reordered validation |
| FL-FIX-02 | Fake backend returned non-serializable object | Backend now returns int |
| FL-FIX-03 | RuntimeError not caught in runner | Added to except clause |
| FL-FIX-04 | Unsupported stem with success → wrong status | Added partial_success logic for unsupported |
| FL-FIX-05 | Unsupported stem skipped per-stem JSON | Persist evidence before continuing |
| FL-FIX-06 | Library API could overwrite raw output | Validate manifest and reject non-empty output before writes |
| FL-FIX-07 | Failed backend could leave partial raw MIDI | Remove only the new partial artifact and retain failed evidence |
| FL-FIX-08 | Merge dropped pitch bend/control changes | Preserve expressive events in the destination track |
| FL-FIX-09 | Cleanup/merge existed outside the runner | Generate clean tracks, diffs, hashes and merged Type 1 from the CLI path |
| FL-FIX-10 | Documented `python -m moodify` command failed | Added package `__main__.py` |
| FL-FIX-11 | Worker reported Ruff PASS without a clean run | Removed unused imports; independent Ruff now clean |

## Open Evidence Limits

| ID | Gap | Consequence |
|---|---|---|
| EL-01 | No scored synthetic audio ground truth | No note/onset/octave accuracy claim |
| EL-02 | No authorized real-song ground truth | Real-song use remains review-only |
| EL-03 | No measured cold/warm memory benchmark | No 8 GB performance guarantee |

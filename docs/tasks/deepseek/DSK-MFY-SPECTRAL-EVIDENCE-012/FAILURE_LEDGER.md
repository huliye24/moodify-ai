# FAILURE LEDGER — DSK-MFY-SPECTRAL-EVIDENCE-012

| ID | Finding | Codex finish |
|---|---|---|
| FL-01 | Before/after each used its own peak reference; gain changes disappeared from difference evidence | Common absolute amplitude reference and regression test |
| FL-02 | `librosa.load` silently resampled and downmixed | Read native format, reject incompatible pairs, explicitly record conversion actions |
| FL-03 | Timeline mismatch only warned and could later broadcast-fail | Reject exact sample-count mismatch before images |
| FL-04 | Track IDs allowed output path escape and duplicates were unchecked | Strict bounded ID grammar and duplicate preflight |
| FL-05 | Validator checked only a subset of before hashes | Re-read both source hashes and verify every artifact hash/path |
| FL-06 | CSV was manually concatenated | Standard CSV writer with stable columns |
| FL-07 | Required XLSX was missing | Added deterministic seven-sheet research workbook |
| FL-08 | No failure injection tests existed | Added six focused tests including tamper and mismatch cases |

Remaining limitation: only one authorized full_mix pair was available; no stem-level population claim is made.


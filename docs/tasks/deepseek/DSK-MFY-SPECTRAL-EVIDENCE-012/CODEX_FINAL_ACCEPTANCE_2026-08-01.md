# DSK-MFY-SPECTRAL-EVIDENCE-012 — Codex Final Acceptance

**Decision:** ACCEPTED_AFTER_CODEX_FINISH  
**Date:** 2026-08-01  
**Acceptance owner:** Codex

## Outcome

The spectral evidence package is accepted after Codex correction and completion. It now produces common-reference before/after/difference spectrograms, traceable metrics, JSON/CSV facts, a seven-sheet XLSX research view, source/artifact hashes and fail-closed validation without modifying source audio.

This is evidence infrastructure. It does not prove that the clean master is better, infer listener preference or authorize training use.

## Worker discrepancies

1. Independent peak normalization made the claimed difference semantics mathematically misleading.
2. Source resampling and mono conversion were silent and original formats were not recorded.
3. Timeline mismatch was only warned and could fail later during matrix subtraction.
4. Track IDs could escape the asset directory and duplicates were not rejected.
5. Validator did not re-read both source files or verify every output artifact.
6. Required XLSX, metric dictionary, XLSX schema, visual limits and failure injection were missing.
7. Stage 3 was reported PASS without a test suite.

## Codex finish

- Established a normalized STFT magnitude with one absolute reference for both versions.
- Defined signed difference as `after_db - before_db` and tested a known +6.02 dB gain case.
- Made mono mixing/resampling explicit and recorded original sample rate/channels/actions.
- Rejected sample-rate, channel and exact timeline mismatch before image generation.
- Added strict case/track schema, duplicate/path-escape prevention and complete hash validation.
- Added deterministic XLSX with seven governed research sheets.
- Kept Human Review blank and Parquet absence explicit.
- Added six focused tests and completed a new real-case validation bundle.

## Independent evidence

- Pytest: **6 passed**
- Ruff: **clean**
- Mypy: **clean across 5 source files**
- Real case: **1 full_mix pair, 0 errors, 0 warnings**
- Bundle validation: **0 issues**
- XLSX: **7 sheets, 0 formula errors, 7/7 visual renders inspected**
- Source hashes: unchanged and revalidated

Final evidence:

```text
E:\moodify\outputs\codex_acceptance\DSK-MFY-SPECTRAL-EVIDENCE-012-FINAL-V2
```

## Remaining limits

1. Only one authorized full_mix pair was available; no stem-level evidence population exists yet.
2. Time sections and decision metadata were not present and remain `NOT_PROVIDED`.
3. Human Review remains blank until an authorized listener enters it.
4. Parquet was not generated because pyarrow is unavailable and new dependencies were forbidden.
5. No musical-quality, preference, superiority or training-readiness claim is accepted.

The accepted package can now supply governed evidence to Treatment Records and the future data-asset task, while preserving the boundary between measurement and musical judgment.

# Repository Weight Before — 2026-10-03

**Task:** `MOODIFY_REPOSITORY_CLEANUP_001`
**Baseline:** `01edc902d72c15010dd86390dc0511fc03fb6323`
**Scope:** current tracked tree only; no history rewrite

## Measurement method

File counts and byte totals come from `git -c core.quotepath=false ls-tree -r -l HEAD`.
They measure uncompressed blob content in the current commit and do not count untracked files.
GitHub metadata comes from the repository API. Local object storage comes from
`git count-objects -vH`; it is history/object-store data and is not comparable to current-tree bytes.

## Summary

| Metric | Before |
|---|---:|
| Tracked files | 1,554 |
| Current-tree blob bytes | 89,990,005 bytes (85.82 MiB) |
| Tracked WAV files | 44 |
| `moodify-core-package/outputs/` files | 32 |
| `moodify-core-package/outputs/` bytes | 48,208,058 bytes (45.97 MiB) |
| GitHub repository metadata size | 318,497 KiB (about 311.03 MiB) |
| Local packed Git object storage | 774.58 MiB |
| Local loose Git objects | 917.82 KiB |
| Local reported garbage | 563.83 MiB across 92 objects |

The local garbage is recorded only. This task explicitly forbids GC, pruning and history rewriting.

## Largest top-level areas

| Path | Files | Bytes |
|---|---:|---:|
| `moodify-core-package/` | 679 | 76,451,225 |
| `examples/` | 49 | 2,987,558 |
| `docs/` | 344 | 2,842,855 |
| `moodify-desktop/` | 27 | 2,421,563 |
| `brand/` | 5 | 1,320,099 |
| `apps/` | 122 | 1,207,885 |
| `.moodify/` | 3 | 825,083 |
| `ops/` | 108 | 775,720 |
| `moodify-music-package/` | 54 | 284,547 |
| `deliverables/` | 18 | 198,259 |

## Largest second-level areas

| Path | Files | Bytes |
|---|---:|---:|
| `moodify-core-package/outputs/` | 32 | 48,208,058 |
| `moodify-core-package/tests/` | 137 | 22,772,167 |
| `moodify-core-package/benchmarks/` | 54 | 3,208,812 |
| `examples/golden_case/` | 49 | 2,987,558 |
| `moodify-desktop/renderer/` | 13 | 2,225,580 |
| `moodify-core-package/src/` | 386 | 2,050,045 |
| `brand/assets/` | 3 | 1,317,814 |
| `.moodify/tt_baseline/` | 2 | 823,250 |
| `apps/android/` | 70 | 789,397 |
| `ops/web_origin/` | 65 | 600,510 |

## Largest tracked files

| Path | Bytes |
|---|---:|
| `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav` | 8,640,172 |
| `moodify-core-package/tests/baseline/test_audio/electronic.wav` | 7,680,172 |
| `moodify-core-package/tests/baseline/test_audio/piano.wav` | 5,760,172 |
| `moodify-core-package/outputs/phase2_agent_b/e2e_gate_DR.wav` | 5,760,044 |
| `moodify-core-package/outputs/phase2_agent_b/e2e_gate_GA.wav` | 5,760,044 |
| `moodify-core-package/outputs/phase2_agent_b/e2e_gate_HL.wav` | 5,760,044 |
| `moodify-core-package/outputs/phase2_agent_b/e2e_gate_SE.wav` | 5,760,044 |
| `moodify-core-package/outputs/phase2_agent_b/e2e_gate_WL.wav` | 5,760,044 |
| `moodify-desktop/renderer/vendor/opensheetmusicdisplay.min.js` | 1,183,666 |

The five gate WAVs and 22 smaller generated WAVs account for most of the output subtree.
The three larger baseline WAVs are intentional regression fixtures and remain in scope to keep.

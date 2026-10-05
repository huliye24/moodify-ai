# Repository Weight After — 2026-10-03

**Task:** `MOODIFY_REPOSITORY_CLEANUP_001`
**Baseline:** `01edc902d72c15010dd86390dc0511fc03fb6323`
**Branch:** `codex/repository-cleanup-001`
**Scope:** current tracked tree only; no history rewrite

## Summary

| Metric | Before | After cleanup payload | Change |
|---|---:|---:|---:|
| Tracked files | 1,554 | 1,522 | -32 |
| Current-tree blob bytes | 89,990,005 | 41,781,947 | -48,208,058 |
| Current-tree blob size | 85.82 MiB | 39.85 MiB | -45.97 MiB |
| Tracked WAV files | 44 | 17 | -27 |
| Tracked `moodify-core-package/outputs/` files | 32 | 0 | -32 |

“After cleanup payload” isolates the intended cleanup itself before adding the small Markdown
evidence reports required by this task. The final proposed tree, including those reports and
the strengthened guard, is recorded in the cleanup report from the staged Git tree.

## Largest top-level areas after removal

| Path | Files | Bytes |
|---|---:|---:|
| `moodify-core-package/` | 647 | 28,243,167 |
| `examples/` | 49 | 2,987,558 |
| `docs/` | 344 before adding this task's reports | 2,842,855 before reports |
| `moodify-desktop/` | 27 | 2,421,563 |
| `brand/` | 5 | 1,320,099 |
| `apps/` | 122 | 1,207,885 |
| `.moodify/` | 3 | 825,083 |
| `ops/` | 108 | 775,720 |

## Largest second-level areas after removal

| Path | Files | Bytes |
|---|---:|---:|
| `moodify-core-package/tests/` | 137 | 22,772,167 |
| `moodify-core-package/benchmarks/` | 54 | 3,208,812 |
| `examples/golden_case/` | 49 | 2,987,558 |
| `moodify-desktop/renderer/` | 13 | 2,225,580 |
| `moodify-core-package/src/` | 386 | 2,050,045 |
| `brand/assets/` | 3 | 1,317,814 |
| `.moodify/tt_baseline/` | 2 | 823,250 |
| `apps/android/` | 70 | 789,397 |
| `ops/web_origin/` | 65 | 600,510 |

## Largest tracked files after removal

| Path | Bytes | Reason retained |
|---|---:|---|
| `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav` | 8,640,172 | Core regression fixture |
| `moodify-core-package/tests/baseline/test_audio/electronic.wav` | 7,680,172 | Core regression fixture |
| `moodify-core-package/tests/baseline/test_audio/piano.wav` | 5,760,172 | Core regression fixture |
| `moodify-desktop/renderer/vendor/opensheetmusicdisplay.min.js` | 1,183,666 | Vendored Studio runtime library |
| `brand/assets/moodify-horizontal.svg` | 850,243 | Brand source asset |

## Storage distinction

- **Current tracked tree:** reduced by exactly 48,208,058 bytes before adding evidence text.
- **Git object/history storage:** unchanged in principle; old commits still contain the blobs.
- **GitHub repository metadata:** measured at 318,497 KiB before the task and is not claimed
  to have fallen to ~40 MiB.
- **Local object store:** old garbage/object warnings were observed and deliberately left
  untouched because GC and pruning are out of scope.

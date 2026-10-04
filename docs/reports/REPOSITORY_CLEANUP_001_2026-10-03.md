# Repository Cleanup 001 — Execution Report

**Baseline main:** `01edc902d72c15010dd86390dc0511fc03fb6323`
**Branch:** `codex/repository-cleanup-001`
**CANON_CHANGE:** `NO`
**History rewrite:** none

## Result

The current tree no longer tracks `moodify-core-package/outputs/`. Exactly 32 generated
files and 48,208,058 bytes were removed from the current-tree payload. The local directory
was not deleted: 1,924 local files remained immediately after `git rm --cached`, protected
by the existing `.gitignore` rule at `.gitignore:215` (`outputs/`).

| Metric | Before | Cleanup payload after |
|---|---:|---:|
| Tracked files | 1,554 | 1,522 |
| Tracked blob bytes | 89,990,005 | 41,781,947 |
| Tracked WAV files | 44 | 17 |
| Tracked Core output files | 32 | 0 |

The final proposed-tree count includes four small evidence reports added by this task and is
recorded below after staging.

## Changes

1. Untracked only `moodify-core-package/outputs/`; local output files remain available.
2. Added an exact `FORBIDDEN_GENERATED_PREFIXES` invariant to
   `scripts/check_repo_structure.py`.
3. Added before/after weight evidence and a remaining-binary inventory.
4. Kept Core baseline WAVs, benchmark fixtures and `examples/golden_case/` unchanged.

No Studio behavior, Core DSP, Quick/Deep Finish semantics, MIDI gating, Android behavior,
Cloud Node behavior or network design was changed.

## Guard evidence

Positive run after untracking:

```text
Repository structure guard: OK (1522 tracked files, 6 checks)
```

Negative probe procedure:

1. `git add -f moodify-core-package/outputs/phase2_agent_b/e2e_gate_DR.wav`
2. Run the guard and observe exit code 1 with the exact forbidden-prefix finding.
3. Remove the probe from the index again with `git rm --cached`.
4. Confirm the local file still exists and rerun the guard.

Observed failure:

```text
Repository structure guard FAILED (1523 tracked files)
[forbidden generated prefixes]
generated output subtree is tracked: 'moodify-core-package/outputs/' (1 file(s))
negative_guard_exit=1
```

Observed recovery:

```text
Repository structure guard: OK (1522 tracked files, 6 checks)
```

The probe is not part of the proposed commit.

## Ignore verification

```text
.gitignore:215:outputs/ moodify-core-package/outputs/phase2_agent_b/e2e_gate_DR.wav
```

`git ls-files moodify-core-package/outputs` returns no paths.

## Final staged-tree measurement

| Metric | Value |
|---|---:|
| Tracked files | 1,526 |
| Tracked blob bytes | 41,796,741 |
| Tracked blob size | 39.86 MiB |

The difference between the 1,522-file cleanup payload and final staged tree consists only of
the required Markdown evidence reports. It does not restore generated output.

## Verification

- Repository structure guard: `PASS`
- Negative repository guard probe: `PASS` (failed when expected, then recovered)
- `git diff --check`: `PASS`
- Ruff: `PASS`
- Python tests: `1197 passed, 5 skipped, 58 warnings`
- Studio pipeline tests: `33 passed, 0 failed`
- Studio headless processing tests: `21 passed, 0 failed`
- Studio static contract check: `PASS`
- Baseline audio remains tracked: `PASS` (3 WAVs plus README)
- Benchmark fixtures remain tracked: `PASS` (10 WAVs)
- `moodify-core-package/outputs/` tracked paths: `0`

## Remaining weight and debt

- Three baseline regression WAVs intentionally account for 22,080,516 bytes.
- Ten benchmark WAV fixtures and four golden-case WAVs remain intentionally tracked.
- 15 bounded `.npz` fixtures total 1,140,899 bytes.
- GitHub metadata was 318,497 KiB before cleanup because history remains intact.
- Old generated blobs remain in history; no `filter-repo`, BFG, GC, pruning, force push,
  tag deletion or commit rewriting was performed.
- The local object store reported garbage objects; Cleanup 001 does not touch them.

## Explicitly out of scope

Temporal Texture baseline debt, workflow cleanup, stale PR cleanup, Android canonical-client
selection, Windows packaging, MOOD contribution work, `moodify_runtime` migration and any
Git history rewrite remain separate tasks requiring new authorization.

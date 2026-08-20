# MFY-CR-P01 — Test Results

Executed 2026-08-17 on the baseline working tree (branch codex/moodify-classic-reconstruction-001, HEAD 5bbc4972).

## Python / Core (moodify-core-package, Python 3.11.9, pytest 9.0.3)

```text
python_total = 692 passed + 5 skipped
python_pass  = 692
python_fail  = 0
python_skip  = 5 (design: matplotlib-tight-layout-adjacent cases, pre-existing)
```

- `pytest -m v01` : 20 passed, 5 skipped, 672 deselected (78s)
- `pytest` (full) : 692 passed, 5 skipped (7m41s)
- Suite covers auditory / contracts / authority / data_factory / node /
  processing / API / stems / release — including the converged uncommitted
  format-invariant guards (DURATION_CHANGED, CHANNEL_LAYOUT_CHANGED,
  SAMPLE_RATE_CHANGED) in tests/auditory/test_comparison.py.

## Root tests (tests/ear_batch — converged in Commit 1)

```text
9 passed (test_ear_batch, test_knowledge_extract, test_material_governance)
```

## Music Web (apps/music-web)

```text
36 passed / 0 failed  (node --test tests/*.test.mjs, Node 24.14.0)
```

Note: `npm test` wrapper fails in this environment with
`ERR_UNSUPPORTED_ESM_URL_SCHEME` at the `node --test tests/*.test.mjs` stage
(Windows cmd passes the glob literally to node). The identical command run
directly from git-bash (glob expanded by shell) passes 36/36. Recorded as an
environment quirk, NOT a suite failure. `npm run build` phase passes.

## Android (apps/music-android)

```text
android_unit    = NO-SOURCE (no unit test sources exist under app/src/test; recorded fact, not a PASS)
android_assemble= BUILD SUCCESSFUL (gradle 8.14, AGP from cached wrapper dist, JAVA_HOME=Android Studio JBR, ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk)
```

`testDebugUnitTest` reports `NO-SOURCE` for both Kotlin and Java — the app has no
unit tests. This is documented, not faked.

真机/instrumentation: NOT_RUN_ENVIRONMENT_UNAVAILABLE (no device attached in this session;
device evidence for playback path exists in artifacts/mfy_mobile_audio_capability_baseline_001).

## Lint / Repo Health

```text
lint       = ruff 0.15.15: ALL CHECKS PASSED (5 pre-existing F401 unused imports auto-fixed as
             baseline integrity fix — none in uncommitted audio-related code, none change behavior)
diff_check = git diff --check: CLEAN (exit 0)
secret     = pattern scan over untracked candidates: 1 hit = docs reference to a local env file path
             (E:\moodify\temp\moodify_audit\polardb_app.env) — pointer, not a secret; file stays out of git
generated-heavy artifact review = classification in UNCOMMITTED_ASSET_AUDIT.md (B items excluded from commits)
```

## Summary

```text
python_total = 692 + 9 + 5 skipped
android_assemble = PASS
android_unit = NO-SOURCE (fact)
lint = PASS
diff_check = PASS
```

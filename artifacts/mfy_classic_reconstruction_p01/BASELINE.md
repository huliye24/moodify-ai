# MFY-CR-P01 — Baseline Manifest

**Task:** MFY-CR-P01 Baseline Convergence
**Executed:** 2026-08-17
**Executor:** Claude Code (executing Moodify_P01_Baseline_Convergence_2026-08-16 package)

## Repository

```text
repo = E:\moodify (git root, branch codex/moodify-classic-reconstruction-001)
remote = origin -> https://github.com/huliye24/moodify-ai.git
         moodify -> https://github.com/huliye24/moodify.git
current_branch = codex/moodify-classic-reconstruction-001
current_head = 5bbc4972
working_tree = uncommitted convergence assets (Commit 1) + P01 evidence (Commit 2)
```

## New Baseline

```text
branch = codex/moodify-classic-reconstruction-001
base_branch = codex/moodify-android-2.0
base_commit = 5bbc4972
created_at = 2026-08-17 (local execution)
```

## Scan-Head Difference (recorded)

Task document scanned head was `0438c22f`. At execution time the working line had advanced by 2 unpushed commits:

```text
0438c22f feat(cloud): harden Music data plane            (scan-time head, also moodify-remote head)
72c47c4d feat(stems): cloud stem separation via lalal.ai API V1 (LALAL-STEMS-001)
5bbc4972 feat(artifacts): MFY_ANDROID_AUDIO_PATH_OBSERVABILITY_001 evidence (2026-08-17 rerun)
```

Per the task rule "以当前仓库事实为准，并写清差异": the canonical baseline for P02 is
**HEAD = 5bbc4972**, which is 2 commits ahead of the documented scan head. Both extra
commits are verified, tested, and belong to the current Android/cloud working line.

## Canonical Components

| Component | Path | Status | Verification | Notes |
|---|---|---|---|---|
| Auditory Core | moodify-core-package/src/moodify/auditory | CANONICAL | pytest full suite PASS | + uncommitted format-invariant guards converged (Commit 1) |
| Contracts | moodify-core-package/src/moodify/contracts | CANONICAL | pytest full suite PASS | |
| Authority | moodify-core-package/src/moodify/authority | CANONICAL | pytest full suite PASS | |
| Data Factory | moodify-core-package/src/moodify/data_factory | CANONICAL | pytest full suite PASS | ruff F401 fix converged |
| Processing | moodify-core-package/src/moodify/processing | CANONICAL | pytest full suite PASS | |
| Node / Worker | moodify-core-package/src/moodify/node + ops/data_node | CANONICAL | pytest full suite PASS; deployed 120.55.191.146 | systemd workers live |
| Web Origin / BFF | apps/music-web + ops/web_origin | CANONICAL | node tests 36/36 PASS | deployed on LA origin 103.144.246.242 |
| Android Player | apps/music-android (new line, com.moodify.music) | CANONICAL | assembleDebug PASS; unit tests NO-SOURCE | release line 2.0.1; player/ui/res converged in Commit 1 |
| Android (legacy) | apps/android (com.moodify.app) | CANONICAL | not rebuilt in P01 | release line 2.0.0/3.0.0/3.1.0; dual-line decision -> UNRESOLVED |
| Stems / LALAL | moodify-core-package/src/moodify/stems + api/routes/stems.py + ops/web_origin | CANONICAL | pytest full suite PASS (stems tests included) | commit 72c47c4d, unpushed to remote |
| Audiolla | external service + artifacts/audiolla_cloud_deploy_001 | SUPPORTED_EXTERNAL | deployment evidence committed (Commit 1) | LA host, PASS_WITH_LIMITATIONS |
| Storage | PolarDB MySQL (pc-bp1112f8t24wdta5t) + LA disk | SUPPORTED_EXTERNAL | not exercised in P01 | VPC peering pending (pre-existing) |
| Tests | moodify-core-package/tests + tests/ear_batch + apps/music-web/tests | CANONICAL | 692+9+36 PASS | root tests/ear_batch converged (Commit 1) |
| Runtime-only assets | temp/, .codex_tmp/, LA /opt/moodify runtime | RUNTIME_ONLY | out of git by design | classification in UNCOMMITTED_ASSET_AUDIT.md |
| Legacy / historical | docs/reference/TENCENT_CLOUD_SERVER.md, sync_cloud.sh | LEGACY | deletions converged (Commit 1) | Tencent cloud expired 2026-08-12 |

## Blocking Issues

```text
- none blocking P01
- Android music-android has NO unit tests (recorded fact; testDebugUnitTest = NO-SOURCE)
- npm test wrapper on Windows cmd hits node --test glob quirk (ERR_UNSUPPORTED_ESM_URL_SCHEME);
  direct `node --test tests/*.test.mjs` runs 36/36 PASS
```

## P01 Status

```text
P01_COMPLETE
```

# Moodify Project Status — 2026-06-04

> **Superseded notice:** 本文记录 2026-06-04 状态。许可决策已被
> `Adopt GPL-3.0 and clean repository metadata (#14)` 取代：Moodify 现为
> `GPL-3.0-only`（见 LICENSE 与 OPEN_SOURCE_NOTICE.md）。文中 Apache-2.0
> 相关表述为历史事实，不代表当前许可。

## Summary

Moodify's active mainline is `codex/mainline-cloud-dev-20260603`.

The project is no longer just the v01 local audio processor. The current branch has become an industrial runtime system for AI music post-processing: operator jobs, queues, runtime execution, MRS scoring, quality gates, reports, delivery records, craft memory, tidal cycles, PDF reports, and craft-chain infrastructure.

## Verified State

Checked locally on 2026-06-04:

```text
python3 -m pytest moodify_runtime/tests/ -q
607 passed, 9 skipped

python3 -m pytest moodify-core-package/tests -q
112 passed
```

Total verified passing tests: 719.

## Git State

- Repository: `git@github.com-moodify:huliye24/moodify-o3is.git`
- Active branch: `codex/mainline-cloud-dev-20260603`
- Remote branch exists: `origin/codex/mainline-cloud-dev-20260603`
- Branch relation to `origin/main` after fetch: `origin/main` has 2 commits not in this branch, this branch has 44 commits not in `origin/main`.
- The two `origin/main` commits are compliance-oriented: remove key-shaped examples and adopt Apache-2.0 license.

## Main Risk

The code and tests are ahead of several status documents. README, architecture, roadmap, E-Chain, and NEM files should be treated as partially reconciled until the release checklist is complete.

## Release Checklist

- Keep Apache-2.0 license metadata in package files.
- Keep `LICENSE` in the repo root.
- Replace key-shaped placeholders with non-key placeholders such as `your-deepseek-api-key`.
- Do not commit generated audio, images, caches, local data, or runtime outputs.
- Run the 719-test verification before creating a release tag or merging to `main`.
- Prefer a PR from `codex/mainline-cloud-dev-20260603` into `main`, because `main` contains compliance commits that must be retained.

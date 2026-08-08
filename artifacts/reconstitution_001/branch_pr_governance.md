# Branch and PR Governance

Snapshot date: 2026-08-08. Divergence counts are relative to `origin/main` at `0b355e7`.

| Branch / PR | Observed state | Recommendation | Reason |
|---|---|---|---|
| PR #15 `codex/mainline-cloud-dev-20260603` | Draft; mergeable but CI-blocked; 92 commits ahead; 2,809 files changed | **CHERRY_PICK / REIMPLEMENT** | Valuable Android, runtime, auditory, learning, and tooling work, but too broad to establish authority safely. Extract tested contracts by subsystem. |
| PR #9 `feat/brand-integration` | Open, conflicting; 70 behind / 28 ahead; 309 files changed | **CLOSE_AS_SUPERSEDED** after preserving design references | Stale AppTabLayout/frontend architecture overlaps newer branches. Do not wholesale merge. |
| PR #13 `huliye24-patch-1` | Open; 1 behind / 1 ahead; license-only | **CLOSE_AS_SUPERSEDED** | GPL-3.0 already landed through PR #14. |
| PR #14 GPL cleanup | Merged | **ARCHIVE** | Completed and now part of `main`; branch may be deleted after normal retention checks. |
| `codex/cloud-mainline-dev-20260603-recovered` | 3 behind / 12 ahead | **HUMAN_DECISION** | Recovery branch may contain unique runtime history; compare against PR #15 before archival. |
| `milestone/moodify-daily-run-mrs-open-v031` | 3 behind / 5 ahead | **CHERRY_PICK** evidence/contracts only | MRS/runtime milestone is useful research but must not create a second scoring authority. |
| `stabilization-sprint-001` | 3 behind / 1 ahead | **CHERRY_PICK** after test review | Small stabilization work may be independently reusable. |
| `mhp-025-api-v01-alignment` | 9 behind / 3 ahead; related PR #10 already merged | **ARCHIVE** | Merged work is represented on main; remaining divergence needs proof before reuse. |

No branch is authoritative because it is larger or further ahead. Changes join the mainline only with a unique responsibility, explicit contracts, tests, defined failure behavior, and a clear place in WSE, MSE, or PPE.

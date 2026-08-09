# Duplicate Systems Audit

| Responsibility | Current `main` authority | Competing implementation | Decision |
|---|---|---|---|
| Audio orchestration | `v01_pipeline.py` | legacy `WorkflowOrchestrator`; workspace/runtime engines on PR #15 | Keep v0.1 canonical; require adapters or a later migration ADR. |
| API | `moodify.api.main` | mobile/workspace/operator APIs on PR #15 | Reimplement or cherry-pick contracts after compatibility tests. |
| Metrics / scoring | v0.1 analyzer and diagnosis outputs | reality metrics, MRS variants, branch-only scoring systems | Experimental until method, version, and evidence provenance are canonical. |
| Records | `treatment_records/*.json` | production-case, learning, runtime, and evidence formats on PR #15 | Define one versioned asset schema before migration. |
| Frontend / app | no canonical full application on `main` | PR #9 frontend and PR #15 Android app | Human product decision, followed by narrow integration work. |
| Configuration | v0.1 presets and package configuration | branch-only runtime/cloud config systems | Do not merge overlapping configuration authorities wholesale. |

This task deliberately makes no deletions. A later convergence task should select contracts, preserve tests, and migrate one responsibility at a time.

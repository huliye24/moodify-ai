# Orchestration Authority Risks

The supported mainline is `Import -> Analyze -> Diagnose -> Process -> Export`.
The wider `moodify-core-package/src/moodify/orchestration/workflow_engine.py`
production-case state machine is classified LEGACY. Branch-era trackers and
experimental workflow descriptions are evidence of design exploration, not a
second authority.

Risks:

- Promoting the legacy workflow engine would conflict with repository status.
- Treating this batch ledger as a product runtime would create a second state machine.
- Treating branch-only cloud/app systems as merged capability would overstate truth.
- Bulk-merging historical orchestration would bypass current tests and authority review.

Controls:

- `ops/ear_batch` manages only this offline knowledge-engineering run.
- It never imports or mutates the product orchestration layer.
- Product authority changes are emitted as human decisions, never auto-applied.
- Future implementation work should prefer narrow adapters and current contracts.

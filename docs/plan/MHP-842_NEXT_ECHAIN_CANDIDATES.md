# MHP-842: Next E-Chain Candidates

**Status**: done

## Candidate Analysis for E-Chain 015

### Candidate 1: DeepSeek API Integration (Priority: HIGH)

Replace simulated worker outputs with real DeepSeek v4 API calls. The protocol and schema are stable — only the transport layer needs implementation.

Scope:
- Add `scripts/deepseek_worker_client.py` with API-key auth
- Run nightly `deepseek_tasks.jsonl` through real model calls
- Compare real vs rule-based recommendations
- Tune severity thresholds based on real model behavior

### Candidate 2: Multi-Night Learning Storage (Priority: HIGH)

The current system processes one night at a time. A multi-night store would enable trend detection, rolling averages, and statistical significance testing.

Scope:
- `moodify_runtime/learning_store.py` — JSONL append-only store
- Cross-night trend analysis in dashboard
- Statistical significance on scoring disagreement rates
- Auto-escalation when a preset degrades 3+ nights

### Candidate 3: Auto-Healing Runtime (Priority: MEDIUM)

Close the loop: when a fatal error is detected, auto-apply the fix and rerun.

Scope:
- `moodify_runtime/auto_fix.py` — pattern-based fix application
- Safe-mode: only apply fixes with `needs_human_review: false`
- Auto-rerun after fix with diff comparison
- Operator notification on fix application

### Candidate 4: X-CLP Score Automation (Priority: MEDIUM)

Automatically compute X-CLP scores for each night's run to quantify codebase and process health.

Scope:
- `moodify_runtime/x_clp_scorer.py` — automated scoring
- Module boundary, naming, logging, config, error handling checks
- Trend dashboard showing X-CLP over time

### Candidate 5: Worker Model Diversity (Priority: LOW)

Support multiple cheap models (Claude Haiku, GPT-4o-mini) alongside DeepSeek v4 for ensemble recommendations.

Scope:
- Abstract worker client interface
- Ensemble voting across models
- Cost comparison per model

### Recommendation

Prioritize Candidates 1 and 2 for E-Chain 015. Candidate 1 (API integration) is the smallest gap — the entire protocol is ready. Candidate 2 (multi-night store) unlocks trend analysis and statistical rigor.

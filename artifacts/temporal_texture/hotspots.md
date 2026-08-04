# Moodify Temporal Texture — Hotspot Ranking

Generated: 2026-08-04 · Baseline: `artifacts/temporal_texture/before/report.json`

## Method

Ranking combines static pressure signals (weighted: error ×5, warning ×2, info ×1) with business/production risk.
Noise directories (scratch/, tmp/, .codex-work/, night/, project_analytics/, node_modules, venvs, generated docs)
were excluded from the ranking; the baseline report itself only excludes tooling/venv directories per config.

## Baseline summary (core scope)

- Files scanned (whole repo, venvs excluded): 666
- Findings: 2878 (219 error / 1885 warning / 774 info)
- Core-scope (noise excluded) findings: 2014, errors: 192
- Empty exception handlers (TT-EMPTY-EXCEPTION, error): 82 total, spread over ~50 modules

## Ranking table

| Rank | Module / function | Pressure signals | Business risk | Test protection | Proposed action | Wave 1 |
|---|---|---|---|---|---|---|
| 1 | `moodify_runtime/operator_console.py` | 3E / 16W / 9I | Operator console = approval & execution authority path | `moodify_runtime/tests/test_operator_console.py` exists | Separate input/judgment/execution/evidence; explicit failure types | **yes** |
| 2 | `moodify-core-package/src/moodify/orchestration/workflow_engine.py` | 5E / 23W / 0I, 8 empty handlers | Orchestrates diagnosis→spatial→result pipeline | core tests present | Remove empty handlers, name decisions, split `_run_*` steps | **yes** |
| 3 | `moodify_runtime/craft_processes.py` | 4E / 14W / 0I | Craft processing chain (audio execution) | `moodify_runtime/tests/test_craft.py` exists | Guard clauses, typed failures, named rules | **yes** |
| 4 | `moodify-bridge/src/moodify_bridge/services.py` | 7E / 28W / 27I, 1 empty handler | Public API service layer | bridge tests exist | Extract validation/cleanup helpers; fix `_cleanup_promotion_marker` empty except | **yes** |
| 5 | `moodify_runtime/runner.py` | 2E / 5W / 23I | Runtime supervisor / control spine | `test_runtime_supervisor.py` exists | Typed results, debt markers, explicit state transitions | **yes** |
| 6 | `moodify-core-package/src/moodify/v01_pipeline.py` | 4E / 11W / 2I, 2 empty handlers | Core processing pipeline (scan→quality gate) | v01 tests exist | Fix empty handlers, split `scan_audio` / `_quality_gate` | **yes** |
| 7 | `moodify-core-package/src/moodify/v01_delivery.py` | 3E / 0W / 0I, 3 empty handlers | Evidence packaging (`_git_hash`, `_installed_packages`) | covered via v01 tests | Replace empty fallbacks with structured evidence failures | **yes** |
| 8 | `moodify_runtime/cli.py` | 3E / 6W / 1I | Public CLI entry | `moodify_runtime/tests/test_cli.py` exists | Guard clauses, split command handlers, unused-import cleanup | **yes** |
| 9 | `moodify_runtime/pdf_ct_builder.py` | 5E / 4W / 35I | PDF evidence builder | weak | Debt markers audit; keep scope minimal | no |
| 10 | `scripts/gen_mhp_629_736.py` | 1E / 109W / 15I | One-shot generation script | none | Low business risk — document only | no |
| 11 | `moodify-core-package/src/moodify/diagnosis/engine.py` | 3E / 10W / 0I, 2 empty handlers | Audio diagnosis chain | diagnosis tests exist | Empty-handler fix could be wave 2 | no |
| 12 | `moodify-core-package/src/moodify/auditory/decode.py` | 2E / 0W / 0I, 2 empty handlers | Auditory decoding | auditory tests exist | Wave 2 candidate | no |

## Selection rationale (wave 1 = top 8)

The 8 selected modules all sit on production-critical paths: operator approval, orchestration,
craft execution, public API, runtime control, processing pipeline, evidence packaging, CLI entry.
Their pressure signals include the repo's most concentrated empty-exception (principle 4) and
broad-exception (principle 3) violations. All 8 have at least some existing test protection,
satisfying the "protect behavior before structure" precondition.

Deliberately excluded from wave 1: `diagnosis/*` and `auditory/*` (wave 2), one-shot scripts and
doc generators (low business risk), `pdf_ct_builder` (evidence cosmetics, needs product authority
for scope).

## Notes

- `operator_console.py` and `workflow_engine.py` are the two highest-risk targets and get the
  most characterization test effort in wave 1.
- Per task protocol, every refactor must keep public APIs, CLI behavior, file formats, state
  transitions and audio-processing semantics unchanged; any intentional difference requires
  documented authority.

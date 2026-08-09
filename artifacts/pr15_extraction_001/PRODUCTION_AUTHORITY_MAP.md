# Production Authority Map

| Candidate | Unit of Work | States | Approval / Gate | Execution / Verification | Evidence | Tests | Recommendation |
|---|---|---|---|---|---|---|---|
| v0.1 pipeline | one audio processing call | implicit stages | diagnosis/quality checks | in-process DSP/export | report/WAV | 109-test baseline | Keep as execution adapter, not future case authority |
| `app/production_control.py` | `ProductionCase` | CREATED through COMPLETED, plus REJECTED/FAILED and controlled recovery | exact plan/spec/source-bound human approval and technical gate | immutable execution envelope; verify then package | transitions, execution, verification, evidence path | CLI-v2 case tests and production-control consumers | **EXTRACT state semantics and reimplement as single authority** |
| `domain/workflow.py` | project workflow | brief/analysis/plan/approval-style project stages | separate approval model | workspace services | project events | 19 v2 test files | Fold useful project concepts into ProductionCase; retire competing state graph |
| `cli_v2/` | command facade around cases/projects | delegates multiple domains | command-level checks | invokes app/services | case directories | substantial CLI-v2 tests | Keep as adapter only |
| `moodify-bridge` | evidence/research case package | mostly immutable records, not execution lifecycle | HumanApproval / validation | services and file store | strong schema bundle | 9 test files | Extract contracts; must not own runtime state |
| `moodify_runtime` | jobs, daily runs, scheduler, operator workflows | several job/task/run state sets | runtime gates and operator approvals | queues/runners/cloud worker | JSONL reports/manifests | 81 test files | Keep infrastructure concepts; rebind to canonical case IDs |
| legacy `WorkflowOrchestrator` | legacy audio workflow | internal phases | legacy quality logic | monolithic orchestration | legacy report | texture/legacy coverage | Archive compatibility path |

## Recommended Single Authority

The future authoritative production state machine is a reimplemented, contract-first `moodify.production.ProductionCase`, using the transition and approval invariants proven in `app/production_control.py`:

`CREATED → SOURCE_REGISTERED → SPECIFIED → ANALYZED → PLANNED → TECHNICALLY_VALIDATED → AWAITING_ARTISTIC_APPROVAL → APPROVED → EXECUTING → EXECUTED → VERIFYING → VERIFIED → PACKAGED → COMPLETED`.

Runtime queues, Android, CLI, cloud workers, and engines consume this authority; none define parallel product states. Execution adapters never mutate case state directly.

## Migration Risks

- The state graph is comprehensive but coupled to file paths/dictionaries and needs minimum contracts first.
- Failure/retry semantics must distinguish re-execution from new approval requirements.
- Workspace `ProjectWorkflow` and runtime job statuses require explicit mapping before retirement.

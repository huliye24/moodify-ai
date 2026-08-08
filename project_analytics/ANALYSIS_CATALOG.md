# Moodify Analysis Catalog

## Routine analyses

| ID | Cadence | Decision supported | Minimum evidence | Stop/alert condition |
|---|---|---|---|---|
| `repo-health-daily` | Daily while active | Is the workspace safe to continue changing? | Git status, diff breadth, last commit, test collection | Collection errors > 0; more than one active task touches shared core |
| `task-acceptance` | At every task handoff | Did implementation become trusted capital? | task manifest, changed files, targeted/full tests, reproducible commands | READY without reproducible evidence; full baseline red |
| `portfolio-flow-weekly` | Weekly | Should work start, stop, or be reprioritised? | task states, start/ready/accept times, dependencies, owner hours | WIP > 1 on shared core; acceptance yield < 80% |
| `engineering-capital-monthly` | Monthly | Is hidden depth increasing future ease? | code/test structure, repeated failures, cycle/rework time, dependency concentration | Rework drag rises; old failures recur; capital grows without lower cycle time |

## Stage analyses

| ID | Trigger | Decision supported | Comparison |
|---|---|---|---|
| `stabilization-baseline` | Before and after a cleanup pause | Did stabilisation reduce uncertainty and work-in-progress? | pre/post baseline using the same metric contract |
| `release-readiness` | Before a version/tag | Is the release reproducible, truthful, and recoverable? | candidate versus last accepted release |
| `architecture-change` | Before/after core model or boundary migration | Did the new form reduce coupling and preserve compatibility? | old/new imports, change surface, test and dependency graph |
| `milestone-closure` | End of a roadmap phase | Which capabilities are accepted, deferred, retired, or unsupported? | plan versus accepted evidence |

## Dedicated analyses

| ID | When justified | Required special evidence |
|---|---|---|
| `audio-perceptual-quality` | A processing/model change claims musical improvement | blinded listening protocol, sample rights, listener agreement, technical metrics |
| `model-backend-benchmark` | Choosing or upgrading a model/backend | fixed corpus, environment lock, quality/latency/cost/failure matrix |
| `security-license-review` | New external tool, model, upload, or distribution path | threat boundary, dependency/license inventory, data-handling evidence |
| `market-financial-roi` | Pricing, financing, hiring, or major time allocation | user demand, usage, conversion/revenue or explicit scenario assumptions |

## Portfolio rule

Routine analytics protects the operating system of the project. Stage analytics
decides whether a transition may proceed. Dedicated analytics exists only for a
specific high-consequence claim and must not become ceremonial recurring work.


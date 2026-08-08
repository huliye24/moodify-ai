# Work Breakdown Structure

每个 Epic 包含 Feature、Task、Test、Documentation 和 Acceptance；详单见 BACKLOG。

| Epic | Feature 范围 | 主要验收 | 依赖 | 优先级/工作量 |
|---|---|---|---|---|
| EPIC-01 Project Foundation | 审计、定位、架构、版本/状态词典 | 路径真实、状态不夸大 | 无 | P0/L |
| EPIC-02 Production Case System | IDs、schema、ledger、revision | raw immutable、关联完整 | 01 | P0/XL |
| EPIC-03 WSE Measurement | registry、adapters、confidence | 标准夹具、null语义 | 02 | P0/XL |
| EPIC-04 MSE Structural Analysis | BPM/key/section/lyrics/MIDI接口 | confidence+人工校正 | 02 | P1/XL |
| EPIC-05 Treatment Engine | pipeline/stage/rules adapter | 不重写DSP、参数可重放 | 02-03 | P1/L |
| EPIC-06 Candidate Search | experiment/candidate registry | 多候选不覆盖 | 05 | P1/XL |
| EPIC-07 Evaluation and Quality Gates | technical/structural/perceptual/PPE | 决策证据与失败阻断 | 03-06 | P0/XL |
| EPIC-08 Production Learning Loop | theory/rule/approval/regression | 禁止自动晋级 | 07 | P0/XL |
| EPIC-09 Asset Packaging | manifest/rights/reports/structure | hash与限制完整 | 02-07 | P1/L |
| EPIC-10 Batch Production | queue/recovery/cost | 幂等与失败隔离 | 02,09 | P1/XL |
| EPIC-11 Human Benchmark | A/B/C protocol and analysis | 盲听、随机、分布、失败保留 | 07 | P1/XL |
| EPIC-12 Release and Documentation | v0.4 baseline | gates/changelog/runbook | 全部 | P1/L |

工作量：XS≤0.5天，S=1天，M=2—3天，L=4—7天，XL=需继续拆分。


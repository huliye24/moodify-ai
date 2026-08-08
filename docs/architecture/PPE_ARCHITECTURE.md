# PPE Architecture

PPE 回答“怎样稳定地把它生产出来”。它管理事实和决策，不替代 WSE/MSE 算法或人的审美责任。

| 子模块 | 核心对象/输出 | 当前状态 | v0.4 要求 |
|---|---|---|---|
| Production Case | case、revision、failure、limitations | bridge Partial | 原始记录不可变 |
| Job definition | input refs, pipeline/rules, resources | Runtime Partial | job 必须关联 case/experiment |
| Pipeline orchestration | stages, parameters, timing | Core/Runtime Partial | 每阶段版本、输入/输出哈希 |
| Candidate generation | candidates | Experimental/Partial | 候选不覆盖，生成理由明确 |
| Candidate registry | CandidateRecord | Planned schema | CASE 内唯一 ID 与资产哈希 |
| Quality gates | checks + result | Partial/分散 | PASS/WARN/FAIL、规则版本、证据 |
| Human review | observation/approval/decision | Partial | 最终选择和规则晋级有责任人 |
| Experiment tracking | ExperimentRecord | Planned schema | 假设、变量、对照、停止条件 |
| Rule versioning | RuleRecord | bridge Partial | proposed→experimental→validated→production→deprecated；禁止自动晋级 |
| Cost/runtime | stage/job timing, human minutes, cost | Partial | 统一单位与缺失语义 |
| Asset packaging | DeliverableManifest | Partial | 哈希、角色、权利、报告/结构资产 |
| Reproducibility | Golden replay | bridge Partial | 同版本重放，差异可解释 |

PPE 的生产门禁依次为：输入完整、身份一致、测量可用、候选可比、人工批准、资产包完整。任何失败都形成事件，不删除失败候选换取通过。


# Moodify 90-Day Plan｜2026-08-01—2026-10-31

原则：先 contract 和证据，再扩算法；每项“完成”必须有代码/数据/测试/文档路径。P0 阻塞闭环，P1 为 90 天必需。

## 阶段一｜Day 1—30｜基础测量与案例系统

目标：让每次处理可追踪、可复现。

| 里程碑 | 任务 | 交付 | 验收 | 依赖 |
|---|---|---|---|---|
| M1.1 v0.4 contract | 审计、定位、架构、schema | 本批文档与 bridge models | schema/test/path 检查通过 | 无 |
| M1.2 Case adapter | core/runtime 写 case/pipeline/rules/asset IDs | adapter + integration test | 不改源文件；失败入 ledger | M1.1 |
| M1.3 WSE registry | 统一名称、单位、backend、confidence | metric registry v0.1 | 合成夹具和参考工具交叉验证 | M1.1 |
| M1.4 Baseline report | before/after 统一报告 | MD/HTML + Parquet | null/warning 不伪造 | M1.2-1.3 |
| M1.5 Golden Set | 5—10 个授权/合成案例 manifest | hashes/rights/coverage | 重放不删除失败 | M1.2 |

阶段验收：同一 input hash、PIPELINE 和 rule versions 可复现相同配置、测量记录和可解释资产；非确定音频字节差异必须有容差与原因。

## 阶段二｜Day 31—60｜候选搜索与结构理解

| 里程碑 | 任务 | 交付 | 验收 | 依赖 |
|---|---|---|---|---|
| M2.1 Candidate registry | 生成多个参数受限候选 | Candidate/Experiment records | 每候选参数、规则、哈希完整 | M1 |
| M2.2 Compare/evaluate | WSE差异、盲听接口、Decision | Evaluation/Decision records | 选择只引用已登记候选 | M2.1 |
| M2.3 Section WSE | 按统一 section ID 计算轨迹 | section Parquet | 相同边界重放一致 | M2.4 |
| M2.4 Minimal MSE | BPM/beat/key/section，lyrics接口 | StructuralRecord | confidence+人工校正；不承诺完整扒谱 | M1 |
| M2.5 Gates | technical/structural/evidence gates | gate registry v0.1 | fail 阻止 deliverable；warn 可追踪 | M2.2-2.4 |

阶段验收：每个 case 可生成多个候选，记录参数、规则、测量/结构差异、自动评价、人工选择和理由。

## 阶段三｜Day 61—90｜闭环、基准与批量生产

| 里程碑 | 任务 | 交付 | 验收 | 依赖 |
|---|---|---|---|---|
| M3.1 Rule registry | Theory→RuleChange→Approval→Validation | versioned YAML/ledger | 无人批不得 production | M2 |
| M3.2 Golden regression | rule/pipeline replay | regression matrix | 回归失败阻止 release | M3.1 |
| M3.3 Batch/recovery | 批量、幂等恢复、失败隔离 | runbook + integration test | 单任务失败不覆盖/阻塞历史 | M1-2 |
| M3.4 Performance/cost | runtime、人时、成本、失败率 | PPE report | 单位、采集范围明确 | M3.3 |
| M3.5 Human benchmark | A原始/B人工/C Moodify | preregistered report | 盲听、随机、分组、分布、失败保留 | M2.5 |
| M3.6 v0.4 baseline | 发布研究/生产基线 | manifest/changelog/docs | 全部门禁通过或明确 HOLD | 全部 |

阶段验收：新 case 入统一 pipeline；候选可自动/人工评价；Decision 可形成 Theory Note；Rule Change 可在 Golden Set 验证；失败阻止规则发布；输出完整 Music Asset Package。

## 关键路径

Schema/ID → Case adapter → WSE registry → Golden Set → Candidate registry → Evaluation/Decision → Rule registry → Golden regression → v0.4 release。MSE minimal 可与 WSE registry 并行，但 section WSE 依赖稳定 section IDs。


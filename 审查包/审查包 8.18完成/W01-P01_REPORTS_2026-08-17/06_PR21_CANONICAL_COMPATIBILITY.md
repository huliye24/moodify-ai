# 06 — PR #21 Canonical Compatibility

**P01 规则（W01-P01_MASTER_TASK §5）：** 不自动 merge/close/rebase PR #21；只做能力与产品哲学分离评估。

## PR #21 事实（P00 证据）

| 项 | 值 | 证据 |
|---|---|---|
| 标题 | Moodify auditory data factory and quiet-authority aesthetic system | gh pr view 21 |
| 状态 | OPEN / DRAFT | gh pr list |
| Branch | codex/mfy-data-factory-001（head e66cbf9d） | E08 |
| 规模 | 511 文件，+56329/-320，26 commits | E08 |
| CI | CI success；Temporal Texture Guard failure | E09 |
| 冻结协议处置 | KEEP — canonical release carrier（2026-08-11） | E12 |

## 1. 可保留的基础设施能力（工程资产，与产品哲学无关）

| 能力 | 分类建议 | 依据 |
|---|---|---|
| Phase-I auditory data factory（`data_factory` 包） | CANONICAL 候选 | 同一逻辑已在杭州 worker 实跑（10-song pilot 10/10，P00 TT-008/E13/E14） |
| Serial Aliyun worker node（`node` 包） | CANONICAL 候选 | 云端实跑（LA/杭州双节点，TT-009） |
| Restart recovery（recover_interrupted_jobs） | CANONICAL 候选 | 24x7 包验证（TT-008） |
| Rejected-case evidence | CANONICAL 候选 | artifacts/mfy_24x7_data_pipeline_001 |
| 算法评审（MFY-ALGO-REVIEW-FORMULA-001） | CANONICAL | 已在 README/REPOSITORY_STATUS 引用（TT-017） |
| Data Protocol v1（冻结） | CANONICAL | docs/contracts/DATA_PROTOCOL_V1.md |
| Visualization dependency | INTERNAL 工具（非产品卖点） | 不构成对外产品面 |

## 2. 与新 Canon 冲突的产品表述（哲学层）

- PR 标题/正文的「quiet-authority aesthetic system」及旧身份语境语言：属于旧产品表述，**不进入新 Canon**。
- 其中任何「Ear 作为对外产品」的措辞：被 W01-P01 Canon 覆盖（CD-002）。

## 3. 尚未验证的运行能力（不得写成已运行）

- PR 声称的完整 data factory 云端链：云端仅有批处理证据（pilot），无生产流量 → 保持 `DEPLOYED_NOT_VERIFIED`。
- PR 内 Temporal Texture Guard 持续 failure：该 workflow 与新 Canon 无关，属技术债（记入 P00 TT-021，不在此修复）。

## 4. 裁决

| 维度 | 结论 |
|---|---|
| 工程资产 | 保留为 INTERNAL/CANONICAL 候选（能力与哲学分离） |
| 产品表述 | LEGACY（不把旧身份带回 Canon） |
| PR 状态 | **不变**（OPEN/DRAFT；不自动 merge/close/rebase） |
| 合并路径 | 由人类在 W01-P01 后裁决（涉及 main 上 154 commits 的整体去向） |

## 5. 风险提示

- 若直接 merge #21，其产品表述与新 Canon 冲突（需先剥离/改写）；若不 merge，main 持续落后本地 154 commits。
- 两者均为人类决策范围（`HUMAN_DECISION_REQUIRED`，CD-014 附注），本包不做。

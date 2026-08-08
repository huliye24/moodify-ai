# DSK-MFY-CAPABILITY-ACCRETION-021｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 020 HANDOFF 可读且验证/候选可用 | HOLD |
| Q0-02 | P0 | 记录模型/提案机制编码前冻结 | HOLD |
| Q1-01 | P0 | 提案不自动生效，需人工确认 | HOLD |
| Q1-02 | P0 | 政策版本化可审计（每次生效变更入 ledger） | HOLD |
| Q1-03 | P0 | 未验证/未批准候选不进知识基线 | HOLD |
| Q1-04 | P0 | NegativeKnowledgeRecord 存在且失败记录不可删除/改写（只能追加 superseded） | HOLD |
| Q1-05 | P1 | 政策变更引用被替代旧规则及其历史来源（规则可改变不可遗忘） | REWORK |
| Q2-01 | P0 | 最小样本门槛（默认 N≥3）生效 | HOLD |
| Q2-02 | P0 | 低置信度不更新政策 | HOLD |
| Q2-03 | P0 | 记录与 ExecutionRecord/验证结果关联不重复 | HOLD |
| Q2-04 | P1 | JudgmentRecord 理由结构化 | REWORK |
| Q3-01 | P0 | 不修改 008/009/017-020 与 moodify_runtime | HOLD |
| Q3-02 | P0 | 无 MATLAB、网络下载、许可证混淆 | HOLD |
| Q3-03 | P1 | 合成 fixture 端到端（完整知识循环） | REWORK |
| Q3-04 | P1 | 测试、CLI smoke、Ruff、文档通过 | REWORK |
| Q3-05 | P1 | 架构文档含知识循环与对接顺序 | REWORK |

Codex 将独立执行：伪造判断记录、单例触发提案、提案自动生效尝试、政策
回滚、记录关联断裂、低置信度更新、旧 CLI 回归、Ruff。

# DSK-MFY-CAPABILITY-ACCRETION-021｜Phase 5: Knowledge Feedback（知识反馈）

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** DSK-MFY-CAPABILITY-ACCRETION-020 已 ACCEPT（验证与候选可用）  
**执行上限：** 4 小时，阶段严格串行

## 1. 核心目标

用已完成的案例更新 provider 偏好、默认值、阈值与规划规则（论文 Phase 5），
完成"知识循环"：

```text
Production case
-> Measurement record
-> Judgment record
-> Rule-change proposal
-> 版本化生产政策更新
-> 下一个 case
```

本任务聚焦**反馈机制本身**，不做大规模统计模型；数据积累交给后续数据任务。

## 2. 必读与基线

```text
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-021/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-021/02_CODEX_ACCEPTANCE_MATRIX.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-020/HANDOFF.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-020/00_TASK_ORCHESTRATION.md
docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md
moodify-core-package/src/moodify/capability_registry/（017-020 交付）
moodify_runtime/craft_memory.py（了解现有记忆模型，只读）
moodify_runtime/learning_store.py（了解现有学习存储，只读）
moodify_runtime/trend_analyzer.py（了解现有趋势分析，只读）
```

## 3. 范围与许可证边界

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\capability_registry\（含 knowledge\ 子包）
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\capability_registry\
E:\moodify\moodify-core-package\pyproject.toml（仅必要时）
E:\moodify\docs\architecture\CAPABILITY_ACCRETION_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-CAPABILITY-ACCRETION-021\
E:\moodify\outputs\deepseek_validation\DSK-MFY-CAPABILITY-ACCRETION-021\
```

禁止：修改 008/009/017-020 实现、Runtime/Bridge/DSP/MRS、真实歌曲；
复制/修改第三方源码；MATLAB；Git 分支/暂存/提交/推送/reset/clean/stash/
checkout；网络下载。**不得改写 moodify_runtime 现有文件**（只读了解，若需要
接口对接写 SCOPE_CHANGE_REQUEST 由 Codex 决定）。

## 4. 任务内容

### Stage A｜记录模型（60 分钟）

1. `MeasurementRecord`：case 的输入特征、选择的能力/provider、版本、参数、
   中间产物、候选输出、测量值、时间与成本。
2. `JudgmentRecord`：人类或机器决策——批准/拒绝/修订 + 理由（结构化）。
3. **`NegativeKnowledgeRecord`（负面知识记录）**：被拒绝的候选、回退路径、
   验证失败、历史规则来源（020 的 historical_source）作为一等公民持久化。
   知识循环同时保存"什么有效"与"什么无效"——排除的路径是未来
   判断的边界，禁止把失败记录清理为"临时事故"。
4. 记录与 ExecutionRecord（019）/验证结果（020）关联，不重复存储；
   未经验证或未批准的候选不得进入知识基线。

### Stage B｜规则更新机制（90 分钟）

1. `RuleChangeProposal`：变更类型（provider 偏好/默认参数/验证阈值/回退顺序）、
   依据（记录链接，**含负面知识记录**）、影响评估、人工确认状态。
2. 提案不自动生效：默认需人工确认；`policy_version` 递增；
   每次生效的变更写入版本化生产政策（policy ledger）。
   **policy ledger 是地质记录的一部分**：每次规则变更必须引用它替代的旧规则
   及旧规则的历史来源——规则可以被改变，但不能被遗忘（"能改变而不忘记
   历史为何存在"）。
3. 防污染：单例/异常案例不足以触发提案（最小样本门槛，默认 N≥3）；
   低置信度结果不得更新政策。
4. 失忆防护：知识存储支持按时间/案例查询历史，但**禁止删除或改写已生效的
   判断/负面知识记录**（修正只能追加新版本并标注 superseded）。

### Stage C｜CLI 与文档（60 分钟）

1. `moodify capabilities history`（案例/测量/判断记录）、
   `moodify capabilities propose <case_id>`（生成规则变更提案，不自动应用）、
   `moodify capabilities policy`（查看版本化政策）。
2. 架构文档更新：知识层、知识循环、政策版本化、防污染门槛。
3. 测试：记录 round-trip、记录关联、提案生成、最小样本门槛、提案不自动生效、
   政策版本递增、合成 fixture 端到端。
4. 更新 PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF。

## 5. P0 门禁与停止条件

**深度维持验收（系列原则 §3.4）**：后期模式，验收不以改动幅度为准——
①知识层必须让已保存的判断持续可用（查询/关联/版本化），否则等于失忆；
②每次政策变更引用被替代旧规则及来源，规则可改变不可遗忘；
③NegativeKnowledgeRecord 追加式持久化，禁止删除/改写。

必须成立：提案不自动生效；政策版本化可审计；未验证候选不进知识基线；
最小样本门槛生效；记录与执行/验证关联；低置信度不更新政策；旧 CLI 回归。

立即停止：需要安装组件、修改 008/009/017-020 或 moodify_runtime 实现、
MATLAB、范围外写入、真实歌曲、提案自动生效、伪造判断记录、网络下载、
现有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

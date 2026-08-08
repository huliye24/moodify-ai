# DSK-MFY-CAPABILITY-ACCRETION-020｜Phase 4: Validation & Candidate（验证与候选选择）

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** DSK-MFY-CAPABILITY-ACCRETION-019 已 ACCEPT（批准执行可用）  
**执行上限：** 4 小时，阶段严格串行

## 1. 核心目标

执行成功 ≠ 生产成功。为每个能力添加**验证器**，并允许多个 provider/参数变体
生成候选、比较、排序、回退（论文 Gate 6 与 Phase 4）。

```text
ApprovedExecutionEnvelope
-> 执行（经 019 gateway）
-> CapabilityValidator（技术验证）
-> ArtisticReviewHook（可选，人工挂点）
-> Candidate（+ 拒绝理由）
-> 排序/选择/回退
-> 选中候选 -> case deliverable
```

## 2. 必读与基线

```text
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-020/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-020/02_CODEX_ACCEPTANCE_MATRIX.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-019/HANDOFF.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-019/00_TASK_ORCHESTRATION.md
docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md
docs/architecture/SCORE_ENGINE_ARCHITECTURE.md（round-trip 验证思想参考）
moodify-core-package/src/moodify/capability_registry/（017-019 交付）
```

## 3. 范围与许可证边界

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\capability_registry\（含 validation\ 子包）
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\capability_registry\
E:\moodify\moodify-core-package\pyproject.toml（仅必要时）
E:\moodify\docs\architecture\CAPABILITY_ACCRETION_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-CAPABILITY-ACCRETION-020\
E:\moodify\outputs\deepseek_validation\DSK-MFY-CAPABILITY-ACCRETION-020\
```

禁止：修改 008/009/017-019 实现、Runtime/Bridge/DSP/MRS、真实歌曲；
复制/修改第三方源码；MATLAB；Git 分支/暂存/提交/推送/reset/clean/stash/
checkout；网络下载。

## 4. 任务内容

### Stage A｜CapabilityValidator（90 分钟）

1. `ValidationRule`：规则 id、条件、级别（error/warning）、说明、
   **historical_source（地质记录）**——每个规则必须回答一个历史问题：
   "系统曾经丢失了什么区分？哪次失败使这条规则成为必要的边界？"
   规则注册时不得留空；无来源的规则标记 `unproven`，直到来源被补充。
2. 通用规则库：output_exists、nonzero_size、no_nan、duration_alignment、
   peak_within_limit、sample_rate_ok、page_count_nonzero、source_hash_linked。
   规则库本身是**地质记录**：每条通用规则附带其来历（如
   `roundtrip_hidden_loss` ← 009 发现的"成功导出掩盖差异"禁令；
   `no_nan` ← 音频变换的 NaN 污染历史）。
3. 按能力绑定规则集（registry 中 quality_policy 声明决定默认集）；
   规则可扩展，不可被 provider 关闭（防止"成功导出掩盖差异"）。
4. 验证失败即**负面知识**：error 级失败与其测量值进入候选的
   RejectionReason 并持久化——被拒绝的路径与成功的路径同样属于系统记忆，
   禁止清理为"临时事故"。

### Stage B｜候选生成与选择（90 分钟）

1. `CandidateGenerator`：对同一能力生成多个候选（多 provider 或参数变体），
   每个候选绑定独立 ApprovedExecutionEnvelope（019 不变性保证）。
2. `CandidateRanker`：按验证分数 + 显式权重排序；保留全部候选与拒绝理由。
3. `RejectionReason`：结构化（rule_id + 测量值 + 期望值），禁止模糊拒绝。
   被拒绝的候选与理由**完整保留**在候选档案中（负面知识），不删除、
   不改写为成功——它们是未来判断"哪种改进值得重试"的地质层。
4. 回退/重试策略：provider 不可用或验证失败 → 按策略换 provider（仅限
   registry 中 declared fallback，不隐式乱换）；每次回退的理由也进入
   负面知识记录。

### Stage C｜CLI 与文档（60 分钟）

1. `moodify capabilities validate <run_dir>`（重放验证）、
   `moodify capabilities candidates <envelope.json>`（生成候选并排序）。
2. 架构文档更新：验证层、候选生命周期、回退策略、人工挂点。
3. 测试：规则库、按能力绑定、候选排序、拒绝理由结构化、回退、双运行、
   合成 fixture 端到端。
4. 更新 PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF。

## 5. P0 门禁与停止条件

**深度维持验收（系列原则 §3.4）**：后期模式，验收不以改动幅度为准——
①每条新规则带 historical_source（地质记录），无来源标记 unproven；
②规则库每次扩充必须来自真实失败的区分，禁止为凑数量造规则；
③验证失败候选与理由完整保留，禁止清理为"临时事故"。

必须成立：验证不可被 provider 绕过；候选全部保留；拒绝理由结构化；
回退只走声明路径；验证分数双运行一致；失败候选不进入交付；旧 CLI 回归。

立即停止：需要安装组件、修改 008/009/017-019 实现、MATLAB、范围外写入、
真实歌曲、隐藏失败候选、隐式换 provider、网络下载、现有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

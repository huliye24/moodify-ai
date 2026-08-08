# DSK-MFY-CAPABILITY-ACCRETION-019｜Phase 3: Approved Execution（批准执行集成）

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** DSK-MFY-CAPABILITY-ACCRETION-018 已 ACCEPT（适配器可用）  
**执行上限：** 4 小时，阶段严格串行

## 1. 核心目标

要求**每一次 provider 执行都源自批准的案例**，并返回执行记录（论文 Law 3：
"每次执行都属于一个案例"）。外部工具永远不能成为不受控的生产权威。

```text
Case
-> Specification
-> Analysis
-> Plan
-> 技术验证
-> 艺术批准
-> ApprovedExecutionEnvelope（不可变）
-> Adapter 执行
-> ExecutionRecord 回写 case
```

## 2. 必读与基线

```text
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-019/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-019/02_CODEX_ACCEPTANCE_MATRIX.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-018/HANDOFF.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-018/00_TASK_ORCHESTRATION.md
docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md
moodify-core-package/src/moodify/capability_registry/（017/018 交付）
moodify-core-package/src/moodify/cli_v2/main.py（了解现有 case 模型，只读）
moodify_runtime/craft_memory.py（了解现有记录模型，只读）
```

## 3. 范围与许可证边界

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\capability_registry\（含 execution\ 子包）
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\capability_registry\
E:\moodify\moodify-core-package\pyproject.toml（仅必要时）
E:\moodify\docs\architecture\CAPABILITY_ACCRETION_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-CAPABILITY-ACCRETION-019\
E:\moodify\outputs\deepseek_validation\DSK-MFY-CAPABILITY-ACCRETION-019\
```

禁止：修改 008/009 实现、Runtime/Bridge/DSP/MRS、真实歌曲；复制/修改第三方
源码；MATLAB；Git 分支/暂存/提交/推送/reset/clean/stash/checkout；网络下载。
**本任务不强行接入 cli_v2 case 系统**（只读了解，避免大爆炸改造）——先做
独立 Envelope/Record 模块与最小 CLI 证明，接入顺序在架构文档注明。

## 4. 任务内容

### Stage A｜ApprovedExecutionEnvelope（60 分钟）

不可变执行描述，包含：

- case_id、capability_id、provider_id（显式选定，不自动路由）
- 输入清单（路径 + SHA-256 + 角色）
- 参数（冻结，类型化）
- 权限（网络 off、输出位置白名单、允许的命令）
- 资源限制（timeout、无并行、工作目录策略）
- 批准签名（签发者、签发时间、policy_version）
- 批准后不可变：任何变更产生新 envelope（新签名），旧 envelope 失效

### Stage B｜ExecutionRecord 与执行网关（90 分钟）

1. `ExecutionGateway`：唯一执行入口。校验 envelope 完整性（哈希/签名/状态）→
   调用 adapter → 组装 `ExecutionRecord`（provider、版本、环境、输入、参数、
   timing、输出、日志、exit code、evidence）→ 写回 case 存储。
2. 未授权执行检测：绕过 gateway 直接调用 adapter 的调用在测试中可被识别
   （adapter 记录 caller 身份或 gateway 维护执行中集合）。
3. 状态机：envelope_created → approved → executing → completed/failed；
   失败保留完整 evidence，不静默丢弃。

### Stage C｜CLI 与文档（60 分钟）

1. `moodify capabilities plan`（由 capability + 参数生成候选 envelope 草案）、
   `moodify capabilities approve`（本地签发，模拟批准）、
   `moodify capabilities execute <envelope.json>`（经 gateway 执行）。
2. 架构文档更新：执行层、envelope 生命周期、与 cli_v2 case 的对接顺序。
3. 测试：envelope 不可变性、哈希/签名校验、状态转换、未授权执行拒绝、
   失败记录完整、双运行、合成 fixture 端到端。
4. 更新 PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF。

## 5. P0 门禁与停止条件

**深度维持验收（系列原则 §3.4）**：后期模式，验收不以改动幅度为准——
①每次执行失败的完整 evidence（命令/版本/日志/exit code/哈希）必须可
持久化为地质记录，禁止只保留成功路径；②gateway 本身不引入新的隐式
依赖或未记录状态（否则等于把复杂性藏回人脑）；③envelope 生命周期
文档化后不依赖创建者记忆。

必须成立：无 envelope 不得执行；envelope 不可变；输入哈希锁定；执行经唯一
gateway；未授权调用可被拒绝/识别；失败 evidence 完整；provider 只拿到
授权范围内的输入/参数/输出位置；旧 CLI 回归。

立即停止：需要安装组件、修改 008/009 实现、MATLAB、范围外写入、真实歌曲、
绕过网关的执行路径、网络下载、现有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

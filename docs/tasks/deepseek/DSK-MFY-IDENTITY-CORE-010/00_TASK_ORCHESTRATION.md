# DSK-MFY-IDENTITY-CORE-010｜作品身份守恒核心 v0.1

**计划日期：** 2026-08-03  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** 009 已形成可读 HANDOFF；否则 HOLD  
**执行上限：** 6 小时，四阶段严格串行

## 1. 唯一目标

Moodify 的核心不是分轨、MIDI、曲谱、DSP 或自动评分。本任务只建立：

> 在不替创作者作最终决定的前提下，比较 Source 与 Candidate，说明作品身份
> 中哪些被保留、哪些按意图改变、哪些意外改变、哪些仍不确定，并把判断
> 所需证据交给 Owner。

最小闭环：

```text
OnePointSpec + Source + Candidate + Evidence
       -> Identity Conservation Assessment
       -> PRESERVED / INTENDED_CHANGE / UNEXPECTED_CHANGE / UNCERTAIN
       -> blind review package
       -> Owner decision record
       -> non-promoted Craft observation
```

不产生总分，不自动声明 improved/Final，不把启发式冒充作品理解。

## 2. 必读事实源

完整读取并冻结必要哈希：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-IDENTITY-CORE-010\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-IDENTITY-CORE-010\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-IDENTITY-CORE-010\03_PRINCIPLE_SEED.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SCORE-ENGINE-009\HANDOFF.md
E:\moodify\docs\strategy\MOODIFY_ONE_POINT_PRINCIPLE.md
E:\moodify\docs\architecture\MOODIFY_ONE_POINT_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\ONE_POINT_CONTRACT.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\LANGUAGE_CANON.md
E:\moodify\docs\architecture\WSE_ARCHITECTURE.md
E:\moodify\docs\architecture\MSE_ARCHITECTURE.md
E:\moodify\docs\architecture\PPE_ARCHITECTURE.md
E:\moodify\moodify-bridge\src\moodify_bridge\schemas.py
E:\moodify\moodify-bridge\src\moodify_bridge\services.py
E:\moodify\moodify-bridge\src\moodify_bridge\cli.py
E:\moodify\moodify-bridge\tests\test_one_point.py
```

检查适用 `AGENTS.md`、Git/dirty 状态、测试基线和现有比较/Craft/审批实现。
现存修改和未跟踪文件属于用户，不得覆盖、还原、整理、暂存或提交。

## 3. 修改范围

允许修改：

```text
E:\moodify\moodify-bridge\src\moodify_bridge\
E:\moodify\moodify-bridge\tests\
E:\moodify\moodify-bridge\README.md
E:\moodify\docs\strategy\MOODIFY_ONE_POINT_PRINCIPLE.md
E:\moodify\docs\architecture\MOODIFY_ONE_POINT_ARCHITECTURE.md
E:\moodify\docs\architecture\IDENTITY_CONSERVATION_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-IDENTITY-CORE-010\
E:\moodify\outputs\deepseek_validation\DSK-MFY-IDENTITY-CORE-010\
```

禁止修改 Core DSP、Runtime、MRS、Preset、008/009 实现、数据库 migration、
DuckDB schema、外部模型、真实歌曲和客户资产；禁止新增依赖、联网和Git操作。
必须优先通过 adapter 复用现有 WSE/MSE/PPE/比较/审批事实。需越界则 HOLD。

## 4. Stage 0｜独特核心合同与可证伪边界（75 分钟）

编码前交付：

- `00_IMPLEMENTATION_AUDIT.md`：现有能力与缺口，不把设计当完成事实；
- `IDENTITY_CONSERVATION_CONTRACT.md`：输入、状态、finding、证据、失败码；
- `EVIDENCE_ALIGNMENT_CONTRACT.md`：声明/WSE/MSE/PPE/人工证据如何并列；
- `HUMAN_SOVEREIGNTY_CONTRACT.md`：Owner decision、盲听和禁止自动 Final；
- `FALSIFIABILITY_PLAN.md`：什么结果能证明当前身份判断无效或过度自信；
- `STAGE_0_GATE.md`：合同冻结且未增加第二个产品中心。

合同必须区分：source fact、owner declaration、deterministic observation、limited
inference、unknown、conflict。任何 finding 必须引用 evidence IDs；证据不足时
只能 `UNCERTAIN/NEEDS_EVIDENCE`，不得由缺失值推断“守恒”。

## 5. Stage 1｜身份守恒报告最小实现（105 分钟）

1. 新增严格版本化对象：IdentityConstraint、EvidenceRef、ConservationFinding、
   IdentityConservationReport；不破坏 OnePointSpec/Result 兼容性。
2. 输入为已登记 Source/Candidate 资产与证据引用，不直接重做 DSP 或测量。
3. 将 `must_preserve/desired_change/must_avoid` 映射为可检查约束；无法机器检查
   的内容明确标 `human_only`，不得做关键词命中即“理解作品”。
4. 输出四种 finding：PRESERVED、INTENDED_CHANGE、UNEXPECTED_CHANGE、
   UNCERTAIN；每项含依据、适用边界、置信来源、Owner question。
5. 不输出总分、排名、Final、自动审批；硬冲突不得被其他指标冲销。
6. 默认表面仍只有 Essence/Protect/Allow/Action/Entrust，完整报告在 evidence。

必须测试：缺失证据、冲突证据、human_only、未知字段、重复/断裂引用、路径
逃逸、资产哈希不匹配、空约束、确定性、正文/内部术语默认表面泄漏。

## 6. Stage 2｜Candidate、盲听、Owner与Craft观察（105 分钟）

1. 构建不泄露版本身份的 review package，记录响度匹配状态；未匹配时警告，
   不伪称盲听公平。
2. Owner decision 只能由显式输入产生：选择、拒绝、继续比较或不确定；记录
   理由和时间，但不让系统代填偏好。
3. Candidate 未经 Owner 决定不得成为 Final；技术门通过不等于身份通过。
4. 将一次决策写成 `CraftObservation`：上下文、动作、结果、Owner理由、限制；
   默认 `NOT_PROMOTED`，不自动生成普遍规则或改变Preset。
5. 建立最小 CLI，名称由 Stage 0 审计后冻结；建议沿用 `refine assess` 与
   `refine decide`，不得破坏 `refine prepare`。

测试：身份隐藏、映射隔离、顺序确定/可审计、未响度匹配、无Owner、重复
决策、篡改包、未批准Final、Observation不晋级、旧006/007行为回归。

## 7. Stage 3｜证据、真实边界与继承（75 分钟）

1. 用合成/明确fixture构造：完全相同、预期改变、意外损伤、证据冲突、证据
   缺失五类案例；不处理真实客户音频。
2. 两个新目录双运行；除显式随机盲听映射外，规范化报告一致；映射可复核但
   评审前隔离。
3. 运行新增测试、Bridge全量回归、Ruff、Mypy、CLI smoke；记录未运行项。
4. `FAILURE_LEDGER.md` 至少覆盖12类失败；源资产和只读基线哈希不变。
5. 更新架构、README、`VALIDATION_REPORT.md`、`PROGRESS.md`、`INHERITANCE.md`、
   `HANDOFF.md`。
6. `CORE_CLAIM_BOUNDARY.md` 明确“已实现、已验证、仍是假设”，禁止宣称优于
   成熟制作人或形成商业护城河，除非证据真实存在。

## 8. P0门禁与停止条件

必须成立：无自动Final/总分；Owner主权真实；finding有证据引用；缺失证据
不伪装守恒；默认五中心不扩张；source/candidate不覆盖；Craft不自动晋级；
旧One-Point兼容；失败与限制完整保留。

立即停止：009无HANDOFF、Stage 0未PASS即编码、需要新依赖/migration、用
关键词或单一指标宣称身份、自动代填Owner判断、自动晋级Craft、范围外写入、
真实歌曲被处理、既有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。DeepSeek无权
宣布ACCEPT、产品独有性已证明或产业优势成立。


# DSK-MFY-KNOWLEDGE-LAYERS-022｜三层知识结构（原理层 / 经验层 / 代码层）

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** 无硬依赖（不要求 017-021 ACCEPT；但需读取其编排与失败台账作素材）  
**执行上限：** 4 小时，阶段严格串行

## 1. 核心目标

项目现状：原理（strategy/ADR/POSC）、经验（FAILURE_LEDGER/交接单）与代码
三层都有素材，但**不成体系**——没有层次定义、没有层间追溯、没有单一入口。
本任务建立两层注册表 + 一个追溯约定，让三层形成闭环：

```text
原理层（为什么必须这样）      docs/standards/PRINCIPLE_REGISTRY.md
   ↑ 约束
工程经验层（哪次失败教会我）  docs/standards/EXPERIENCE_REGISTRY.md
   ↑ 防复发
代码功能层（现在的规则/测试） src/ + tests/（只读，不修改）
```

## 2. 必读与基线

```text
docs/tasks/deepseek/DSK-MFY-KNOWLEDGE-LAYERS-022/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-KNOWLEDGE-LAYERS-022/02_CODEX_ACCEPTANCE_MATRIX.md
docs/tasks/deepseek/DSK-MFY-KNOWLEDGE-LAYERS-022/03_PRINCIPLE_SEED.md
docs/strategy/MOODIFY_INDUSTRIAL_DIRECTION.md
docs/strategy/MOODIFY_CIVILIZATIONAL_DEVELOPMENT_MODEL.md
docs/strategy/MOODIFY_ENGINEERING_THICKNESS_STANDARD.md
docs/decisions/ADR-001..004（全部四个）
docs/standards/FAILURE_LEDGER.md
docs/standards/CRAFT_EVIDENCE_LEDGER.md
docs/standards/STANDARD_EVOLUTION_LEDGER.md
docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/FAILURE_LEDGER.md
docs/tasks/deepseek/DSK-MFY-STEM-MIDI-008/FAILURE_LEDGER.md（若存在）
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/00_SERIES_ORCHESTRATION.md
E:\软件建造的哲学\markdown\POSC_003_*.md（地质记录原则）
docs/architecture/PPE_ARCHITECTURE.md
```

材料盘点以**实际文件为准**；文件缺失或路径变化时记录并跳过，不编造。

## 3. 范围与许可证边界

允许修改：

```text
E:\moodify\docs\standards\PRINCIPLE_REGISTRY.md（新建）
E:\moodify\docs\standards\EXPERIENCE_REGISTRY.md（新建）
E:\moodify\docs\tasks\deepseek\DSK-MFY-KNOWLEDGE-LAYERS-022\
E:\moodify\docs\architecture\THREE_LAYER_KNOWLEDGE.md（新建，追溯约定主文档）
```

禁止：修改任何 src/ 代码、tests/、008/009/017-021 任务包已有文件、
strategy/decisions/standards 既有文件（只读引用）；MATLAB；Git 分支/暂存/
提交/推送/reset/clean/stash/checkout；网络下载；真实歌曲。

## 4. 任务内容

### Stage 0｜盘点与合同冻结（45 分钟）

1. 盘点三层现状：原理素材清单（strategy/ADR/POSC）、经验素材清单
   （各 FAILURE_LEDGER/交接单/audits）、代码模块清单（src 顶层模块）。
2. 冻结注册表 schema：
   - 原理条目：`PR-0xx` + 一句话原理 + 来源（文档/章节或 ADR 编号）+
     适用范围（模块/阶段）+ 关联经验 ID（可空）。
   - 经验条目：`EX-0xx` + 失败事实 + 根因 + 边界（什么条件下失效）+
     防复发机制（对应哪条测试/规则/流程）+ 关联模块 + 关联原理 ID（可空）。
3. 交付 `STAGE_0_GATE.md`：schema 冻结且盘点真实（数量、来源可核对）。

### Stage B｜原理注册表（60 分钟）

从 strategy/ADR/POSC/架构文档提取首批原理（预计 8-12 条），每条：
ID、原理陈述、来源、适用范围、关联经验（初始可空，Stage C 回填）。
示例（以实际材料为准）：

```text
PR-001 生产以案例为单元，工具执行受批准包络约束（来源：ADR-003）
PR-002 证据先于宣称：无证据不宣称优越性（来源：ADR-004）
PR-003 工具拥有执行，Moodify 拥有解释权（来源：能力引力井论文 §4.3）
PR-004 推断不冒充事实，未确认保持 unknown（来源：009 MOODIFYSCORE 合同）
PR-005 规则可改变，不可遗忘（来源：POSC-003 地质记录原则）
PR-006 深度 = 复杂性转化为形式，厚度 ≠ 深度（来源：POSC-003）
```

### Stage C｜经验注册表（75 分钟）

从现有 FAILURE_LEDGER/交接单/audits 提取首批经验（预计 10-15 条），
每条：ID、失败事实、根因、边界、防复发机制、关联模块、关联原理。
示例（以实际材料为准）：

```text
EX-001 MuseScore 4.5.1 一次仅接受一个 -o 且不支持 -I 参数
       → 防复发：009 backend 分两次 argv 调用 + 测试
       → 关联原理：PR-003
EX-002 多页 SVG 自动带页码后缀，目标路径收集失败
       → 防复发：glob stem-*.svg 收集 + 测试
EX-003 round-trip 必须重解析并报告差异，禁止"成功导出"掩盖
       → 防复发：roundtrip_report.json verdict 门禁
       → 关联原理：PR-002 / PR-005
```

从 008/009/017 系列失败台账中选取至少 3 条真实失败（不得编造）。

### Stage D｜追溯约定与验证（60 分钟）

1. `THREE_LAYER_KNOWLEDGE.md`：三层定义、注册表维护规则（新增条目必须
   来自真实失败/真实决策，禁止凑数）、引用约定（任务包/交接单写
   PR-xxx/EX-xxx）、反向索引方法。
2. 引用约定示范：在 022 的 HANDOFF 中引用本次新建的 PR/EX 条目。
3. 验证：注册表条目全部有来源且可核对；经验条目防复发机制可对应到
   实际文件/测试；编号连续无重复；Markdown 结构一致。
4. 更新 `PROGRESS.md`、`VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、
   `HANDOFF.md`。

## 5. P0 门禁与停止条件

**深度维持验收（系列原则 §3.4，POSC-003）**：本任务产出全部为知识层，
验收不以改动幅度为准：①注册表条目必须全部携带真实来源（无来源=失忆，
REWORK）；②经验条目的防复发机制必须可核对（指向真实文件/测试/流程）；
③本任务自身新增的失败（如有）记入 FAILURE_LEDGER，不删除不改写。

必须成立：不修改任何代码与既有文档；来源可核对；无编造条目；编号无冲突；
Markdown 可读；MATLAB/网络/git 禁令遵守。

立即停止：发现素材不足却编造条目、需要修改代码/既有文档、范围外写入、
真实歌曲、网络下载、现有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

# DSK-MFY-ONE-POINT-006｜让这首音乐成为它自己

**日期：2026-08-01**  
**任务性质：Moodify 原理中心化与产品形式跃迁**  
**执行 Worker：DeepSeek**  
**最终 Judge、验收与收尾：Codex / 授权用户**  
**执行方式：三阶段严格串行；每阶段必须先形成可验收闭环，再进入下一阶段**

## 1. 唯一中心

Moodify 的所有复杂能力必须服从一句话：

> **让这首音乐成为它自己。**

更深的动作不是增强、修饰、标准化或替代，而是：

> **成全。**

Moodify 识别作品已经包含但尚未充分显现的秩序，在不损害作品身份的前提下，以克制、可逆、可验证的工艺帮助它完成自身。系统内部可以复杂，正式产品形式必须安静、清晰，并把复杂性放在需要它的深度，而不是转嫁给操作者。

本任务不是品牌文案，不是 UI 换肤，也不是大规模重写。它必须把该原则落实为：

1. 一个稳定的产品语言；
2. 一个唯一默认入口；
3. 一个最小但真实的输入合同；
4. 一个渐进披露的结果形式；
5. 一组能阻止系统背叛该原则的机器测试。

## 2. 不可改变的战略边界

本任务必须服从现行战略：

- Moodify 是供音乐公司调用的无创作者前端音乐处理基础设施；
- 荣景文川/授权制作人负责理解创作者、定义艺术方向和最终选择；
- Moodify 负责诊断、处理计划、候选、技术门、证据、版本和工艺继承；
- 不建设消费级“一键变好听”产品；
- 不自动选择 Final，不以分数替代艺术判断；
- 不把 WSE/MSE/PPE 删除，它们应退到内部秩序和可展开证据层；
- 不破坏 `v2.0.0-mvp`、现有 Workspace、Runtime、Bridge 或历史记录。

## 3. 必读事实源

开始前完整读取：

```text
E:\软件建造的哲学\POSC_002_Function_Is_Not_Form_Edition_0.1.pdf
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\03_PRINCIPLE_SEED.md
E:\moodify\docs\strategy\MOODIFY_MUSIC_PROCESSING_INFRASTRUCTURE.md
E:\moodify\docs\strategy\MOODIFY_ENGINEERING_THICKNESS_STANDARD.md
E:\moodify\docs\architecture\MOODIFY_SYSTEM_ARCHITECTURE_v0.4.md
E:\moodify\docs\architecture\CURRENT_TO_TARGET_MODULE_MAP.md
E:\moodify\docs\architecture\WSE_ARCHITECTURE.md
E:\moodify\docs\architecture\MSE_ARCHITECTURE.md
E:\moodify\docs\architecture\PPE_ARCHITECTURE.md
E:\moodify\moodify-bridge\README.md
E:\moodify\moodify-bridge\src\moodify_bridge\schemas.py
E:\moodify\moodify-bridge\src\moodify_bridge\services.py
E:\moodify\moodify-bridge\src\moodify_bridge\cli.py
E:\moodify\docs\tasks\deepseek\DSK-MFY-PPE-HARDENING-005\CODEX_FINAL_ACCEPTANCE_2026-08-01.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\02_CODEX_ACCEPTANCE_MATRIX.md
```

同时查找并遵守适用 `AGENTS.md`，记录 Git、dirty 状态、Python 和现有测试。所有现存修改和未跟踪文件均属于用户。

## 4. 允许与禁止范围

允许修改：

```text
E:\moodify\moodify-bridge\src\moodify_bridge\
E:\moodify\moodify-bridge\tests\
E:\moodify\moodify-bridge\README.md
E:\moodify\docs\strategy\MOODIFY_ONE_POINT_PRINCIPLE.md          # 新文件
E:\moodify\docs\architecture\MOODIFY_ONE_POINT_ARCHITECTURE.md  # 新文件
E:\moodify\docs\tasks\deepseek\DSK-MFY-ONE-POINT-006\
E:\moodify\outputs\deepseek_validation\DSK-MFY-ONE-POINT-006\
```

禁止修改：

- `moodify-core-package`、`moodify_runtime`、Workspace、DSP、Preset、MRS；
- `moodify-bridge/migrations`、现有 DuckDB schema、demo 原件；
- 8 月 1 日历史输出和上一轮 Codex 验收基线；
- 真实音频、客户资产和权利未确认材料；
- 根 README 和现行 v0.4 战略文件（本任务新增两个增量文件，不覆盖历史）；
- Git 分支、暂存区、提交、远程。

禁止联网、安装依赖、删除旧入口、批量改名、搬迁模块或以破坏兼容性的方式“统一”。如果确实需要越界，写 `SCOPE_CHANGE_REQUEST.md` 后停止并判定 HOLD。

## 5. 产品形式目标

Stage 1 必须根据仓库事实确定最终名称；默认建议建立一个兼容门面：

```powershell
py -3.12 -m moodify_bridge.cli refine run SPEC.yaml --output-dir NEW_DIR
```

“refine”只在真实执行范围内使用。如果当前实现只能形成计划和证据，命令必须诚实命名为 `refine prepare`，不得用 `run` 暗示已经生成音频。

外部默认只表达五件事：

```text
作品是什么（Essence）
什么必须保留（Protect）
什么可以改变（Allow）
系统实际做了什么（Action）
什么仍需人来决定（Entrust）
```

内部 WSE/MSE/PPE、指标、Gate、ledger、版本和日志仍完整保存，但放入可展开的 Evidence/Technical Detail，而不是默认主叙事。

## 6. 三阶段总览

```text
Stage 1｜归一：找到不可再减少的中心
Stage 2｜成形：让复杂能力服从一个入口和一个结果形式
Stage 3｜留白：删除暴露、验证继承、封存高级秩序
```

---

# Stage 1｜归一：原理、语言与边界

## 目标

在编码前证明“一个点”是什么，并区分哪些复杂性必须存在、哪些必须隐藏、哪些应该停止新增。

## 工作

1. 冻结 Git、测试、入口、对象和现有产物事实。
2. 建立 `COMPLEXITY_INVENTORY.md`：逐项列出 WSE/MSE/PPE/MRS/Craft/Case/Gate/Runtime/Workspace 对唯一中心的贡献。
3. 为每项给出唯一分类：
   - `VISIBLE`：操作者完成任务必须直接理解；
   - `PROGRESSIVE`：需要时展开；
   - `INTERNAL`：默认隐藏但保留证据；
   - `DEFER/REMOVE_FROM_DEFAULT`：不再进入默认形式。
4. 建立 `LANGUAGE_CANON.md`，冻结不超过 12 个外部词；禁止同义概念并列争夺解释权。
5. 建立 `ONE_POINT_CONTRACT.md`，定义最小输入、输出、状态、失败、人工责任和兼容映射。
6. 输出两个增量文件：
   - `docs/strategy/MOODIFY_ONE_POINT_PRINCIPLE.md`
   - `docs/architecture/MOODIFY_ONE_POINT_ARCHITECTURE.md`
7. 写 `STAGE_1_GATE.md`，逐条证明方案不是创作者前端、不是一键母带、不是删掉工程证据。

## Stage 1 门禁

- 唯一中心能解释全部现有核心能力，但不被任何单一模块替代；
- 外部词汇不超过 12 个；
- 默认主路径不出现 WSE/MSE/PPE/MRS 等内部缩写；
- 每个被隐藏的概念都有明确的证据展开路径；
- 没有代码修改先于合同冻结；
- Codex 验收矩阵的 S1 项全部可证。

未通过则 `REWORK`，不得进入 Stage 2。

---

# Stage 2｜成形：单一入口与渐进披露

## 目标

实现一个真实、兼容、可复现的 One-Point 门面，使操作者从一个意图合同进入，并得到一个以作品为中心的结果包。

## 最小实现

根据 Stage 1 的事实设计，优先在 Bridge 合同孵化层新增：

1. **OnePointSpec（或事实证明更合适的名称）**
   - case/资产引用；
   - `essence`：作品已经是什么；
   - `must_preserve`：不可损伤；
   - `desired_change`：希望显现的变化；
   - `must_avoid`：禁止副作用；
   - `human_owner`：最终判断责任人；
   - 可选限制和交付条件。
2. **OnePointResult**
   - 输入身份；
   - 五项默认叙事；
   - 状态：`READY_FOR_HUMAN_REVIEW / NEEDS_EVIDENCE / BLOCKED` 等经 Stage 1 冻结的少量状态；
   - 技术证据入口，而不是技术细节堆叠；
   - 不得存在自动 Final 字段。
3. **单一 CLI**
   - 严格新目录；
   - 复用已验收 PPE Runner/ledger/gates，不平行复制；
   - 保存环境、命令、闸门、报告和 SHA-256；
   - 预期失败无 traceback、有稳定错误码。
4. **渐进披露结果包**

```text
NEW_DIR/
  result.json             # 五项核心结果与状态
  summary.md              # 默认阅读面，不出现内部缩写堆叠
  summary.html            # 同一信息架构，克制、可访问
  evidence/               # 完整技术证据、gate、manifest、ledger 链接
  FINAL_STATUS.txt
```

5. **兼容适配**
   - 不改旧 schema/migration；
   - 通过引用/adapter 使用 ProductionCase、PPE 结果和既有证据；
   - 旧入口继续工作并有回归测试。

## 必须测试

- strict schema、未知字段拒绝；
- essence/protect/allow/avoid 为空或互相冲突；
- human_owner 缺失；
- 输入资产不存在或哈希不一致；
- 输出目录非空；
- 默认 summary 不泄漏内部缩写和无关指标；
- evidence 路径全部存在且哈希匹配；
- 人工责任始终显式；
- 相同输入的规范化结果一致；
- 旧 CLI 和全部 Bridge 测试不回归。

## Stage 2 门禁

- 一个命令生成完整结果包；
- 默认层只表达五项核心内容；
- 技术复杂性未丢失，可从 evidence 层审计；
- 未生成音频时不使用“processed/improved/final”等虚假措辞；
- 没有人工判断时状态不得等于完成；
- Codex 验收矩阵 S2 项全部可证。

---

# Stage 3｜留白：减法、工艺与继承

## 目标

证明高级秩序不是新的一层复杂包装，而是让不必要的复杂性从默认形式中退场，同时保留专业深度。

## 工作

1. 建立 `DEFAULT_SURFACE_AUDIT.md`，逐项检查默认 CLI、summary、README 是否只保留必要内容。
2. 建立 `SUBTRACTION_LEDGER.md`：记录隐藏、合并、延后和拒绝新增的概念及原因；不删除历史代码。
3. 对 summary HTML 做视觉与可访问性检查：层级、留白、行宽、对比度、键盘阅读顺序；禁止装饰性仪表盘、分数墙和技术炫耀。
4. 建立 `PRINCIPLE_REGRESSION_TESTS`：未来任何改动若出现以下行为必须失败：
   - 默认层出现未经允许的内部术语；
   - 自动宣称“更好听”或 Final；
   - 隐藏缺失证据；
   - 省略 must_preserve、must_avoid 或 human_owner；
   - 结果无法追溯到输入和技术证据。
5. 两个全新目录独立复现；执行不少于 8 类失败注入。
6. 更新 Bridge README：首先解释唯一动作，再提供渐进式技术入口。
7. 生成：
   - `VALIDATION_REPORT.md`
   - `FAILURE_LEDGER.md`
   - `INHERITANCE.md`
   - `HANDOFF.md`
8. 最终输出只可为：`READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

## Stage 3 门禁

- 新增默认概念数量少于被隐藏/合并的概念数量；
- 后来者只读 One-Point README/HANDOFF 可复现；
- 原理回归测试、全部 Bridge 测试、Ruff、Mypy 通过；
- 双运行和失败矩阵证据完整；
- demo、旧验收基线和历史资产哈希不变；
- DeepSeek 不自行宣布最终 ACCEPT。

---

## 7. 强制质量原则

### 7.1 身份优先

任何 desired change 都不得覆盖 must_preserve。冲突必须 BLOCKED，而不是自动权衡。

### 7.2 克制优先

每个可见字段、状态和按钮都必须证明其必要性。仅仅“有数据”不构成展示理由。

### 7.3 可逆优先

源资产永不覆盖；新输出有身份、血缘和回退路径。

### 7.4 诚实优先

系统必须区分：知道、推断、不知道、需要人判断。没有证据时不生成漂亮结论。

### 7.5 人类主权

Moodify 可以准备、解释、比较和阻断，但最终艺术选择属于明确的人。

## 8. 每阶段记录格式

每阶段必须更新 `PROGRESS.md`：

```text
阶段 / 开始结束时间 / 基线哈希 / 阅读文件 / 决策
修改文件 / 命令 / 退出码 / 测试数 / 失败注入
默认形式减少了什么 / 复杂性被保存在哪里 / 未解决限制
阶段门禁：PASS / REWORK / HOLD
```

## 9. 停止条件

发生以下任一情况立即 HOLD：

- 修改范围外文件；
- 只读资产哈希变化；
- 需要修改 migration/schema；
- 需要真实音频、联网或新增依赖；
- 为追求“简单”而删除证据、失败或人工审批；
- 为追求“大跃迁”而大规模重写现有系统；
- 默认形式宣称声音改善，但没有真实候选与人工评价；
- Stage 1 未通过即开始编码。

## 10. 最终交付

DeepSeek 必须交付：

```text
docs/tasks/deepseek/DSK-MFY-ONE-POINT-006/
  00_IMPLEMENTATION_AUDIT.md
  COMPLEXITY_INVENTORY.md
  LANGUAGE_CANON.md
  ONE_POINT_CONTRACT.md
  STAGE_1_GATE.md
  PROGRESS.md
  DEFAULT_SURFACE_AUDIT.md
  SUBTRACTION_LEDGER.md
  VALIDATION_REPORT.md
  FAILURE_LEDGER.md
  INHERITANCE.md
  HANDOFF.md

docs/strategy/MOODIFY_ONE_POINT_PRINCIPLE.md
docs/architecture/MOODIFY_ONE_POINT_ARCHITECTURE.md
```

以及允许目录中的实现、测试和：

```text
outputs/deepseek_validation/DSK-MFY-ONE-POINT-006/
  run_a/
  run_b/
  failure_matrix/
  readonly_hashes_before.json
  readonly_hashes_after.json
  normalized_comparison.json
```

完成后停止，等待 Codex 独立验收和必要收尾。


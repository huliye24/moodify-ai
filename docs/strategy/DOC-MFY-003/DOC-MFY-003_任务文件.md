# DOC-MFY-003｜任务文件

> 文档编号：DOC-MFY-003
> 版本代号：v0.4 — Acoustic Compliance Upgrade (ACU)
> 生成日期：2026-07-02 15:37 (Asia/Singapore, UTC+8)
> 上游文档：DOC-MFY-002（声学理论合规审计与第二代研发路线图）
> 下游输出：EXP-MFY 声学实验任务 / ENG-MFY 工程实现任务
> 状态：草稿 — 待 Founder/CTO 签核

---

## T0 建立项目章程元数据

**状态：** ✅ 完成

**产物：**
- `metadata.json` — 机器可读元数据（doc_id, version, milestones, formulas, aep_tasks, deliverables）
- 所有 markdown 文件头包含文档编号、版本代号、日期、责任人

**验收证据：**
- `metadata.json` 位于 `DOC-MFY-003/metadata.json`
- 包含所有 10 个 AEP 任务、6 个里程碑、2 个公式、15 项交付物清单

---

## T1 定义项目目标

**状态：** ✅ 完成

**产物：**
- 目标声明（`markdown/00_project_charter.md` §0）
- 成功判定 6 条全部可量化

**核心目标：**
- 将 Moodify 声学合规度 A_compliance 从 65/100 提升至 88/100
- 修复 2 个 P0 声学理论与实现缺口
- 建立感知声学基础设施建设入口

**验证口径：**
- [x] 目标可量化（A_compliance: 65 → 88）
- [x] 成功判定有具体阈值（MRS 差值 < 2.0 分, ruff/pytest 全通过）
- [x] 不是 UI/商业/大模型项目

---

## T2 确定范围边界

**状态：** ✅ 完成

**产物：**
- 范围表（`markdown/01_scope_boundary.md` §1）：In Scope 10 条
- 不做事项表（`markdown/01_scope_boundary.md` §2）：Out of Scope 12 条
- 候选池（`markdown/01_scope_boundary.md` §3）：8 条候选，标注推迟理由和目标版本
- 范围变更控制流程（`markdown/01_scope_boundary.md` §4）

**验证口径：**
- [x] In Scope: P0×3 + P1×3 + P2×4 = 10 条
- [x] Out of Scope: 模型×3 + 产品×3 + 架构×3 + 研究×3 = 12 条
- [x] 候选池 8 条，每条有推迟理由和目标版本
- [x] 范围蔓延唯一合法理由：发现新 P0 级声学合规缺陷

---

## T3 拆解 AEP-ACU-001~010

**状态：** ✅ 完成

**产物：**
- AEP 清单表（`markdown/02_aep_acu_list.md`）
- 10 张可独立执行的任务卡

**每张卡包含：**
- 任务定义 + 研发意义
- 输入（代码文件路径 + 外部参考）
- 输出（修改后的代码 + 实验报告 + 数据）
- 实验入口（逐步实验设计）
- 工程入口（具体文件 + 修改方案）
- 冻结标准（可量化验证的 checkbox 列表）

**优先级分布：**
| 优先级 | 数量 | 任务 |
|--------|------|------|
| P0 | 3 | ACU-001 (Schroeder), ACU-002 (RBJ EQ), ACU-003 (HPSS) |
| P1 | 3 | ACU-004 (7频段), ACU-005 (True Peak), ACU-006 (感知尺度) |
| P2 | 4 | ACU-007 (掩蔽), ACU-008 (F0), ACU-009 (Chroma), ACU-010 (MRS) |

**依赖关系：**
- P0 三项完全独立（不同文件，无代码冲突）
- P1 三项完全独立
- P2 中 ACU-007 依赖 ACU-006（Bark 尺度映射），其余独立

---

## T4 定义版本节奏

**状态：** ✅ 完成

**产物：**
- 节奏图（`assets/cadence_diagram.png`）：6 阶段 Gantt 图
- 阶段表（`markdown/04_release_cadence.md` §1）：每阶段有进入/退出条件
- 每日日程分解（`markdown/04_release_cadence.md` §3）

**6 阶段节奏：**
| 阶段 | 名称 | 耗时 | 退出条件 |
|------|------|------|----------|
| P0 | 章程签核 | 0.5 天 | GATE-09 签核通过 |
| P1 | P0 修复 | 2 天 | ACU-001/002/003 MUST 通过 |
| P2 | P1 补完 | 5 天 | ACU-004/005/006 MUST 通过 |
| P3 | 回归测试 | 1 天 | GATE-03~06 通过 |
| P4 | P2 判断 | 1 天 | 合入/推迟决定已记录 |
| P5 | 封口归档 | 1 天 | GATE-01~09 全部通过 |

**总预计耗时：约 10.5 天**

**里程碑：**
| 编号 | 日期 | 条件 |
|------|------|------|
| M1 | 2026-07-03 | Founder/CTO 签核 |
| M2 | 2026-07-05 | P0 修复验收通过 |
| M3 | 2026-07-12 | P1 补完验收通过 |
| M4 | 2026-07-13 | 回归测试通过 |
| M5 | 2026-07-14 | P2 合入/推迟决定 |
| M6 | 2026-07-15 | v0.4 封口 + git tag |

---

## T5 定义验收标准

**状态：** ✅ 完成

**产物：**
- 验收矩阵（`markdown/03_acceptance_matrix.md`）：17 个验收项 × 10 个 AEP
- 验收检查表（`docx/DOC-MFY-003_验收标准与检查表.docx`）：可逐项打勾

**验收等级：**
- MUST：27 项（不通过则 v0.4 不发布）
- SHOULD：16 项（需要合理理由才能跳过）
- MAY：0 项（条件允许则合入 —— P2 级任务自带此属性）

**全局验收门 9 项（GATE-01 ~ GATE-09）：**
1. 所有 MUST 验收项通过
2. 所有 SHOULD 验收项有明确状态
3. ruff lint 零错误
4. pytest -m v01 全通过
5. pytest 全量通过
6. MRS 回归: 20 首基线差值 < 2.0 分
7. A_compliance ≥ 85
8. 文档无 TODO/占位符
9. Founder/CTO 签核

---

## T6 定义样本与数据要求

**状态：** ✅ 完成

**产物：**
- 测试基线集规格（`markdown/03_acceptance_matrix.md` §测试音频基线集）

**规格：**
| 要求 | 规格 |
|------|------|
| 数量 | 20 首（固定，不可替换） |
| 来源 | AI 生成 ≥ 12 首 + 真实录音 ≥ 8 首 |
| 风格 | 6 种各 ≥ 2 首 |
| 格式 | WAV 44.1 kHz 16-bit stereo |
| 长度 | 30-180 秒 |
| 路径 | `tests/data/baseline/v04/` |
| 冻结 | M2 里程碑前 |

---

## T7 定义公式与指标

**状态：** ✅ 完成

**产物：**
- 公式表（`markdown/06_formula_system.md`）：2 个新公式 + 3 个继承公式的 v0.4 预期值

**新增 v0.4 专用公式：**

1. **C_v04（v0.4 完成度）= S_scope × A_AEP × Q_accept × F_freeze / R_drift**
   - 当前: 6.0/10, 目标: 9.8/10

2. **V_ACU（声学合规补完价值）= I_sound × R_risk × A_standard × E_evidence**
   - ACU-002 (RBJ EQ): 68/100 vs ACU-007 (掩蔽): 5/100 — 解释了 P0 vs P2 优先级差异

**继承公式 v0.4 预期：**
- A_compliance: 65 → 88
- P_align: 0 → 3.1（长期建设）
- C_loop: 6.0% → 14.4%

---

## T8 定义风险与阻断项

**状态：** ✅ 完成

**产物：**
- 风险登记表（`markdown/05_risk_register.md`）：10 项风险

**风险分布：**
| 等级 | 数量 | 风险值 |
|------|------|--------|
| 阻断 | 1 | R-006 (回归测试覆盖不足, P×I=15) |
| 高 | 5 | R-001/007/008/004/009 (P×I=10-12) |
| 中 | 4 | R-003/002/005/010 (P×I=6-9) |

**每项风险包含：** 描述、概率 (1-5)、影响 (1-5)、风险值 (P×I)、缓解措施、触发条件、应急预案

---

## T9 定义冻结规则

**状态：** ✅ 完成

**产物：**
- 冻结门禁（`markdown/04_release_cadence.md` §2）：5 个冻结门

| 门禁 | 触发时间 | 冻结内容 |
|------|----------|----------|
| F-INPUT | P1 开始前 | 范围边界 + AEP 任务 + 测试基线 |
| F-P0 | P1 完成时 | ACU-001/002/003 代码 + 证据 |
| F-P1 | P2 完成时 | ACU-004/005/006 代码 |
| F-MRS | P3 通过后 | 20 首基线 MRS + 管线快照 |
| F-RELEASE | P5 完成时 | v0.4 全部 + git tag |

---

## T10 定义 DeepSeek 执行方式

**状态：** ✅ 完成

**产物：**
- DeepSeek 执行提示词（`markdown/07_deepseek_execution_prompt.md`）

**核心要求：**
1. 每个输出落到变量、测量值、统计检验、验收证据或冻结判定
2. 不允许只写描述性段落
3. 不确定内容标记为 [理论假设] 或 [待实验验证]
4. 每 AEP 产出：实验设计 + 原始数据 + 统计分析 + 验收判定
5. 失败处理：产出失败转交单，不自行修改代码

**执行模板：** 实验设计 → 原始数据 → 统计分析 → 验收判定 → 结论

---

## T11 封口归档

**状态：** ⚠️ 部分完成

| 交付物 | 格式 | 状态 |
|--------|------|------|
| 00_project_charter.md | MD | ✅ |
| 01_scope_boundary.md | MD | ✅ |
| 02_aep_acu_list.md | MD | ✅ |
| 03_acceptance_matrix.md | MD | ✅ |
| 04_release_cadence.md | MD | ✅ |
| 05_risk_register.md | MD | ✅ |
| 06_formula_system.md | MD | ✅ |
| 07_deepseek_execution_prompt.md | MD | ✅ |
| DOC-MFY-003_任务文件.md | MD | ✅ 本文件 |
| DOC-MFY-003_项目章程_合订版 | DOCX + PDF | ✅ |
| DOC-MFY-003_需求说明书 | DOCX + PDF | ✅ |
| DOC-MFY-003_验收标准与检查表 | DOCX + PDF | ✅ |
| scope_diagram.png | PNG | ✅ |
| priority_matrix.png | PNG | ✅ |
| cadence_diagram.png | PNG | ✅ |
| company_logo.png | PNG | ⚠️ 占位符 — 需替换为官方 logo |
| reference_standards.md | MD | ✅ |
| metadata.json | JSON | ✅ |
| README.txt | TXT | ✅ |

**未完成项：**
1. `company_logo.png` 是占位符，需替换为公司官方 logo 文件
2. Founder/CTO 签核待完成（GATE-09）

---

## 下一步

签核通过后，启动 Phase 1：

```text
Phase 1 (P0 修复, Day 1-2):
  并行执行: AEP-ACU-001 / ACU-002 / ACU-003
  产出: experiments/ACU-NNN/ 下每项的执行证据
  封口: 3 个 P0 MUST 验收项全部通过

Phase 2 (P1 补完, Day 3-7):
  并行执行: AEP-ACU-004 / ACU-005 / ACU-006
  封口: 3 个 P1 MUST 验收项全部通过

Phase 3-5: 回归 → P2 判断 → 封口归档
```

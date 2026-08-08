# DOC-MFY-003｜Moodify Acoustic Compliance Upgrade v0.4 项目章程

> 文档编号：DOC-MFY-003
> 版本代号：v0.4 — Acoustic Compliance Upgrade (ACU)
> 生成日期：2026-07-02 15:37 (Asia/Singapore, UTC+8)
> 公司主体：荣景文川（深圳）科技有限公司
> 任务责任：Founder / CTO
> 执行对象：DeepSeek / AI Worker Layer
> 上游输入：DOC-MFY-002（声学理论合规审计与第二代研发路线图）
> 下游输出：EXP-MFY 声学实验任务、ENG-MFY 工程实现任务
> 任务类型：项目章程 / 研发管理资产

---

## 0. 项目定义

### 0.1 v0.4 是什么

v0.4 (Acoustic Compliance Upgrade) 是 Moodify 的**声学合规补完版本**。它的核心不是新增功能，而是修复 DOC-MFY-002 审计中发现的声学理论与实现缺口。

v0.4 的战略定位：

```text
v0.1.0 (当前)           v0.4 (本次)            v0.5+ (后续)
─────────────────────    ────────────────────    ──────────────────
声学合规度: 65/100  →    声学合规度: 88/100  →  感知对齐度: 17/100+
感知对齐度: 0/100        感知对齐度: 5/100       智能层扩展
审计闭环: 6.0%           审计闭环: 25%+          闭环效率: 60%+
```

### 0.2 成功判定

v0.4 的完成标准——以下条件**全部满足**才算交付：

1. P0 缺陷 DEF-001 (RBJ EQ) 和 DEF-002 (Schroeder Reverb) 修复并验收通过
2. AEP-ACU-001~010 中 P0 和 P1 任务的验收证据全部产出
3. 声学合规评分 A_compliance 从 65 → ≥ 85
4. 所有修复通过 ruff lint + pytest -m v01 + pytest 全量（MHP 完成标准四道门）
5. 回归测试：20 首基线音频的处理前后 MRS 差值变化 < 2.0 分
6. DOC-MFY-003 全部交付物归档完成

---

## 1. 上游审计发现映射

v0.4 的任务直接派生自 DOC-MFY-002 的 13 项缺陷登记。映射关系：

| DOC-MFY-002 缺陷 | v0.4 任务 | 优先级 | 说明 |
|------------------|-----------|--------|------|
| DEF-001 (FFT EQ → RBJ) | AEP-ACU-002 | P0 | RBJ biquad EQ 替换 |
| DEF-002 (Schroeder 缺全通) | AEP-ACU-001 | P0 | 全通滤波器 + 双声道混响 |
| DEF-006 (频段不一致) | AEP-ACU-004 | P1 | 7 频段统一 + 5-8 kHz 区间 |
| DEF-001/NEW-04 (真峰值) | AEP-ACU-005 | P1 | True Peak Limiter |
| DEF-005 (mel/bark/chroma/F0) | AEP-ACU-006 | P1 | Mel/Bark/ERB 感知尺度 |
| DEF-005 (F0) | AEP-ACU-008 | P2 | F0/Pitch Stability |
| DEF-005 (chroma) | AEP-ACU-009 | P2 | Chroma/Key/Harmony |
| DEF-004 (掩蔽模型) | AEP-ACU-007 | P2 | 心理声学掩蔽初版 |
| 新增 (HPSS 残差) | AEP-ACU-003 | P0 | HPSS 残差分量守恒审计 |
| 新增 (MRS 鲁棒化) | AEP-ACU-010 | P2 | MRS 参考集鲁棒化 |

> AEP-ACU-003 和 AEP-ACU-010 是 DOC-MFY-002 未显式登记但在 v0.4 章程中新增的研发条目。两者的理论依据见对应任务卡。

---

## 2. 交付物清单

| 编号 | 交付物 | 格式 | 状态 |
|------|--------|------|------|
| D01 | DOC-MFY-003 项目章程正文 | MD | 本文件 |
| D02 | 范围边界与不做事项 | MD | 01_scope_boundary.md |
| D03 | AEP-ACU-001~010 任务卡清单 | MD | 02_aep_acu_list.md |
| D04 | 验收矩阵 | MD | 03_acceptance_matrix.md |
| D05 | 研发节奏与冻结规则 | MD | 04_release_cadence.md |
| D06 | 风险登记表 | MD | 05_risk_register.md |
| D07 | 公式与指标体系 | MD | 06_formula_system.md |
| D08 | DeepSeek 执行提示词 | MD | 07_deepseek_execution_prompt.md |
| D09 | 项目章程合订版 | DOCX + PDF | 待生成 |
| D10 | 需求说明书 | DOCX + PDF | 待生成 |
| D11 | 验收标准与检查表 | DOCX + PDF | 待生成 |
| D12 | 元数据文件 | JSON | metadata.json |
| D13 | 项目说明 | TXT | README.txt |
| D14 | 图表资产 | PNG/SVG | assets/ |
| D15 | 参考标准 | PDF/摘录 | references/ |

---

## 3. 团队与角色

| 角色 | 负责人 | 职责 |
|------|--------|------|
| Founder / CTO | — | 最终签核、优先级确认、IP 策略决策 |
| Claude A (交接官) | huliye24 | 任务分发、跨文档一致性、封口验收 |
| Claude C (审计官) | — | 代码审查、合规验证、bug 检测（只查不修） |
| DeepSeek (AI Worker) | — | AEP 任务执行、实验设计、报告生成 |
| Codex (实现) | — | ENG-MFY 工程实现 |

---

## 4. 关键日期

| 里程碑 | 日期 | 条件 |
|--------|------|------|
| M1 — 项目章程签核 | 2026-07-03 | Founder/CTO 批准 DOC-MFY-003 |
| M2 — P0 修复完成 | 2026-07-05 | AEP-ACU-001/002/003 验收通过 |
| M3 — P1 补完完成 | 2026-07-12 | AEP-ACU-004/005/006 验收通过 |
| M4 — 回归测试通过 | 2026-07-13 | 全量 pytest + MRS 回归 |
| M5 — P2 合并判断 | 2026-07-14 | 决定 P2 任务是并入 v0.4 还是推迟到 v0.5 |
| M6 — v0.4 封口 | 2026-07-15 | 全部交付物归档 + 文档冻结 |

> 日期为乐观估计。如遇阻断项（见 05_risk_register.md），M2-M6 顺延。

---

## 5. 版本命名与编号规则

```text
v0.4 = Moodify 0.x 系列的第四个次要版本
ACU = Acoustic Compliance Upgrade

内部任务编号: AEP-ACU-NNN (NNN = 001~010)
下游实验编号: EXP-MFY-NNN (继承 DOC-MFY-002)
下游工程编号: ENG-MFY-NNN (继承 DOC-MFY-002)
```

---

## 验收检查

- [x] doc_id、版本代号、日期、责任人、输入来源完整
- [x] 上游审计发现映射表（10 行，每行对应 DOC-MFY-002 缺陷或标注新增）
- [x] 成功判定 6 条全部可量化
- [x] 交付物清单 15 项
- [x] 角色定义 5 个
- [x] 里程碑 6 个含日期和条件

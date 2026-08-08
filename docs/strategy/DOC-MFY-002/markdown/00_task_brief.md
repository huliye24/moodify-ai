# DOC-MFY-002｜任务简介与元数据

> 文档编号：DOC-MFY-002
> 生成日期：2026-07-02 15:25 (Asia/Singapore, UTC+8)
> 公司主体：荣景文川（深圳）科技有限公司
> 任务责任：Founder / CTO
> 执行对象：DeepSeek / AI Worker Layer
> 任务类型：技术审计 / 声学合规层 / 第二代研发路线图
> 上游输入：DOC-MFY-001（Moodify 声学实验生命体报告）、moodify-core-package 源代码审计、moodify_runtime 源代码审计
> 输出清单：10 份 Markdown 章节 + DOCX/PDF 交付物 + 图表资产 + 参考文献

---

## 输入来源

| 来源 | 类型 | 关键内容 |
|------|------|----------|
| DOC-MFY-001 §1-7 | 战略文档 | 16 命题 (P01-P16)、4 假设 (H1-H4)、7 公式体系、22 参考文献、知识四层分类 |
| moodify-core-package/src/moodify/ | Python 源码 | 处理算子 (operators.py)、诊断引擎 (engine.py)、守恒审计 (conservation.py)、MRS (reality_metrics.py)、工艺链 (craft_chains.py)、物理实验 (physics/) |
| moodify_runtime/ | Python 源码 | 声学 CT (acoustic_ct.py)、工艺处理 (craft_processes.py)、在线校准 (calibration/)、PDF 报告 (pdf_report.py) |
| workers/ | Python 源码 | MRS 指标 (mrs_metrics.py)、MRS 公式 v0.2 (mrs_formula_v02.py)、MRS 基准 v0.3 (mrs_open_benchmark_v03.py) |
| docs/ 目录审计 | 文档 | 25+ MHP 审计报告、集成审计 (INTEGRATION_AUDIT.md)、MRS 校准指南、频段定义文档 |

---

## 审计方法论

本次审计采用"代码→理论→标准"三层对照法：

1. **代码层**：逐文件审查 moodify-core-package 和 moodify_runtime 中的声学处理实现
2. **理论层**：对照 DOC-MFY-001 的公式系统、假设体系、参考文献要求
3. **标准层**：对照 ITU-R BS.1770、EBU Tech 3342、ITU-R BS.1387 (PEAQ)、RBJ EQ Cookbook、Schroeder 1962、Zwicker & Fastl 2007 等行业标准

每个发现均标注：审计来源（文件路径:行号）、科学依据（参考文献编号）、风险等级（P0/P1/P2）、可执行任务编号（EXP-MFY-XXX / ENG-MFY-XXX）。

---

## 输出文件清单

| 文件 | 内容 | 字数估计 |
|------|------|----------|
| 00_task_brief.md | 任务简介与元数据（本文件） | ~500 |
| 01_audit_strengths.md | 声学合规优点表 | ~2000 |
| 02_defect_register.md | 缺陷登记表（科研式模板） | ~8000 |
| 03_priority_matrix.md | P0/P1/P2 优先级矩阵 | ~3000 |
| 04_acoustic_layers.md | 三层研发模型（合规/感知/智能） | ~4000 |
| 05_aep_exp_eng_map.md | AEP/EXP/ENG 任务入口映射 | ~5000 |
| 06_ip_trade_secret_layout.md | 专利候选与商业秘密清单 | ~3000 |
| 07_model_gpu_hardware_path.md | 模型/GPU/硬件路线图 | ~3000 |
| 08_formula_metrics.md | 公式与指标体系 | ~3000 |
| 09_reference_notes.md | 参考标准与文献 | ~2000 |
| 10_acceptance_checklist.md | 封口验收表 | ~1500 |

---

## 第二代研发主公式（本任务定义）

```text
A_compliance = L_loudness × E_EQ × R_reverb × H_HPSS × P_peak × C_conservation
P_align = M_mel × B_bark × E_ERB × K_masking × F_F0 × C_chroma
V_roadmap = S_severity × A_actionability × E_evidence × I_IP / C_complexity
C_loop = D_diagnosis × P_processing × A_audit × R_report × F_feedback
```

变量释义见 `08_formula_metrics.md`。

---

## 验收检查

- [x] doc_id、日期、责任人、输入来源、输出清单完整
- [x] 目录结构已创建（markdown/ docx/ pdf/ assets/ references/）
- [x] 审计方法论明确定义（代码→理论→标准 三层对照）
- [x] 第二代研发主公式已写入

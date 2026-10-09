# ThinkPad 002 — Case/Project Layout Compatibility Audit

**Task:** MOODIFY THINKPAD HEAVY LANE 002 (Phase A, §5A)
**Date:** 2026-10-05
**Branch:** `feat/thinkpad-case-compat-002`
**Method:** 只读盘点；每个结论都带可复查的仓库/磁盘证据。未记录的语义不推测。

---

## 1. 已知布局总表

| # | 布局 | 识别标志（磁盘证据） | 生产者（代码证据） | 状态 |
|---|---|---|---|---|
| L1 | **Song Project**（`moodify.project/0.1`） | `project.json` | `moodify/project/service.py::create_project` | canonical，本次作为一等识别对象 |
| L2 | **Core 听觉 case 包** | `case.json`（+`report.json`/`scan/`） | `moodify/release.py::analyze_to_case`（`moodify demo` / 0.2 analyze 作业同路径） | canonical 产物，无 manifest 声明 |
| L3 | **Studio case** = L2 + studio 子树 | L2 标志 **且** `studio/` 目录 | `moodify-desktop/src/{main.js,studio.js,pipeline.js}`（Core case 之上挂 studio/ 子树） | canonical 产物，schema 字符串自带版本 |
| L4 | **Legacy WSE 案卷** | `00_source/` 编号目录 | 历史 WSE 工作流（仓库样本 `examples/golden_case/`） | legacy，只读识别 |
| — | 非案卷输出目录 | 无上述标志（如 `moodify-core-package/era_cli_out/`、`golden_run_out/`） | — | **UNSUPPORTED**（不猜测） |

**识别优先级**（写死在 reader 中）：L1 → （L2 标志 + `studio/`）= L3 → L2 → L4 → UNSUPPORTED。

## 2. L1 — Song Project（既有实现，非本次新增）

**权威文件**: `project.json`（`moodify.project/0.1`，frozen CanonicalModel，extra=forbid）。
**权威事实**: `project_id`、`source` 资产（`logical_path` 恒为 `source/original.<ext>`、`content_hash`、`size_bytes`、`original_name`、`media_type`）、十一个预留 section（0.1 全部为空 `{}`）。
**完整性**: `load_project` 对源文件重验 size+sha256；不匹配 → `ProjectIntegrityError`（响亮失败，不重哈希）。
**可安全归一化**: 全部（模型即目标词汇）。
**必须保持 UNKNOWN**: 预留 section 的内容语义（0.1 无 schema）。

## 3. L2 — Core 听觉 case 包（实测样本：`local_audio_assets/outputs/analyze_A/case_825c5e20…`）

```text
<case>/
  case.json              权威个案记录（ProductionCase）
  report.json            0.2 报告（moodify.msp_report/0.2）——测量/judgment_boundary/plan 的权威
  report.md / report.html 派生渲染（optional；缺失正常）
  measurements.json      MeasurementRecord 列表（52 条实测）
  evidence.json          EvidenceArtifact 列表（4 条实测）
  judgment_rules.json    阈值来源/版本快照
  auditory_report.json   旧层报告（report_id/overall_status/sections/evidence_index）
  scan/
    scan_manifest.json   **artifact 哈希权威**（input_path/input_sha256/artifacts{name:{path,sha256,size_bytes}}）
    metrics.json / timeline_metrics.jsonl / analysis_data.npz / spectrum_{linear,log}.png
```

**权威事实**：
- `case.json`: `case_id`、`source_id`（`sha256:<64hex>`）、`lifecycle_state`（`ACTIVE`→`COMPLETED`）、`authority_state`（本样本 `HUMAN_REQUIRED`）、`created_at`、`measurement_ids/evidence_ids/rule_ids`、`schema_version`（canonical contract，`1.0`）。
- `report.json`: `case.case_id`、`source.{name,sha256,duration_s,channels,sample_rate}`、`findings[]`、`plan`（恒 `DRAFT_PLAN_NOT_EXECUTED`）、`judgment_boundary`、`provenance`。
- `scan/scan_manifest.json`: `input_sha256`（源音频哈希）、`artifacts.*.sha256`（每个扫描产物的哈希）。

**重复事实（同值多处）**: 源哈希同时出现在 `case.json.source_id`、`report.json.source.sha256`、`scan_manifest.input_sha256`、`auditory_report.json.source_sha256`（实测四处同值 `sha256:8ac3577c…`）。**不挑“最权威的一份”合并——全部保留引用，完整性取可验证处**。
**陈旧/UI-only**: `report.md/html`（可重渲染）、`generated_at`（时间戳，不是事实）。
**源文件位置**: **不在 case 内**。`case.json.source_id` 只有哈希；路径仅当 Studio 写了 `source_path.json` 时存在（L3）。
**缺失含义**: 有 `case.json` 无 `report.json` = 分析未完成（`lifecycle_state` 佐证）→ **INCOMPLETE**，不是“空结果”。
**可安全归一化**: case_id、源哈希（记录值）、scan 产物引用+哈希、report 存在性。
**必须保持 UNKNOWN**: 源文件本体（无路径时不可读、不可验证——`verified=null`）、音频听感、findings 的音乐含义。

## 4. L3 — Studio case（= L2 + `studio/` 子树；实测结构证据来自 `studio.js`/`pipeline.js`/`main.js`）

```text
<case>/source_path.json            桌面壳写入的源路径指针（外部绝对路径；可缺失/可失效）
<case>/stems/*.wav + manifest.json 快速分离（引擎 dsp_center_hpss，grade 预览级写在 manifest.engine_note）
<case>/midi/*.mid[,*.csv]          basic-pitch ONNX 转录
<case>/score/*.musicxml            music21 派生解读（不顶替 MIDI）
<case>/finishing/*                 预设 Mix Graph 产物（graph.json + *_mixgraph_*.wav + *.evidence.json）
<case>/compare/ab_comparison.json  已准备的 A/B 对（测量事实）
<case>/compare/ab_choices.jsonl    人类 keep-A/B 决策账本（append-only）
<case>/studio/
  meta.json        moodify.studio.meta/0.1（case_dir【绝对路径，信息性】、updated_at）
  diagnosis.json   moodify.studio.diagnosis/0.1（严格投影自 report.json；含 preserve/human_notes 人类字段）
  context.json     moodify.studio.context/0.1（只引用存在的路径）
  plans/*.json     moodify.studio.plan/0.1（恒 DRAFT_PLAN_NOT_EXECUTED）
  finish_mode.json moodify.studio.finish-mode/0.1（人类显式选择 QUICK_STEREO_ONLY 的痕迹）
  pipeline.json    moodify.studio.pipeline/0.1 —— **记录，不是权威**（stage 每次由磁盘产物重新推导）
  selection.json   moodify.studio.selection/0.1（人类选定版本）
  versions/ai_*/   {job.json, out/*.wav, evidence.json}（每次尝试一个不可覆盖目录）
  verification/*.json, export/*.json
```

**权威事实**: 人类决策三件（selection / finish_mode / ab_choices）、版本目录的存在与内容、各 JSON 的 schema 字符串与 case_id 绑定。
**UI-only / 派生（不得当权威读）**: `pipeline.json:stage`（推导记录）、`studio/meta.json:case_dir`（本机绝对路径）、`report.md/html`。
**陈旧风险**: `source_path.json` 指向的路径可被移动/删除（桌面代码 `source:resolve` 就是 null 语义）。
**重复事实**: `stems/manifest.json.source_sha256` 与 `report.json.source.sha256` 应同值；`versions/*/evidence.json` 里的 `target` 与目录名无关（按 evidence 读，不按名字猜——代码如此）。
**可安全归一化**: 三大人类决策、版本清单、产物引用、schema 版本。
**必须保持 UNKNOWN**: `job.json` 的未记录字段语义、未来 section 的内容 schema、听感判断。

## 5. L4 — Legacy WSE 案卷（仓库样本：`examples/golden_case/`，49 文件）

```text
production_case.json                                 ProductionCase 记录（与 L2 case.json 同合同）：
                                                     case_id=case_0000…01 / source_id / lifecycle=COMPLETED / authority=ALGORITHM
case_manifest.json                                   MFY-DATA-PROTOCOL-001 清单：source_path(相对) /
                                                     source_sha256 / candidate_sha256{A,B,C} / versions{scan_profile,plan_gen,…}
README.md / reopen_golden.py                         案卷文档；重开+校验工具（data_factory.dataset_builder）
00_source/source.wav                                 被处理源（**在案卷内**）
01_source_scan/{scan_manifest.json, metrics.json, timeline_metrics.jsonl, analysis_data.npz}
                                                     （*scan_manifest 记录 5 个 artifact 含 spectrum_{linear,log}，磁盘缺失——见下*）
02_plans/plan_{A,B,C}.json                           plan_id/params/rationale/source_sha256
03_candidates/candidate_{A,B,C}.{json,wav}           candidate_sha256/parent_source_sha256/processing_*
04_after_scan/{A,B,C}/…                              候选项复扫（同 01 结构）
05_comparison/source_vs_{A,B,C}/                     每个 5 文件：auditory_report / comparison_manifest /
                                                     comparison_report / judgment_rules / metrics_delta
06_human_review/{review.json, algorithmic_scores.json}
07_learning/{pairwise_preferences.jsonl, training_record.json}
```

**实测哈希验证（2026-10-05）**:
- `00_source/source.wav` == `production_case.json:source_id` == `case_manifest.json:source_sha256` == `scan_manifest:input_sha256` == `e8e61fea…` —— **四处一致 + 实际文件 MATCH**；
- 三个候选 WAV 对 `candidate_sha256`（record 文件与 manifest map 双向一致）—— **全部 MATCH**。

**陈旧/缺失证据（重要，reader 实测行为）**:
- `scan_manifest.input_path` 指向另一台机器/旧路径 `E:\moodify\…\00_source\source.wav` —— **input_path 不可信，摘要可信**；reader 以“哈希对案卷内实际文件”验证，不按 input_path 寻找。
- **8 个 spectrum PNG 记录在案但磁盘缺失**（01 的 linear/log + 04 的 A/B/C 各 2 个；历史 `.gitignore` 吞掉所致）。reader 如实报 `ARTIFACT_MISSING` ×8 → `INCOMPLETE` —— 这是“missing ≠ success”的实机演示，不是误报。

**可安全归一化**: case_id、编号目录的角色（结构性事实）、源/候选哈希（已挂到 artifact 引用上）、计划/复审/学习的**存在性与文件引用**、README/reopen 工具的引用。
**必须保持 UNKNOWN**: 02–07 各 JSON 的完整语义（`params` 具体含义、`judgment_decision` 的裁决语义、learning 记录的用途）——只记录 observed role，不解释。

## 6. 支持边界（本任务交付的 reader 遵守）

```text
识别:     L1 / L2 / L3 / L4（按 §1 优先级；L4 也可被显式指定——命令行直接指向 00_source 的父目录）
不识别:   非案卷输出目录、未知布局 → UNSUPPORTED + 原因（绝不猜测升级）
读操作:   纯读取；同一案卷读两次磁盘零字节变化（测试断言整个目录树哈希不变）
哈希:     源（L1: 对副本; L2/L3: 对 source_path 指向的实际文件 vs case 记录; L4: 00_source vs
          多份记录——production_case / case_manifest / scan 先互相冲突检查，再对实际文件）
          与 scan_manifest.artifacts、候选 WAV（存在则验证）；记录哈希而不复制文件
缺失:     「记录里有的文件不在」= 问题 + INCOMPLETE；「记录里没有的东西缺失」= 正常
篡改:     哈希不匹配 = 问题 + CORRUPT（响亮，不修复、不重哈希）
未知:     未识别的 schema 字符串 → unknowns 记录 + 不解释其内容（不静默接受）
状态:     RECOGNIZED / INCOMPLETE / CORRUPT / UNSUPPORTED（§5E 词汇）
```

**明确不做（本任务非目标）**: 迁移、复制音频、自动修复、stage 推导（Production Graph 属后续任务）、把 Studio 的 stage 判定搬进 Core（那是 REALIGNMENT §16 Phase 3）。

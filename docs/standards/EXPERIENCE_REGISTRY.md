# Moodify 工程经验注册表（Experience Registry）

**Created:** 2026-08-02  
**任务来源：** DSK-MFY-KNOWLEDGE-LAYERS-022  
**Purpose:** 记录"哪次失败教会我"——每条经验有失败事实、根因、边界与可核对的防复发机制。  
**维护规则：** 新条目必须来自真实失败（FAILURE_LEDGER/交接单/审计）；已生效条目不可删除或改写，修正以新版本标注 superseded（失忆防护，PR-007）。

---

## EX-001 派生汇总与原始记录不一致（Treatment Summary Staleness）

**来源：** `docs/standards/FAILURE_LEDGER.md` FL-001  
**失败事实：** `summary.json` 声称 30 records / 6 completed；源目录实际 27 / 3。三个记录改名为 `.bak` 后未重生成汇总。  
**根因：** 派生数据在源变化后未重算；聚合器重跑是手动步骤。  
**边界：** 任何记录增删改名后，汇总必须重生成；`.bak` 排除必须有显式记录。  
**防复发机制：** 聚合器重跑确定性输出 + `scan_absent_records()` + 备份-再覆盖策略（`scripts/v01_aggregate_treatment_records.py`）。  
**关联模块：** treatment_records、v01 聚合  
**关联原理：** PR-001, PR-007, PR-009

## EX-002 MRS 不能作为质量发布唯一权威

**来源：** `docs/standards/FAILURE_LEDGER.md` FL-004；`MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §4.6  
**失败事实：** MRS gate 准确率 9.1%、伪 MRS 偏好相关 ~0.19、MRS Open 一致 ~60.6%；历史上无代码级门禁阻止 MRS 被视为发布权威。  
**根因：** 指标与人类工程判断未校准；单一指标被赋予超出其证据能力的权力。  
**边界：** 无人工批准时 MRS 分数不得单独放行。  
**防复发机制：** `mrs_can_release(mrs_score, human_approved)` 强制人工批准（`moodify_runtime/hardening_gates.py`）+ `MRS_AUTHORITY_STATEMENT`。  
**关联模块：** hardening_gates、MRS 门禁  
**关联原理：** PR-002, PR-010

## EX-003 MuseScore 4.5.1 一次仅接受一个 -o 且不支持 -I 参数

**来源：** `DSK-MFY-SCORE-ENGINE-009/FAILURE_LEDGER.md` #3  
**失败事实：** 009 后端初版用多 `-o` + `-I musicxml` 调用 MuseScore，exit code != 0 导出失败。  
**根因：** 对 MuseScore 4.5.1 CLI 的实际参数约束（一次一个 `-o`、无 `-I`）未探测即假设通用。  
**边界：** MuseScore 4.x 各小版本 CLI 参数可能不同；探测必须针对实际安装版本。  
**防复发机制：** 009 backend 分两次 argv 调用 + `test_export_with_real_musescore`（`moodify-core-package/tests/score_engine/test_musescore_backend.py`）。  
**关联模块：** score_engine/musescore_backend  
**关联原理：** PR-005, PR-006

## EX-004 多页 SVG 自动带页码后缀，目标路径收集失败

**来源：** `DSK-MFY-SCORE-ENGINE-009/FAILURE_LEDGER.md` #4  
**失败事实：** 导出 SVG 时目标 `score.svg` 不存在，实际生成 `score-1.svg`（多页页码后缀），产物收集为空。  
**根因：** 假设输出文件名与请求路径一致；未验证真实产物命名。  
**边界：** 多页 SVG 的页码后缀随渲染内容变化。  
**防复发机制：** glob `stem-*.svg` 收集 + `test_export_with_real_musescore` 断言 SVG 存在。  
**关联模块：** score_engine/musescore_backend  
**关联原理：** PR-005, PR-007

## EX-005 round-trip 必须重解析并报告差异，禁止"成功导出"掩盖

**来源：** `DSK-MFY-SCORE-ENGINE-009/FAILURE_LEDGER.md` #9；ROUNDTRIP_LOSS_CONTRACT  
**失败事实：** 初版 `_compare` 把"守恒"也误报为 WARNING，且导出成功与语义保存被混为一谈。  
**根因：** 验证逻辑把状态类别混用；"导出成功"不等于"语义无损"。  
**边界：** round-trip 关键字段（part/measure/note/pitch/duration/tempo）损失必须 FAIL。  
**防复发机制：** `roundtrip_report.json` verdict 门禁（PASS/WARNINGS/FAIL）+ `_compare` 分类修正 + 测试（`tests/score_engine/test_musescore_backend.py::TestExportBehavior`）。  
**关联模块：** score_engine/roundtrip  
**关联原理：** PR-002, PR-005, PR-007

## EX-006 派生数据在源变化后未重算（规则与聚合器生命周期）

**来源：** `docs/standards/FAILURE_LEDGER.md` FL-001 的同类模式；`MOODIFY_ENGINEERING_THICKNESS_STANDARD.md` §4.4  
**失败事实：** 汇总数据脱离原始记录成为事实源（与 EX-001 同源模式）。  
**根因：** 缺少"源 → 派生"的依赖追踪。  
**边界：** 任何自动聚合/派生结果不得独立于源成为权威。  
**防复发机制：** 聚合器确定性输出 + 源扫描校验（`scripts/v01_aggregate_treatment_records.py`）；标准 §4.4 明确禁止。  
**关联模块：** treatment_records、v01 聚合  
**关联原理：** PR-001, PR-007

## EX-007 Windows 平台 `open()` 默认 GBK 编码破坏 UTF-8 文件

**来源：** `docs/standards/FAILURE_LEDGER.md` FL-002  
**失败事实：** 三个治疗记录 JSON 未显式指定 UTF-8 读取时 `UnicodeDecodeError`。  
**根因：** Windows 系统默认编码为 GBK，`open()` 不传 `encoding="utf-8"` 即按 GBK 解析。  
**边界：** 所有涉及 UTF-8 文件的 I/O 必须显式指定编码。  
**防复发机制：** 生产模块全部显式 `encoding="utf-8"` + `test_malformed_json_does_not_crash`。  
**关联模块：** moodify_runtime、v01 聚合  
**关联原理：** —

## EX-008 写入/放行逻辑与生产路径脱节（谓词存在但无人调用）

**来源：** `docs/standards/FAILURE_LEDGER.md` §Independent Audit Correction（FL-003/FL-004 状态修正）  
**失败事实：** `can_write_back()` 与 `mrs_can_release()` 谓词有单元测试，但真实 Craft Library 写路径与交付边界未调用——谓词是"遏制研究"不是"生产强制"。  
**根因：** 门禁函数被当作安全网而非生产路径的组成部分。  
**边界：** 单元测试通过 ≠ 生产强制生效；必须验证调用链。  
**防复发机制：** 审计把 FL-003/FL-004 状态从 RESOLVED 修正为 OPEN（`docs/standards/FAILURE_LEDGER.md` §Independent Audit Correction）；后续任务必须接入真实调用链。  
**关联模块：** craft_evidence、hardening_gates  
**关联原理：** PR-009, PR-010, PR-007

## EX-009 对 CLI 参数的假设必须实测，不能从文档/惯例推断

**来源：** `DSK-MFY-SCORE-ENGINE-009/FAILURE_LEDGER.md` #3/#4 的共同模式  
**失败事实：** 009 假设 MuseScore 通用 CLI 行为，实际版本行为不同，导致两次导出失败。  
**根因：** 工具版本行为差异未在探测阶段捕获。  
**边界：** 任何外部工具集成前必须对实际安装版本做最小调用探测。  
**防复发机制：** capability_registry（017）的 known_failure_modes + 探测要求；009 `_probe_version`。  
**关联模块：** 全部外部工具集成  
**关联原理：** PR-005, PR-006

## EX-010 008 转录能力的已知边界：无 Demucs、无 ground truth、鼓轨不支持

**来源：** `DSK-MFY-STEM-MIDI-008/HANDOFF.md`（Remaining Limitations）  
**失败事实：** 008 交付时 Demucs 未安装（分离不可用）、无真实歌曲 ground truth、鼓转录 UNSUPPORTED、无 GPU。  
**根因：** 硬件约束与数据缺失；准确率声明被禁止（BENCHMARK_LIMITS）。  
**边界：** 任何"转录准确率"主张必须有独立 benchmark 任务证据；鼓轨不得用 Basic Pitch 音高冒充。  
**防复发机制：** HANDOFF 明示 BENCHMARK_LIMITS；能力矩阵登记 UNSUPPORTED（`docs/tasks/deepseek/DSK-MFY-STEM-MIDI-008/`）。  
**关联模块：** transcription_pipeline  
**关联原理：** PR-002, PR-006

## EX-011 环境事实（2026-08-02）：本机已安装工具清单

**来源：** `DSK-MFY-CAPABILITY-ACCRETION-017/00_SERIES_ORCHESTRATION.md` §2（实测）  
**失败事实：** 无失败——是已确认的边界事实：MuseScore 4.5.1 / FFmpeg 8.1.1 / SoX 14.4.2 / RubberBand 4.0.0 / Audacity 已装；Demucs 未装。  
**根因：** —  
**边界：** 环境变化（工具升级/卸载）后本记录可能过期，需重新探测。  
**防复发机制：** capability_registry 探测 + 环境记录维护（017）；探测只读不安装。  
**关联模块：** capability_registry（017 起）  
**关联原理：** PR-005

## EX-012 验证规则必须携带历史来源，无来源规则标记 unproven

**来源：** 系列编排 DSK-MFY-CAPABILITY-ACCRETION-017 §3.5 + 020 编排  
**失败事实：** 无失败——是预防性设计（防止验证规则变成无来历的仪式）。  
**根因：** —  
**边界：** 规则库扩充必须来自真实失败，禁止凑数量造规则。  
**防复发机制：** 020 的 `ValidationRule.historical_source` 字段 + 验收矩阵 Q1-04。  
**关联模块：** capability_registry/validation（020 起）  
**关联原理：** PR-007, PR-008

---

## 注册摘要

| ID | 一句话 | 状态 |
|---|---|---|
| EX-001 | 派生汇总与源不一致（summary 30 vs 27） | 已防复发 |
| EX-002 | MRS 不是发布唯一权威 | 已防复发 |
| EX-003 | MuseScore 单 -o、无 -I 参数 | 已防复发 |
| EX-004 | 多页 SVG 页码后缀 | 已防复发 |
| EX-005 | round-trip 差异必须可见 | 已防复发 |
| EX-006 | 派生数据不得独立成为权威 | 已防复发 |
| EX-007 | Windows GBK 破坏 UTF-8 | 已防复发 |
| EX-008 | 门禁谓词与生产路径脱节 | OPEN（待接入调用链） |
| EX-009 | CLI 参数假设必须实测 | 已防复发（017） |
| EX-010 | 008 转录能力边界 | 边界登记 |
| EX-011 | 本机工具环境事实 | 边界登记 |
| EX-012 | 验证规则必须带历史来源 | 预防性设计 |

# Moodify 项目审计｜2026-08

状态：2026-07-31 完成第一轮代码级审计。本文是 v0.4 调整的事实基线；结论来自读取实现、配置、测试和入口，不以目录名推断能力。

## 1. 审计范围与方法

检查了根 README、路线图与战略文档；`moodify-core-package/src/moodify`、`moodify_runtime`、`moodify-bridge` 的入口和关键实现；pytest 文件；配置；Treatment Records；历史实验、数据与输出目录；Git 状态与大文件政策。审计时工作树已有大量用户修改和未跟踪资产，本轮不覆盖、不移动、不删除它们。

代码规模快照：核心包 103 个 Python 文件、约 737 个函数和 152 个类；Runtime 150 个 Python 文件、约 1,692 个函数和 357 个类；测试目录包含 37 个核心测试文件（约 406 个测试函数）和 75 个 Runtime 测试文件（约 933 个测试函数）。`operator_api.py` 与核心 API 合计可见 71 个路由装饰器；三套 CLI 中可见约 105 个命令/解析器注册点。这些是静态计数，不等同于全部生产可用。

## 2. 当前项目真实能力

| 能力 | 实现证据 | 状态 | 边界 |
|---|---|---|---|
| 音频载入与基础分析 | `audio_io.py`、`v01_analyzer.py`、`reality_metrics.py` | Partially implemented | 指标定义分散；部分扫描值是代理量 |
| 预设 DSP 处理与 WAV 输出 | `v01_pipeline.py`、`processing/`、`v01_exporter.py` | Partially implemented | 有可运行链路；发行级质量尚未经正式对照实验验证 |
| Before/After 与质量门 | `v01_pipeline.py`、Runtime 报告与 gate 模块 | Partially implemented | 多套 gate/MRS 定义并存，缺统一证据契约 |
| Runtime、队列、失败与报告 | `moodify_runtime/runner.py`、`supervisor.py`、`report.py` | Partially implemented | 功能面广，状态与版本叙述需重新核验 |
| Operator API/内部控制台 | `operator_api.py`、`operator_console.py/html` | Partially implemented | 属内部操作面；不是创作者产品 |
| Workspace、版本与人工审批 | 核心 `services/`、`storage/workspace_store.py` 及测试 | Partially implemented | 与新 Production Case ledger 尚未统一 |
| 工艺/学习记录 | Treatment Records、`craft_*`、`learning_store.py` | Experimental | 不能称自动学习；存在多套状态机与存储模型 |
| 不可变案例与证据账本 | `moodify-bridge` Pydantic、DuckDB、Parquet、YAML、CLI | Partially implemented | 合成案例验证通过；尚未接入真实主处理入口 |
| WSE 指标适配 | `moodify-bridge/metrics.py` | Partially implemented | 覆盖基础 level/spectral/band/comparison/stereo；LRA/true peak 明确为 null |
| MSE 结构理解 | 资产与 SymbolicAnchor schema；仓库零散节拍/特征代码 | Planned / Experimental | 尚无统一 BPM、key、section、lyrics、MIDI 生产管线 |
| 候选搜索 | legacy optimizer、Runtime candidate/compare 相关对象 | Experimental | 不能视为统一可复现 Candidate Registry |

## 3. 当前模块结构

- `moodify-core-package`：安装包 `moodify` 2.0.0；包含 v01 主链、旧诊断/编排、DSP、优化、Workspace 服务、API。
- `moodify_runtime`：仓库根级 Python 包；承担作业、队列、报告、控制台、Craft、调度、学习面和大量运行测试。
- `moodify-bridge`：独立 Python 3.12 项目；承担不可变 Production Case、测量、证据、规则审批、回归和报告。
- `configs/`：MRS、preset、night job 和服务器限制等配置，尚无单一配置版本清单。
- `docs/experiments/`、`experiments/`、`science/`：研究与实验资产丰富，但命名、状态和生产引用关系不统一。
- `data/`、`cloud_data/`、`local_audio_assets/`、`outputs/`、`reports/`：本地/生成资产并存；必须继续排除私有和大音频。

## 4. 已完成的工作

1. 存在可调用的音频分析、预设处理、导出和报告链。
2. 存在 Runtime、作业、API、内部控制台与大量自动化测试资产。
3. 存在 Workspace 版本、比较、Judge、归档和人工审批相关实现。
4. 已开始积累 Treatment Records、Craft 与校准证据。
5. 已建立 `moodify-bridge` 的严格 Pydantic v1 schema、DuckDB 迁移、Parquet 指标存储、YAML 规则/假设、人批晋级和 Golden Case 回归。
6. 已明确重音量偏差、真实样本不足和不能从小样本宣布总体优势。

## 5. 未完成的工作

- 主处理链尚未自动生成统一 Production Case。
- WSE 指标没有单一命名、单位、算法版本和置信度登记表。
- MSE 尚未形成统一结构记录与可重复 CLI。
- Candidate、Evaluation、Decision、Theory Note、Rule Change 尚未在同一 ledger 中贯通。
- 规则注册与现有 Craft/MRS 状态机未统一；旧逻辑可能允许“稳定/采用”语义与新人工审批规则冲突。
- API/CLI/Runtime/bridge 三种入口缺少统一 pipeline version 和 case ID。
- Golden Set 仍小，未建立 A/B/C 人工对照基准。

## 6. 技术债

1. **版本冲突：** 根 README 同时出现 v0.2.0-alpha、v2.0.0-mvp 和历史 v0.1；核心包版本为 2.0.0，bridge 为 0.1.0。
2. **对象重复：** Workspace、Runtime Job/Craft、Treatment Record、bridge Case/Rule 各自描述相近事实。
3. **指标语义风险：** `v01_pipeline.scan_audio` 中 RMS 推导的 loudness 被标为近似 LUFS；它不能替代标准响度测量。
4. **过宽入口：** legacy 与主线命令共存，容易把实验能力误当生产能力。
5. **静默降级：** 多处 `except ...: pass` 用于可选路径；生产路径需要结构化 warning/failure event。
6. **存储碎片化：** JSON/JSONL/SQLite/文件目录/DuckDB 并存，关联 ID 不一致。
7. **环境分裂：** 核心要求 Python 3.10+，bridge 要求 3.12；需明确基线而非隐式混用。
8. **仓库卫生：** 当前存在未跟踪安装包、音频/视频与大量输出目录；必须在提交前做大文件和隐私审查。

## 7. 与新定位一致的部分

- 基础频谱、动态、声道、残差/差异工作属于 WSE。
- Workspace、Runtime、候选比较、报告、Craft 与人工审批属于 PPE。
- `moodify-bridge` 已确立 Production Case、证据、规则版本、人批和回归的核心原则。
- “不以更响代替更好”“不从小样本得出总体结论”与证据优先一致。

## 8. 与新定位冲突的部分

- README 中“一条命令”“自动化传统处理”式历史表达会误导项目边界。
- 近似指标若未标注 confidence/backend，可能被当作标准测量。
- “learning”“adopted”等命名未必要求显式人批，与规则治理原则不一致。
- 大量情绪、通用生成/消费者方向的历史叙述超出当前狭窄领域。
- 现有“已完成/100%”状态多为软件测试结论，不应等同于相对人工优势已验证。

## 9. 可以保留的模块

保留 `audio_io`、v01 pipeline、processing、分析特征、质量安全、Workspace services、Runtime runner/report/supervisor、API/console、Treatment Records、全部历史实验和现有入口。保留 legacy 兼容命令，但显式标注 legacy/experimental。`moodify-bridge` 作为 v0.4 case/evidence contract 的孵化实现继续发展。

## 10. 建议重构但暂时不要移动

| 当前模块 | 目标边界 | 当前动作 |
|---|---|---|
| `v01_analyzer.py`、`reality_metrics.py`、features/perception | WSE | 建适配层和指标注册，不移动实现 |
| legacy optimizer/search | Candidate Generation | 先登记实验状态和输入输出 |
| services/judge、version_compare | Evaluation | 先映射到 Evaluation/Decision schema |
| Runtime runner/supervisor/report | PPE | 先让运行输出 case/event ID |
| Craft/learning modules | Rules / Production Learning Loop | 禁止自动 production promotion，建立兼容映射 |
| 分散节拍/特征代码 | MSE | 先建实验接口与置信度，不宣称完整结构恢复 |

## 11. 未来 90 天最重要的技术瓶颈

1. 同一输入、pipeline、rules 能否生成可复现且关联完整的 case。
2. WSE 指标定义、算法版本、置信度和标准后端能否统一。
3. Candidate/Evaluation/Decision 是否能成为不可变事实，而不是报告文本。
4. MSE 的稳定最小集（BPM、beat grid、key、section）能否建立校正和置信度协议。
5. Golden Set 是否具备授权、覆盖、固定哈希和失败保留。
6. 人工对照实验能否控制响度、顺序、听众群体和处理条件。
7. 三套运行面如何通过兼容层收敛，而不破坏现有 1,000+ 测试函数覆盖的行为。

## 12. 审计结论

Moodify 已有较厚的音频与生产基础，但尚未形成统一、可验证的 WSE—MSE—PPE 闭环。v0.4 不应重写 DSP；应把 `moodify-bridge` 的不可变 contract 接到现有主链，以一个 case ID 贯通测量、候选、决策、规则和回归。任何“优于人工”的结论必须留待预注册的 A/B/C 对照实验。


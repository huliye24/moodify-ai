# DSK-MFY-SPECTRAL-EVIDENCE-012｜处理前后频谱证据与研究数据包 v0.1

**计划日期：** 2026-08-01  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**任务性质：** 今日新增、稍后串行执行  
**建议时间盒：** 4 小时；时间不足则按阶段停下并如实交接

## 1. 唯一目标

为每首歌曲和每条已有音轨建立可复现的处理前后证据：

```text
Source / Stem Before + Candidate / Stem After
  -> 同条件测量
  -> Before / After 频谱图
  -> Difference 频谱图
  -> 区段与频带指标
  -> JSON + CSV/Parquet 事实层
  -> XLSX 人工研究视图
  -> manifest / hashes / limitations
```

本任务建立“观察声音变化”的研究基础设施，不证明声音一定改善，不训练模型，不用频谱外观替代人工听感。

## 2. 开始前审计

完整读取并检查：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-SPECTRAL-EVIDENCE-012\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SPECTRAL-EVIDENCE-012\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SPECTRAL-EVIDENCE-012\03_DATA_CONTRACT_SEED.md
E:\moodify\docs\product\MOODIFY_WEEKLY_EXECUTION_2026-08-03.md
E:\moodify\docs\treatment_records\README.md
E:\moodify\scripts\v01_create_treatment_record.py
E:\moodify\scripts\v01_update_treatment_feedback.py
E:\moodify\scripts\v01_aggregate_treatment_records.py
```

同时检查适用的 `AGENTS.md`、Git/dirty 状态、Python 环境、已有 WSE/测量/报告/Excel 能力及测试。现有音频、输出、Treatment Records 和用户修改全部只读，不得整理、覆盖或回写。

先写 `00_IMPLEMENTATION_AUDIT.md`，列明可复用模块、依赖、冲突、输入权利状态、实际可用样本和计划输出。若没有合法可用的 before/after 对，允许仅用合成 fixture 验证工具，但必须标记 `REAL_DATA_NOT_RUN`。

## 3. 允许范围

优先放入隔离包：

```text
E:\moodify\science\Moodify_Spectral_Evidence_v0_1_Package\
E:\moodify\docs\architecture\SPECTRAL_EVIDENCE_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SPECTRAL-EVIDENCE-012\
E:\moodify\outputs\deepseek_validation\DSK-MFY-SPECTRAL-EVIDENCE-012\
```

不得修改生产 DSP、Runtime、Bridge、MRS、Preset、历史 Treatment Records 或真实音频。不得实现分轨模型；只接受已经存在且来源明确的 stem。不得联网、增加 GPU 要求、提交 Git、删除或覆盖既有产物。若必须新增依赖、修改生产入口或写入其他目录，先写 `SCOPE_CHANGE_REQUEST.md` 并 HOLD。

## 4. Stage 0｜冻结证据合同（45 分钟）

在编码前完成：

- `SPECTRAL_EVIDENCE_CONTRACT.md`：case、track、role、before/after、时间轴和版本关系；
- `ANALYSIS_PARAMETER_CONTRACT.md`：采样率、声道策略、FFT/window/hop、幅度标度、颜色范围与响度匹配规则；
- `METRIC_DICTIONARY.md`：单位、算法版本、适用条件、null 原因；
- `XLSX_RESEARCH_SCHEMA.md`：工作表、列、数据类型、来源与超链接；
- `VISUAL_INTERPRETATION_LIMITS.md`：频谱图能与不能证明什么；
- `STAGE_0_GATE.md`。

强制规则：before/after 必须使用完全相同的分析参数、时间范围、通道策略和色标；原始比较与响度匹配比较分开保存，禁止暗中标准化。缺失 stem、区段或指标必须是显式状态，不得填零。

## 5. Stage 1｜确定性分析与图像生成（75 分钟）

在隔离包实现 CLI：

```text
python -m moodify_spectral_evidence audit ...
python -m moodify_spectral_evidence build --case-spec CASE.yaml --output-dir NEW_DIR
python -m moodify_spectral_evidence validate BUNDLE_DIR
```

每个合法 before/after track pair 至少生成：

- `before_spectrogram.png`、`after_spectrogram.png`；
- 使用有符号 dB 差值、固定对称色标的 `difference_spectrogram.png`；
- 可选但同样固定条件的波形/频谱均值图；
- `track_metrics.json`、`band_metrics.csv`、`section_metrics.csv`；
- 资产 SHA-256、分析参数、软件版本、生成时间与 provenance。

覆盖整曲及实际存在的 vocals、drums、bass、piano、guitar、other 等 stem；不得因名称猜测乐器。时间轴不一致、采样率不一致和长度不同必须被检测、记录或拒绝，不能静默裁切。

指标可包含 Peak、True Peak（已有可靠实现时）、RMS、LUFS-I/LRA（适用时）、crest factor、clipping count、silence ratio、spectral centroid、rolloff、band energy、noise proxy、transient density。任何不可可靠计算的指标必须为 null 并附 reason。

## 6. Stage 2｜事实层与 Excel 研究工作簿（60 分钟）

生成一个只读研究交付包：

```text
manifest.json
case_summary.json
track_summary.csv
band_comparison.csv
section_comparison.csv
spectral_evidence.xlsx
assets/...
```

若仓库已有 Parquet 支持，同时生成 Parquet；不得为此新增依赖。Excel 至少包含：

| Sheet | 内容 |
|---|---|
| README | case、版本、生成器、限制和阅读方法 |
| Track_Summary | 每条轨道 before/after/delta 及资产链接 |
| Band_Comparison | 频带能量、变化量、单位和有效性 |
| Time_Sections | 区段起止、指标与差异 |
| Decision_Log | 处理动作、参数引用、操作者；未知则留显式 null |
| Human_Review | 独立的人工试听标签、选择、理由和时间；不自动填写 |
| Data_Quality | 缺失值、对齐、失败、警告、算法版本 |

Excel 只作为人工研究视图，不是唯一事实源；单元格必须能追溯到 JSON/CSV 与图像。不要嵌入巨大音频文件，不要写宏，不要伪造人工评价。

## 7. Stage 3｜验证、失败注入与交接（60 分钟）

至少验证：

1. 同输入、同参数双构建得到相同结构化数据和确定性资产命名；
2. 图像尺寸、坐标、色标、单位和 before/after 参数一致；
3. 差值方向固定为 `after - before`，正负含义在图例中明确；
4. Excel 可打开，公式/链接有效，行数与事实层一致；
5. 源音频和既有记录哈希未变化；
6. 注入缺失 stem、损坏 WAV、长度不匹配、采样率不同、重复 track ID、非法路径、NaN/Inf、无写权限等失败；
7. 测试、lint、type check、CLI smoke；未运行项必须说明原因。

最终生成 `VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、`PROGRESS.md` 和 `HANDOFF.md`。HANDOFF 必须列出绝对路径、命令、样本性质、图像/表格数量、失败数量、限制和下一步建议。

## 8. P0 门禁

出现以下任一情况即 HOLD：

- before/after 使用不同分析参数或色标却继续比较；
- 静默裁切、重采样、响度匹配或归一化；
- 将缺失值填为零，或根据文件名猜测 stem；
- 用频谱差异、自动指标或 Excel 公式宣布“声音改善”；
- 自动生成或伪造 Human Review；
- 覆盖源音频、历史记录或既有输出；
- 图像与结构化数据无法追溯到输入哈希和算法版本；
- 需要越界写入、新依赖、联网或生产修改却未申请范围变更。

最终状态只能是 `READY_FOR_CODEX_REVIEW`、`REAL_DATA_NOT_RUN`、`REWORK` 或 `HOLD`。DeepSeek 不得宣布该能力已接入生产、已形成训练模型或已证明某种处理更好。


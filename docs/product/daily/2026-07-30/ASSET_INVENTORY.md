# Moodify 验证资产盘点｜D1-02

**记录日期：2026-07-30**  
**任务：D1-02｜盘点真实音频、Treatment Records、MRS和Listening资产**  
**执行方式：只读统计；未移动、复制、重命名或删除任何资产**  
**门禁结果：G2 PASS（验证音频权利确认仍是后续前置条件）**

## 1. 状态定义

- `READY`：路径有效、格式可读、用途清楚，可直接用于对应下一步；
- `PARTIAL`：资产存在，但缺少元数据、权利确认、标签、反馈或完整性证据；
- `HISTORICAL`：用于历史追溯，不代表当前版本状态；
- `BLOCKED`：缺失、损坏、不可读或权利状态不明，不能进入验证集。

状态针对具体用途判断。同一资产可以作为历史证据可用，但不适合作为新一轮声音验证输入。

## 2. 总体盘点

以下是目录内实际文件数量。音频数是目录计数，不是去重后的作品数；原始文件、处理版本、响度匹配版本和重复格式可能同时存在。

| 目录 | 文件数 | 音频数 | JSON/JSONL | 体积约 | 状态 | 当前用途 |
|---|---:|---:|---:|---:|---|---|
| `pre-music` | 274 | 77 | 64 | 2.67 GB | PARTIAL | 近期分轨项目、处理产物和Workspace黄金路径来源 |
| `music` | 44 | 44 | 0 | 0.79 GB | PARTIAL | 22组MP3/WAV音乐文件，存在同名和`(1)`版本 |
| `local_audio_assets` | 46 | 11 | 16 | 0.23 GB | PARTIAL | MHP-026七类测试源及处理库 |
| `uploads` | 4 | 4 | 0 | 0.14 GB | BLOCKED | 历史上传音频，目录ID不表达来源和权利 |
| `listening_test` | 54 | 34 | 0 | 0.97 GB | PARTIAL | Before/After试听材料和评分卡模板 |
| `inspector_reports` | 335 | 31 | 34 | 0.99 GB | HISTORICAL/PARTIAL | v0.1检查报告、指标和响度匹配文件 |
| `calibration_reports` | 114 | 27 | 30 | 0.20 GB | HISTORICAL | v0.1.0-alpha.1及调参批次结果 |
| `treatment_records` | 33 | 0 | 28 | 0.15 MB | PARTIAL | 工艺记录与人工反馈；存在汇总不一致 |
| `data` | 43 | 0 | 21 | 19.58 MB | PARTIAL | Runtime、MRS、Workspace和MVP证据 |
| `reports` | 273 | 0 | 78 | 0.37 MB | HISTORICAL/PARTIAL | 各轮运行、MRS和实验结论 |
| `outputs` | 513 | 72 | 39 | 1.16 GB | HISTORICAL/MIXED | 多轮生成产物；不得直接作为源音频池 |

## 3. 音频资产判断

### 3.1 `pre-music`

主要内容：

- `2026-07-24_1441_split_by_lalalai`；
- `2026-07-29_1223_split_by_lalalai`；
- 两个对应ZIP包；
- 若干直接WAV；
- 日志、处理输出和release目录。

音频格式：74个WAV、3个FLAC。

判断：路径和近期项目结构存在，但目录混合源文件、stem、处理候选和交付产物，且未发现机器可读的授权或权利元数据，因此作为新验证集来源时为`PARTIAL`。其中2026-07-24项目已被Workspace v2验收引用，但这只证明工作流，不自动证明可用于新的公开或商业测试。

### 3.2 `music`

音频格式：22个MP3、22个WAV。多个作品同时存在MP3/WAV和`(1)`版本。

判断：文件直接可读，但缺作品ID、版本关系、来源、生成方式和权利记录。当前为`PARTIAL`，在去重与权利确认前不得直接抽取5首验证集。

### 3.3 `local_audio_assets/mhp026/source`

存在7类源音频：

| 类型 | 文件 | 技术可用性 | 权利状态 |
|---|---|---|---|
| AI vocal | `01_ai_vocal/...wav` | 可定位 | 未登记 |
| Suno pop | `02_suno_pop/...flac` | 可定位 | 未登记 |
| Rock | `03_rock/...mp3` | 可定位 | 未登记 |
| Ambient | `04_ambient/...mp3` | 可定位 | 未登记 |
| Rap/spoken | `05_rap_spoken/...mp3` | 可定位 | 未登记 |
| Dense mix | `06_dense_mix/...mp3` | 可定位 | 未登记 |
| Thin demo | `07_thin_demo/...mp3` | 可定位 | 未登记 |

判断：这是目前结构最清楚、曲目类型覆盖最好的候选池，但仓库内未找到license、copyright、授权、来源URL或生成账户记录，因此整体为`PARTIAL`。只要荣景文川确认这7个源文件拥有内部验证使用权，即可从中冻结5首验证集。

### 3.4 `uploads`

存在4个WAV，位于4个不透明ID目录中。未找到项目身份、上传者、用途或授权说明。

判断：`BLOCKED`。在补齐来源和权利记录前不得进入验证集。

## 4. Treatment Records实际状态

### 4.1 实际文件与汇总不一致

`treatment_records/summary.json`声称：

- 30条记录；
- 6条已完成反馈；
- 24条待反馈；
- 每个Preset各10条。

实际目录重新解析得到：

- 27个`treatment_record`文件；
- 3条已完成反馈；
- 24条待反馈；
- 覆盖10个song_id，但其中3个song/preset组合文件缺失。

汇总引用但当前不存在的文件：

| 缺失文件 | song_id | preset | 汇总所称状态 |
|---|---|---|---|
| `electronic_wide_space.json` | `electronic_001` | `wide_space` | completed |
| `piano_clean_master.json` | `piano_001` | `clean_master` | completed |
| `vocal_folk_warm_vocal.json` | `vocal_folk_001` | `warm_vocal` | completed |

这三条缺失文件恰好解释了“30/6”与“27/3”的差异。

### 4.2 当前判定

Treatment Records整体为`PARTIAL`：

- 记录模式、前后指标、响度匹配字段和人工反馈结构存在；
- 实际已完成反馈只有3条，覆盖不足；
- `summary.json`已经过时或与工作区不同步；
- 在修复汇总前，所有统计必须从实际记录文件重新计算；
- 不应恢复或伪造三条缺失记录，应先查明删除、迁移或未提交原因。

## 5. Listening与Inspector资产

### 5.1 Listening Test

存在：

- 34个音频文件；
- 20个Markdown文件；
- MHP-026七类评分卡；
- MHP-027的AI vocal和dense mix评分卡；
- 早期vocal_folk、piano和electronic对比材料。

抽查评分卡显示：

- 已规定`before → after_matched → before → after_matched`顺序；
- 明确禁止因更响而给高分；
- 包含清晰度、温暖度、空间感、刺耳控制、塑料感、伪影和目标适配等维度；
- Markdown评分卡本身大多为空模板；真实的3条已完成反馈保存在Treatment Record JSON中。

判断：协议骨架`READY`，完整反馈数据`PARTIAL`。

### 5.2 Inspector Reports

存在指标对比JSON、Markdown/HTML报告、Before/After及`after_matched.wav`等产物，能够支持历史处理复盘。

判断：作为v0.1工艺历史证据为`HISTORICAL`；作为本周当前代码结果为`PARTIAL`，因为它们不是当前HEAD重新运行产生的证据。

### 5.3 Calibration Reports

三个主要批次：

- `v0.1.0-alpha.1`；
- `v0.1.0-alpha.1-tuning-a`；
- `v0.1.0-alpha.1-tuning-b`。

判断：`HISTORICAL`。可以帮助选择失败案例和比较旧参数，但不能作为当前v2声音能力的现行证明。

## 6. MRS资产判断

### 6.1 可定位资产

配置与数据包括：

```text
configs/mrs_weights.yaml
configs/mrs_thresholds.yaml
configs/mrs_open_v03.yaml
configs/mrs_formula_v02.yaml
data/calibration/mrs_002/registry.jsonl
data/calibration/mrs_002/labels.jsonl
data/validation/ground_truth.jsonl
reports/nem_mrs_002/
reports/listening_probe/
```

### 6.2 已知历史结论

`reports/nem_mrs_002/calibration_report.md`记录：

- 61个音频样本、5类曲风；
- pseudo-MRS对这批材料不鲁棒；
- 61个样本全部得到负向delta；
- 旧over-dark检测没有区分力；
- Gate accuracy为9.1%（3/33），远低于85%目标。

`reports/listening_probe/mrs_listening_gap_brief.md`记录：

- pseudo-MRS与偏好的相关性约`r=0.19`；
- MRS Open与人工判断一致率约60.6%；
- 缺分曲风校准；
- 需要100+真实人工pairwise标签。

判断：MRS代码和配置资产存在，但历史校准结论明确表明其不能单独作为声音好坏依据。旧报告为`HISTORICAL`；当前HEAD的MRS能力在D1-04重新运行前为`PARTIAL`。

## 7. Workspace v2黄金路径证据

`data/mvp_evidence/workspace_v2_candidate`当前包含：

- `candidate_manifest.json`；
- `v2_pytest.xml`。

Manifest记录：

- 候选提交`1c0f270e28d9e767fd372f799a00836ffb4a5321`；
- 基线标签`v2.0.0-mvp`；
- Workspace测试179通过、0失败；
- 样本`WSA_20260724_001`具有2个候选版本；
- 血缘、Judge降级披露、自动验收fixture和归档完整性通过。

当前`data/workspace_v2/projects`没有可枚举的持久化项目文件，因此可核验的封口证据主要是Manifest与JUnit XML，而不是一个仍驻留在Workspace存储中的完整项目树。

判断：作为v2工作流发布证据为`READY`；作为本周声音质量证据为`HISTORICAL/NOT APPLICABLE`。

## 8. 周二验证集候选池

为了覆盖至少3类声音问题，建议优先从MHP-026结构化源中选择以下5首：

| 优先级 | 类型 | 主要验证问题 | 当前状态 |
|---:|---|---|---|
| 1 | AI vocal | 人声塑料感、稳定性、主体清晰度 | PARTIAL：待权利确认 |
| 2 | Dense mix | 层级拥挤、动态和主体分离 | PARTIAL：待权利确认 |
| 3 | Thin demo | 厚度、频谱完整性和过度处理风险 | PARTIAL：待权利确认 |
| 4 | Rock | 瞬态、动态保留和高频刺激 | PARTIAL：待权利确认 |
| 5 | Ambient | 空间、宽度、尾音和单声道兼容 | PARTIAL：待权利确认 |

备选：Suno pop、Rap/spoken。

候选理由：七类源已经具有明确类型、已有历史Treatment和响度匹配产物，便于比较新旧结果。但在荣景文川明确确认“允许内部验证”前，这五首不能升级为`READY`。

## 9. 权利与来源检查

对`pre-music`、`local_audio_assets`、`music`、`uploads`、`listening_test`、`treatment_records`和MVP证据中的Markdown、JSON、JSONL、TXT进行了关键词检索，未找到可作为正式权利证明的license、copyright、rights、授权、版权、来源URL或生成账户元数据。

因此：

- 技术可读不等于有权使用；
- 本周验证集冻结前必须由荣景文川确认内部使用权；
- 后续`ProductionSpec`应加入素材权利状态字段；
- 不在本任务中推测作品归属。

## 10. G2验收

| 检查项 | 结果 | 证据 |
|---|---|---|
| 主要资产类别全部覆盖 | PASS | 第2—7节 |
| 每项给出路径 | PASS | 各节路径与目录表 |
| 音频只统计、未修改 | PASS | 本任务仅执行只读命令 |
| 区分源音频、测试材料和生成产物 | PASS | 第3、5、7节 |
| 权利不明音频标为PARTIAL/BLOCKED | PASS | 第3、8、9节 |
| Treatment反馈按实际文件重算 | PASS | 第4节：27条/3完成/24待定 |
| 给出验证集候选池 | PASS | 第8节 |

**G2结论：PASS。D1-02完成。下一步可以进入D1-03能力—证据—缺口矩阵。**

## 11. D1-03必须继承的事实

1. Workspace v2工作流已封存，但不能等同于声音质量已验证；
2. MRS历史校准准确率和人工一致性不足，不能单独决定通过；
3. Treatment汇总与实际文件不一致，当前真实数为27条、3条完成反馈；
4. 现有试听协议可复用，但反馈覆盖不足；
5. 本周五首候选在权利确认前均为`PARTIAL`。


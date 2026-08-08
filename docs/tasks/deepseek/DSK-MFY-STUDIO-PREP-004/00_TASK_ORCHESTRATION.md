# DSK-MFY-STUDIO-PREP-004｜商业录音棚项目 6 小时工具链预备

**日期：2026-07-31**  
**执行窗口：最长 6 小时，五批串行**  
**任务所有者与最终 Judge：Codex / 授权用户**  
**执行 Worker：DeepSeek（用户手动发送命令）**  
**性质：新增隔离工具、测试、运行手册和合成验证；不处理明日客户音频**

## 1. 业务目标

为 2026-08-01 的收费录音棚项目准备一套可靠的本地工具，使明日能够：

1. 在录音前冻结项目 brief、交付范围、采样规格、文件命名和备份路径；
2. 对录音资产做只读身份核验和技术 preflight；
3. 生成 WSE 基础测量、波段演化、动态、瞬态、立体声、相位/相关和残差证据；
4. 根据测量生成**候选处理计划**，而不是自动覆盖或直接作艺术决策；
5. 使用现有 Moodify pipeline 在隔离目录生成候选、做响度匹配比较并形成报告；
6. 保留失败、限制、人工审批点和所有输入/输出 SHA-256。

商业目标是“降低明天出错概率并提高判断深度”。本任务不证明 Moodify 已超过人工；未来只有受控 A/B/C 实验可以支持限定优势主张。

## 2. 任务边界

### 允许修改

```text
E:\moodify\tools\studio_session_prep\
E:\moodify\tests\studio_session_prep\
E:\moodify\docs\tasks\deepseek\DSK-MFY-STUDIO-PREP-004\
E:\moodify\outputs\deepseek_validation\DSK-MFY-STUDIO-PREP-004\
```

仅当新工具必须调用现有 package 且无法通过 import adapter 实现时，才可提出修改其他文件的建议；**不得自行修改**。

### 禁止修改

- `moodify-core-package/src/moodify/processing/`、preset、DSP、MRS、门限、Runtime、bridge schema/store；
- 客户文件、`local_audio_assets/`、历史实验、原运行产物和任何现有收费项目；
- Git 分支、暂存区、提交、远程；
- 依赖版本、系统环境、私有配置和密钥。

### 禁止行为

- 不读取或处理明日客户音频；测试只能使用程序生成的合成信号或明确的现有测试 fixture；
- 不覆盖、移动、重命名源文件；
- 不执行 `git reset/clean/stash/rebase/checkout --/commit/push`；
- 不安装或升级依赖；
- 不实现新的核心 DSP，不用占位公式冒充 LUFS/LRA/true peak/相位/掩蔽；
- 不把波谱变化写成“更好听”，不自动选择 Final，不自动晋级规则；
- 不生成客户承诺、报价或版权结论。

## 3. 必读事实源

开始前完整读取：

```text
E:\moodify\README.md
E:\moodify\docs\audit\PROJECT_AUDIT_2026_08.md
E:\moodify\docs\strategy\MOODIFY_POSITIONING_v0.4.md
E:\moodify\docs\architecture\MOODIFY_SYSTEM_ARCHITECTURE_v0.4.md
E:\moodify\docs\architecture\WSE_ARCHITECTURE.md
E:\moodify\docs\architecture\PPE_ARCHITECTURE.md
E:\moodify\docs\architecture\PRODUCTION_LEARNING_LOOP.md
E:\moodify\moodify-bridge\README.md
E:\moodify\moodify-bridge\src\moodify_bridge\metrics.py
E:\moodify\moodify-bridge\src\moodify_bridge\hashing.py
E:\moodify\moodify-bridge\src\moodify_bridge\services.py
E:\moodify\moodify-core-package\src\moodify\v01_pipeline.py
E:\moodify\scripts\v01_inspector.py
```

同时检查适用的 `AGENTS.md`、当前分支、HEAD、`git status --short` 和 Python 3.11/3.12 可用依赖。所有现存改动均视为用户资产。

## 4. 总体设计要求

新增工具目标目录：

```text
tools/studio_session_prep/
  README.md
  studio_prep.py
  models.py
  wse_profile.py
  candidate_plan.py
  reporting.py
  templates/
    session_brief.example.yaml
    delivery_contract.example.yaml
    quality_gate.example.yaml
```

测试目标目录：

```text
tests/studio_session_prep/
  test_models.py
  test_hash_safety.py
  test_wse_profile.py
  test_candidate_plan.py
  test_reporting.py
  test_cli_smoke.py
```

可以根据实际实现减少文件，但不得把所有职责塞入一个超大脚本。优先复用 bridge 的 hashing/metrics；不得复制一套同名但含义不同的指标。

CLI 最小接口：

```text
python tools/studio_session_prep/studio_prep.py session-init ...
python tools/studio_session_prep/studio_prep.py asset-verify ...
python tools/studio_session_prep/studio_prep.py wse-analyze ...
python tools/studio_session_prep/studio_prep.py candidate-plan ...
python tools/studio_session_prep/studio_prep.py candidate-compare ...
python tools/studio_session_prep/studio_prep.py report-build ...
```

所有写入必须位于显式 `--output-dir`；默认拒绝输出到源文件目录；已有输出默认拒绝覆盖，除非是全新空目录且显式确认。测试不得依赖网络、随机时间或客户素材。

## 5. 六小时分批执行

严格按 Batch 0→A→B→C→D 串行。每批完成后先运行该批测试并更新 `PROGRESS.md`。出现源文件变化、越权路径、现有测试回归或无法解释的指标时立即停止。

### Batch 0｜45 分钟｜事实审计与执行设计

任务：

1. 记录分支、HEAD、dirty status、Python 与可用依赖；
2. 阅读上述实现，确认哪些指标可真实复用，哪些必须保持 null；
3. 画出工具数据流和文件写入边界；
4. 列出明日商业风险：削波、采样规格、命名、双备份、take 丢失、响度偏差、相位、客户修改范围；
5. 写实现计划，禁止先编码后补设计。

输出：

```text
00_IMPLEMENTATION_AUDIT.md
PROGRESS.md
```

Batch Gate：所有 import/依赖路径真实；没有要求修改核心 DSP；输出边界明确。否则 `HOLD`。

### Batch A｜75 分钟｜录音项目初始化与资产安全

实现：

1. 严格的 SessionBrief、RecordingSpec、DeliverableContract、AssetEntry 数据模型；
2. `session-init`：从 YAML 初始化新会话目录和 manifest；
3. `asset-verify`：只读计算 SHA-256、大小、扩展名；音频可解码时记录采样率、声道、帧数和时长；
4. 生成 `RECORDING_DAY_CHECKLIST.md`：录音前、每个 take、录音后、离棚前四道检查；
5. 双备份路径必须不同；源路径和输出路径相同时拒绝；
6. 原始 take 只能登记，不能被工具重写。

测试：路径越界、重复 ID、缺失字段、错误哈希、源/输出同路径、已有输出拒绝覆盖、无音频依赖时清晰报错。

Batch Gate：生成的 manifest 可重复；运行前后合成源文件哈希一致；Batch A 测试全绿。

### Batch B｜90 分钟｜WSE 分析与高级候选计划

实现：

1. `wse-analyze` 调用现有 bridge adapters，输出版本化 JSON 和长表 CSV/Parquet（视已有依赖）；
2. 覆盖 peak/RMS/crest、spectral entropy/centroid/flux、band fractions、L/R correlation；
3. 新增**有定义且可测试**的 section/window evolution：固定 frame/hop，输出每窗时间、RMS、peak、centroid、band fractions；
4. 对缺失 loudness/LRA/true peak/phase/masking 明确 `null + warning`，不得用代理量冒充；
5. `candidate-plan` 根据指标和显式阈值生成 2—3 个**处理假设**：保守、平衡、探索；每项包含 evidence、risk、允许参数范围、人工检查点；
6. 候选计划不得输出“必然提升”“发行级”“超过人工”，不得自动运行或选择。

合成测试至少包括：静音、单位正弦、双声道同相、双声道反相、已知增益、低/高频组合、短音频。随机信号固定种子。

Batch Gate：数值夹具误差有断言；所有未知指标为 null；源哈希不变；Batch B 测试全绿。

### Batch C｜90 分钟｜隔离候选生成、比较与报告

实现：

1. 提供现有 v01 pipeline 的安全 adapter；只允许显式 `--execute-candidates` 执行；
2. 每候选使用独立目录，保存 preset、pipeline version、参数、命令、退出码、时间、输出哈希和失败；
3. 未安装核心依赖时退化为 dry-run candidate plan，不伪造音频输出；
4. `candidate-compare` 要求相同采样率和可解释对齐，复用 waveform correlation、fitted gain、relative residual、difference SNR；
5. 比较报告同时列技术差异、限制和人工试听栏，默认 `human_review=PENDING`；
6. 不自动选 Final；硬失败不得被单一总分冲销；
7. `report-build` 生成 Markdown 与 HTML 的录音项目技术报告。

只用合成信号做一次 dry-run 和一次可行的隔离候选 smoke；禁止碰真实客户音频。

Batch Gate：候选互不覆盖；失败留档；人工栏保持 PENDING；原文件哈希不变；Batch C 测试全绿。

### Batch D｜60 分钟｜全量验证、明日运行手册与交接

执行：

1. 新增测试全量运行；
2. `moodify-bridge` 测试；
3. 只读运行 core/Runtime 与本任务相关的 smoke；不得为追求全绿改无关代码；
4. CLI help 和六个命令 smoke；
5. 生成合成 demo 输出并检查 JSON/YAML/MD/HTML；
6. 对允许目录做 `git diff`，确认没有越权修改；
7. 写明未运行测试、依赖和建议命令。

输出：

```text
TOMORROW_STUDIO_RUNBOOK.md
VALIDATION_REPORT.md
HANDOFF.md
```

`TOMORROW_STUDIO_RUNBOOK.md` 必须包含：

- 到棚前 30 分钟检查；
- 录音工程规格与命名；
- 每个 take 的保存/备注；
- 双备份；
- 离棚前验证；
- 后期 ingest→WSE→candidate plan→candidate generation→human review→deliverable；
- 遇到削波、底噪、相位、丢 take、依赖故障时的降级方案；
- 明确“商业交付由人工批准，Moodify 不自动 Final”。

## 6. 代码质量要求

- Python 严格类型，清晰异常；路径操作使用 `pathlib`；
- 数据模型优先 Pydantic；若复用困难需说明，不得同时维护重复 schema；
- 不使用 shell 字符串拼接执行不可信路径；
- 输出 canonical JSON，时间为 UTC；
- 不隐藏异常，不用空 `except`；
- 函数单一职责，关键阈值可见且有单位；
- 不增加云依赖；不使用网络；
- 生成文件包含 tool version、schema version 和 source hash。

## 7. 验收标准

最终 `HANDOFF.md` 只有满足以下条件才可给 `READY_WITH_LIMITS`：

1. 五批均完成，新增测试全绿；
2. 六个 CLI 命令可运行或明确 dry-run；
3. 合成 demo 可生成 session manifest、WSE profile、candidate plan、comparison 和双格式报告；
4. 所有源文件运行前后哈希一致；
5. 没有修改允许范围外文件；
6. 未知测量为 null/warning；
7. 不自动 Final、不自动规则晋级；
8. 明日 runbook 可直接复制执行。

其他判定：

- `REWORK`：局部代码/测试问题可修复；
- `HOLD`：越权、源文件变化、依赖不可信、核心回归或证据污染。

## 8. 失败处理

任一批失败，停止后写：

```text
【MTP 失败报告】
任务编号 / 当前批次 / 已用时间 / 失败步骤 / 完整命令 / 完整错误
已创建或修改文件 / 源哈希检查 / git status / 可安全继续的唯一动作
```

不得失败后扩大修改范围或猜测式改核心代码。

## 9. 最终交接格式

`HANDOFF.md` 必须包含：批次时间与状态、文件列表、测试命令与结果、demo路径、可用/不可用能力、明日具体命令、已知限制、P0—P3问题、需要 Codex/用户决策的事项，以及唯一下一动作。

终端最终回复不超过 25 行，只给：总判定、各批状态、测试数、文件数、限制和 `HANDOFF.md` 路径。完成后停止。


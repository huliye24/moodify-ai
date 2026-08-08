# DSK-MFY-CAPABILITY-ACCRETION-017｜Phase 1: Capability Registry（能力注册表）

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** DSK-MFY-SCORE-ENGINE-009 已交付可读 HANDOFF（ACCEPTED 路径）；本系列论文
`DSK-MFY-CAPABILITY-ACCRETION-001`（能力引力井架构）为设计依据  
**执行上限：** 4 小时，阶段严格串行

## 1. 系列定位

`DSK-MFY-CAPABILITY-ACCRETION-017 ~ 021` 五包串行，落地"能力引力井"架构：

```text
017 Registry（注册表先行）   ← 本任务
→ 018 Adapter Boundary（适配器边界）
→ 019 Approved Execution（批准执行集成）
→ 020 Validation & Candidate（验证与候选选择）
→ 021 Knowledge Feedback（知识反馈）
```

五包严格串行：上一包 HANDOFF 可读且 Codex ACCEPT（或明确批准接口稳定）后才启动下一包。

## 2. Phase 1 核心目标

建立 **Capability Registry**：Moodify 知道当前环境存在哪些能力、由谁提供、
受什么约束，并以结构化记录取代"开发者记忆"。本任务只注册、不实现新适配器。

```text
发现已安装工具/能力
-> 登记 capability_id + provider_id
-> 声明输入/输出/约束/许可证
-> 健康检查与版本探测
-> evidence 要求
-> 能力矩阵文档
```

## 3. 必读与基线

完整读取：

```text
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/02_CODEX_ACCEPTANCE_MATRIX.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/03_PRINCIPLE_SEED.md
docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/HANDOFF.md
docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/BACKEND_CAPABILITY_MATRIX.md
docs/tasks/deepseek/DSK-MFY-STEM-MIDI-008/HANDOFF.md
docs/architecture/SCORE_ENGINE_ARCHITECTURE.md
docs/strategy/MOODIFY_INDUSTRIAL_DIRECTION.md
moodify-core-package/src/moodify/score_engine/backend.py
moodify-core-package/pyproject.toml
```

检查适用 `AGENTS.md`、Git/dirty 状态、Python、各候选工具的
可执行文件与版本。**只读探测**，不安装、不下载、不修改第三方程序。

本机已知环境事实（2026-08-02 探测）：

| 工具 | 路径 | 版本 |
|---|---|---|
| MuseScore | `C:\Program Files\MuseScore 4\bin\MuseScore4.exe` | 4.5.1 |
| Audacity | `C:\Program Files\Audacity\Audacity.exe` | 待探测 |
| FFmpeg | `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_...\bin\ffmpeg.exe` | 8.1.1 |
| SoX | `%LOCALAPPDATA%\Microsoft\WinGet\Packages\ChrisBagwell.SoX_...\sox.exe` | 14.4.2 |
| RubberBand | `E:\moodify\tools\third_party\rubberband-4.0.0\...\rubberband.exe` | 4.0.0 |

## 4. 范围与许可证边界

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\capability_registry\
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\capability_registry\
E:\moodify\moodify-core-package\pyproject.toml（仅必要时）
E:\moodify\docs\architecture\CAPABILITY_ACCRETION_ARCHITECTURE.md（新建）
E:\moodify\docs\tasks\deepseek\DSK-MFY-CAPABILITY-ACCRETION-017\
E:\moodify\outputs\deepseek_validation\DSK-MFY-CAPABILITY-ACCRETION-017\
```

禁止：修改 Runtime/Bridge/DSP/MRS/008/009 实现与真实歌曲资产；复制/修改
第三方工具源码、site-packages、模型、声音库、字体；MATLAB 调用；
Git 分支/暂存/提交/推送/reset/clean/stash/checkout；网络下载。

## 5. 任务内容

### Stage A｜Registry 模型与 manifest schema（60 分钟）

1. `CapabilityRegistry`：注册/查询/列出能力与 provider；持久化为 JSON/YAML。
2. `CapabilityContract`：capability_id、contract_version、purpose、inputs、outputs、
   quality_policy、providers、execution 约束、validation 要求、evidence 要求
   （对齐论文 Appendix A 的 minimal record）。
3. `ProviderRecord`：provider_id、adapter_version、license_class、版本、路径、
   状态（active/known_missing/unsupported）、健康检查结果。
4. **`known_failure_modes`（负面知识字段）**：每个能力/ provider 必须声明
   已知失败模式与排除的路径（如 MuseScore 多页 SVG 页码后缀、一次仅一个 `-o`、
   ffprobe 对未知容器的退出行为、sox 对 8-bit 输入的精度损失）。声明
   "未遇到失败" 不是合法记录——必须写 `none_encountered_yet` 或真实边界。
   未安装能力只登记 `known_missing` + 已知安装风险，禁止伪注册。
5. manifest 严格 schema：未知键拒绝；双运行序列化一致。

### Stage B｜环境探测器（90 分钟）

对以下工具实现探测（版本、路径、可用性、许可证分类）：

- MuseScore（可复用 009 的探测逻辑思想，但**不得 import 009 实现**——本包独立，
  009 只是事实基线）
- FFmpeg / ffprobe
- SoX
- RubberBand
- Audacity
- Basic Pitch（.venv-basic-pitch 存在性 + python 包探测）
- Moodify 自身能力：score_engine（009）、transcription（008）

探测只读：不执行任何加工命令，不修改任何文件。

### Stage C｜首批能力注册（90 分钟）

按论文 §14 能力域，注册本机真实存在的能力（不注册未安装的）：

| capability_id | 域 | 现 provider | 许可 |
|---|---|---|---|
| media.transcode | 媒体基础 | ffmpeg | GPLv3/LGPL（外部进程） |
| media.probe | 媒体基础 | ffprobe | GPLv3/LGPL |
| notation.render | 音乐结构 | musescore | GPLv3（外部进程） |
| audio.time_stretch | 音频变换 | rubberband | GPLv2（外部进程） |
| audio.measure_loudness | 波谱分析 | sox stat 子集 | LGPL（外部进程） |
| audio.separate_manifest | 音乐结构 | basic_pitch（008 基线） | Apache-2.0 |
| waveform.region_edit | 音频变换 | audacity | GPLv2（外部进程） |

每个能力必须有：输入/输出声明、quality_policy、validation 要求、
evidence 要求、**known_failure_modes（负面知识）**。provider 缺失时状态
`known_missing`（如分离模型 Demucs 未装）。

**地质记录起点（negative knowledge seed）**：注册每个能力时，从既有
项目事实中提取至少一条真实失败模式作为种子（例如 009 的 FAILURE_LEDGER
中的 MuseScore 多页 SVG / 单 `-o` 限制、008 的 Demucs 未装、round-trip
隐藏损失禁令）。注册表不是空表——它从第一天就携带项目已学会的边界。

### Stage D｜验证与文档（60 分钟）

1. 新增测试：schema 严格性、双运行一致性、探测正确性（存在/缺失）、
   注册表持久化 round-trip、能力矩阵生成。
2. 相关 Core 回归 + CLI help/smoke + Ruff；记录未运行项。
3. `CAPABILITY_ACCRETION_ARCHITECTURE.md`：六层架构、注册表位置、
   capability/provider 术语、首批能力矩阵、后续接入顺序。
4. 更新 `PROGRESS.md`、`VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、`HANDOFF.md`。

## 6. P0 门禁与停止条件

**深度维持验收（系列原则 §3.4）**：本包处于后期模式，验收不以改动幅度
为准，而以三问为准——①注册表登记能力后是否新增了已知失败模式/边界记录
（地质记录起点，无则 REWORK）；②既有 009/008 边界是否被保留未松动；
③探测结果是否以可复现形式保存（否则下次重新探测等于失忆）。

必须成立：探测只读；未安装工具不注册为可用；manifest 严格 schema；
许可证与版本真实记录；dirty 边界未越界；旧 CLI 无回归；能力矩阵反映真实环境。

立即停止：需要安装/下载组件、修改 008/009/Runtime 实现、MATLAB 调用、
范围外写入、真实歌曲被处理、现有用户修改被还原、伪报告已安装能力。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。DeepSeek 完成
HANDOFF 后停止，由 Codex 给出 `ACCEPT / REWORK / HOLD`。

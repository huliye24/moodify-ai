# DSK-MFY-CAPABILITY-ACCRETION-018｜Phase 2: Adapter Boundary（适配器边界）

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** DSK-MFY-CAPABILITY-ACCRETION-017 已 ACCEPT（Registry 可用）  
**执行上限：** 4 小时，阶段严格串行

## 1. 核心目标

把所有 provider 特定命令移到 **适配器** 之后，业务/工作流逻辑只依赖能力合同，
provider 名不得泄漏到上层（论文 Law 5）。

```text
Capability contract（上层）
   ↑ 稳定接口
ProviderAdapter Protocol
   ├── MuseScoreAdapter
   ├── FFmpegAdapter / FFprobeAdapter
   ├── SoXAdapter
   ├── RubberBandAdapter
   ├── AudacityAdapter
   └── BasicPitchAdapter（调用 008 能力）
```

每个适配器：探测、版本、invoke（contract 输入 → provider 命令/API）、
错误翻译、受控工作目录、命令 manifest、超时/资源策略、evidence 产出。

## 2. 必读与基线

```text
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-018/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-018/02_CODEX_ACCEPTANCE_MATRIX.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/HANDOFF.md
docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/00_TASK_ORCHESTRATION.md
docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/BACKEND_CAPABILITY_MATRIX.md
docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md（017 交付）
moodify-core-package/src/moodify/score_engine/musescore_backend.py
moodify-core-package/src/moodify/score_engine/backend.py
moodify-core-package/src/moodify/capability_registry/（017 交付）
```

## 3. 范围与许可证边界

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\capability_registry\（含 adapters\ 子包）
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\capability_registry\
E:\moodify\moodify-core-package\pyproject.toml（仅必要时）
E:\moodify\docs\architecture\CAPABILITY_ACCRETION_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-CAPABILITY-ACCRETION-018\
E:\moodify\outputs\deepseek_validation\DSK-MFY-CAPABILITY-ACCRETION-018\
```

禁止：修改 009 `score_engine/musescore_backend.py`、008 实现、Runtime/Bridge/DSP/MRS、
真实歌曲；复制/修改第三方源码、site-packages、模型、声音库、字体；
MATLAB 调用；Git 分支/暂存/提交/推送/reset/clean/stash/checkout；网络下载。

**注意：009 的 MuseScoreBackend 已是"类适配器"实现。本任务不得改写它，
而是在 adapter 层把它包为 provider（组合而非修改），或者在新 adapter 中
体现同等安全标准。**

## 4. 任务内容

### Stage A｜Adapter Protocol 与基类（60 分钟）

1. `ProviderAdapter` Protocol：capability_id、provider_id、detect()、version()、
   invoke(contract_request) -> AdapterResult、health()、evidence_schema。
2. `AdapterResult`：status（success/failure/unavailable）、artifacts、evidence、
   errors、exit_code、elapsed。
3. 统一错误分类：invalid_input / provider_defect / environment_failure / timeout /
   partial_output / policy_rejection（论文 Gate 8 失败分类）。
4. 受控工作目录：每次 invoke 使用全新临时目录，输出哈希，拒绝路径逃逸。

### Stage B｜五个适配器（150 分钟）

每个适配器要求：argv 数组调用（禁 shell 拼接）、超时、stdout/stderr、
版本与命令入 evidence、缺失时稳定 unavailable：

| 适配器 | capability | provider |
|---|---|---|
| MuseScoreAdapter | notation.render | MuseScore 4 CLI |
| FFmpegAdapter / FFprobeAdapter | media.transcode / media.probe | ffmpeg / ffprobe |
| SoXAdapter | audio.measure_loudness 等 sox 能力 | sox |
| RubberBandAdapter | audio.time_stretch | rubberband |
| AudacityAdapter | waveform.region_edit（受控导出） | audacity CLI/插件模式 |
| BasicPitchAdapter | audio.transcribe_midi | 008 transcription（import 接口） |

BasicPitchAdapter 是唯一允许 import 008 接口的适配器（因为它是 Moodify 内部
能力而非外部进程）；Audacity 若只支持 GUI 则能力声明 human_handoff，不伪称自动化。

### Stage C｜CLI 与文档（60 分钟）

1. `moodify capabilities adapters`（列表）、`moodify capabilities invoke <id> ...`
   （显式受控调用，仅测试 fixture）。
2. 架构文档更新：adapter 层、错误分类表、适配器清单。
3. 测试：每个适配器存在/缺失两态、argv 数组、超时、错误翻译、路径逃逸拒绝、
   双运行、fixture 端到端（合成输入）。
4. 更新 PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF。

## 5. P0 门禁与停止条件

**深度维持验收（系列原则 §3.4）**：后期模式，验收不以改动幅度为准——
①每个适配器必须新增 known_failure_modes（适配器发现的 provider 边界，
如某版本 CLI 参数差异、编码行为），无新地质记录则 REWORK；②既有
009/008 的 round-trip 与转录边界未松动；③错误分类与 evidence 以结构化
形式持久化，不依赖工人记忆。

必须成立：provider 名不出现在上层业务逻辑；argv 数组；无 shell 注入；
缺失 provider 稳定降级；错误分类统一；输出隔离；旧 CLI 回归；真实歌曲不处理。

立即停止：需要安装组件、修改 008/009 实现、MATLAB、范围外写入、伪称自动化、
GPL 混淆、网络下载、现有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

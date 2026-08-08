# DSK-MFY-STEM-MIDI-008｜分轨感知 Audio-to-MIDI v0.2

**日期：** 2026-08-01  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**执行方式：** 四阶段严格串行；合同与基线未通过时禁止实现

## 1. 目标

把当前 `moodify transcribe` 从“一个音频文件调用 Basic Pitch”升级为：

```text
audio/stems -> stem classification -> per-stem transcription
            -> non-destructive cleanup -> multitrack MIDI + evidence
```

首批支持 `vocals / bass / piano / guitar / other`。鼓轨只登记为
`UNSUPPORTED_FOR_PITCH_TRANSCRIPTION`，不得用 Basic Pitch 音高结果冒充鼓 MIDI。
原始逐轨 MIDI 永远保留；清洗和合并只能生成派生文件。

## 2. 必读事实源

开始前完整读取并记录 SHA-256：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-STEM-MIDI-008\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-STEM-MIDI-008\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-STEM-MIDI-008\03_PRINCIPLE_SEED.md
E:\moodify\docs\architecture\AUDIO_TO_MIDI.md
E:\moodify\moodify-core-package\pyproject.toml
E:\moodify\moodify-core-package\src\moodify\transcription.py
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\test_transcription.py
E:\moodify\scripts\install_transcription.ps1
E:\moodify\tools\score_asset_pipeline.py
```

检查适用 `AGENTS.md`、当前分支/HEAD、`git status --short`、Python 3.11、
`.venv-basic-pitch`、Basic Pitch/ONNX/Demucs 可用性。现有 dirty worktree、
未跟踪文件和刚接入的转录实现全部属于用户，不得覆盖或还原。

## 3. 范围

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\transcription.py
E:\moodify\moodify-core-package\src\moodify\transcription_pipeline\
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\test_transcription.py
E:\moodify\moodify-core-package\tests\transcription\
E:\moodify\moodify-core-package\pyproject.toml
E:\moodify\scripts\install_transcription.ps1
E:\moodify\docs\architecture\AUDIO_TO_MIDI.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-STEM-MIDI-008\
E:\moodify\outputs\deepseek_validation\DSK-MFY-STEM-MIDI-008\
```

禁止修改其他 Core DSP、Runtime、Bridge、preset、MRS、历史任务、真实歌曲、
客户资产和既有输出。禁止 Git reset/clean/stash/checkout/commit/push/切分支。
禁止修改第三方 site-packages 或把 Basic Pitch/Demucs 模型复制进仓库。
新增依赖、网络下载或扩大范围前写 `SCOPE_CHANGE_REQUEST.md`，置为 HOLD。

## 4. Stage 0｜基线与合同

编码前交付：

- `00_IMPLEMENTATION_AUDIT.md`：真实 API、依赖、dirty 边界、性能和许可证；
- `TRANSCRIPTION_CONTRACT.md`：输入、stem 枚举、profile、输出 schema、错误码；
- `MIDI_CLEANUP_CONTRACT.md`：raw/clean 边界及每个清洗动作的可逆证据；
- `BENCHMARK_PLAN.md`：确定性合成夹具、允许使用的授权 fixture、指标与门槛；
- `STAGE_0_GATE.md`：逐项证明没有把启发式结果包装成 ground truth。

合同至少冻结：输出目录必须全新或显式允许续跑；源文件只读且哈希不变；
每轨保存 source hash、backend/model/version、profile、参数、运行时间、状态；
失败轨不得被静默丢弃；同名文件不覆盖；路径逃逸拒绝；raw MIDI 不修改；
stem 来源可为预分轨目录或可选 separator，二者必须明确区分。

## 5. Stage 1｜分轨感知转录

实现可替换组件，不把职责堆进 CLI：

1. `StemKind` 与严格 manifest；支持显式 `--stem kind=path` 和 manifest 输入。
2. profile registry：每类轨的音域、onset/frame、最短音符、弯音策略；参数及单位可见。
3. 复用 `TranscriptionBackend`；同一模型只加载一次，逐轨失败隔离。
4. 可选 separation adapter 只能调用已安装能力；未安装时给稳定错误/降级，
   不自动联网下载模型。Demucs `other` 不得伪称 piano/guitar ground truth。
5. 新 CLI 建议保持 `moodify transcribe-stems`；现有 `transcribe` 完全兼容。
6. 输出 `run_manifest.json`、每轨 raw MIDI、事件 CSV/JSON（可行时）、日志和哈希。

必须测试：各 stem profile、显式输入、缺失/重复 stem、非法 kind、路径逃逸、
后端缺失、单轨失败、Unicode 路径、空音频、已有输出、源哈希不变、模型复用。

## 6. Stage 2｜非破坏性 MIDI 清洗与多轨合并

清洗必须作为独立、可关闭、可比较的派生阶段：

1. 去除严格定义的重复/近重复 note event；不得仅因同音高重叠就盲删。
2. 最短音符过滤、音域裁剪/标记、同轨 voice limit；默认参数来自 profile。
3. 量化必须 `off` 默认，显式提供 grid/strength；保留原始 timing，报告位移统计。
4. 调性纠错必须 `off` 默认；只有显式 key/scale 才允许产生候选，保存原音、
   候选音、距离和规则；不得自动修改 pitch bend/滑音人声。
5. 合并为 Type 1 多轨 MIDI：稳定轨序、轨名、GM program/channel、统一 tempo/
   timebase；不得把鼓放到旋律声部。
6. 生成 raw-vs-clean diff：增删改数、timing/pitch displacement、警告和限制。

必须测试：确定性、幂等性、零强度量化等同 raw、非法 key、跨小节 note、
重叠弯音、多轨 channel/track 独立、空轨、合并后可重新解析。

## 7. Stage 3｜证据、性能与回归

1. 用程序生成的单音、音阶、和弦、贝斯、滑音及混合信号做端到端测试。
2. 分别报告 note precision/recall/F1、onset tolerance、octave error；没有标注的
   真实歌曲只能 smoke，不得报告准确率。
3. 冷/热启动与逐轨耗时、峰值内存；本机 8 GB 下不得并行加载多个模型。
4. 两个全新目录双运行；规范化 manifest、MIDI 事件和哈希应一致。
5. 运行新增测试、相关 Core 测试、CLI help/smoke、Ruff；记录未运行项。
6. 更新架构文档、`PROGRESS.md`、`VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、
   `HANDOFF.md`。

## 8. 验收和停止条件

P0 条件：源/raw MIDI 不变；无路径越界/覆盖；raw 与 clean 分离；旧 CLI 回归；
失败轨可见；多轨 MIDI 可解析；无伪造准确率或 stem 标签。任一 P0 失败即 HOLD。

以下情况立即停止：需要修改范围外文件、下载新模型/数据、真实歌曲被写入或
覆盖、site-packages 被修改、Stage 0 未 PASS 即编码、清洗默认改变音符、
Demucs `other` 被冒充确定乐器、测试依赖网络或随机外部状态。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。DeepSeek 不得
宣布最终 ACCEPT；完成 `HANDOFF.md` 后停止等待 Codex 独立验收。


# DSK-MFY-SCORE-ENGINE-009｜Moodify Score Engine 原点与 MuseScore Backend

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** DSK-MFY-STEM-MIDI-008 已形成可读 HANDOFF；若未完成则 HOLD  
**执行上限：** 6 小时，四阶段严格串行

## 1. 核心目标

Moodify 不开发另一个 MuseScore，也不把 `.mscz` 变成内部事实源。建立：

```text
MIDI / MusicXML
       ↓
MoodifyScore v0.1
       ↓
ScoreBackend
├── MuseScoreBackend   本任务实现
├── VerovioBackend     仅冻结能力位
├── LilyPondBackend    仅冻结能力位
└── OSMDBackend        仅冻结能力位
       ↓
MusicXML / PDF / SVG / PNG + evidence
```

“原点”是 Moodify 持有曲谱语义、来源、置信度、修订和后端证据；外部引擎
只承担成熟排版、渲染、播放或人工编辑能力。

## 2. 必读与基线

完整读取：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-SCORE-ENGINE-009\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SCORE-ENGINE-009\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SCORE-ENGINE-009\03_PRINCIPLE_SEED.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-STEM-MIDI-008\HANDOFF.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-STEM-MIDI-008\00_TASK_ORCHESTRATION.md
E:\moodify\docs\architecture\MSE_ARCHITECTURE.md
E:\moodify\docs\architecture\AUDIO_TO_MIDI.md
E:\moodify\tools\score_asset_pipeline.py
E:\moodify\moodify-core-package\pyproject.toml
E:\moodify\moodify-core-package\src\moodify\cli.py
```

检查适用 `AGENTS.md`、Git/dirty 状态、Python、MuseScore 可执行文件及版本、
现有 MIDI/MusicXML/PDF 产物。记录只读事实源 SHA-256。现有修改与未跟踪
文件属于用户，不得整理、覆盖、还原、暂存或提交。

## 3. 范围与许可证边界

允许修改：

```text
E:\moodify\moodify-core-package\src\moodify\score_engine\
E:\moodify\moodify-core-package\src\moodify\cli.py
E:\moodify\moodify-core-package\tests\score_engine\
E:\moodify\moodify-core-package\pyproject.toml（仅必要可选依赖/入口）
E:\moodify\docs\architecture\MSE_ARCHITECTURE.md
E:\moodify\docs\architecture\SCORE_ENGINE_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SCORE-ENGINE-009\
E:\moodify\outputs\deepseek_validation\DSK-MFY-SCORE-ENGINE-009\
```

禁止复制/修改 MuseScore 源码、site-packages、第三方模型、声音库和字体；
MuseScore 只作为独立外部进程，通过 MIDI/MusicXML/文件输出交换。Moodify
保持 Apache-2.0；MuseScore 的 GPLv3、版本和调用方式进入许可证清单。
禁止修改 Runtime/Bridge/DSP/MRS/008 实现和真实歌曲资产。禁止 Git 分支、
暂存、提交、推送及 reset/clean/stash/checkout。需新增依赖或越界时 HOLD。

## 4. Stage 0｜事实、合同和损失边界（60 分钟）

编码前交付：

- `00_IMPLEMENTATION_AUDIT.md`：现有曲谱链、MuseScore 探测、dirty/许可证；
- `MOODIFYSCORE_CONTRACT.md`：稳定 ID、版本、timeline、parts/staves/voices/events；
- `SCORE_BACKEND_CONTRACT.md`：capabilities/validate/export/inspect；
- `ROUNDTRIP_LOSS_CONTRACT.md`：哪些字段必须守恒、哪些允许告警损失；
- `STAGE_0_GATE.md`：合同冻结且 008 输入边界真实。

`MoodifyScore v0.1` 最少支持 metadata、source assets、tempo/time/key timeline、
part/instrument、staff/voice、measure、note/rest、lyrics reference、revision、
evidence。推断字段必须带 `source/status/confidence`；不得伪装人工确认。

## 5. Stage 1｜内部模型与 MusicXML（105 分钟）

1. 使用严格类型和版本化 schema；拒绝未知关键字段。
2. MIDI ingest 保存原始 tick/time、track/channel/program、tempo/time signature；
   无法可靠推断的 key/voice/measure 信息保持 unknown/warning。
3. 建立稳定 ID 和 canonical JSON；同输入双运行规范化一致。
4. MusicXML 4.x exporter 输出 partwise 总谱；支持 part、measure、voice、note、
   rest、duration、tie、tempo、time/key（存在时）和歌词引用（存在时）。
5. 不用 MusicXML 替代内部 evidence/revision/confidence；不覆盖输入 MIDI。

测试：单轨、多轨、tempo change、拍号变化、休止、和弦、跨小节/tie、Unicode、
空轨、非法 MIDI、未知字段、稳定序列化、源哈希不变。

## 6. Stage 2｜MuseScoreBackend 最小闭环（105 分钟）

1. `ScoreBackend` Protocol 与 `BackendCapabilities`；未实现后端只声明能力，
   不创建会误导用户的假实现。
2. MuseScore 探测显式路径/环境/PATH，记录版本；缺失时稳定 `UNAVAILABLE`。
3. 使用参数数组启动独立进程，禁止 shell 字符串拼接；超时、退出码、stdout/
   stderr、命令参数、版本和输出哈希进入 evidence。
4. 从 MoodifyScore 导出 MusicXML，再无界面生成 PDF 与 SVG；输出目录必须全新，
   禁止覆盖和路径逃逸。
5. 输出重新解析验证：至少比较 part、measure、note、pitch、duration、tempo；
   允许损失必须进入 `roundtrip_report.json`，不得用“成功导出”掩盖差异。
6. CLI 最小入口：`moodify score import-midi`、`score export`、`score backends`。

## 7. Stage 3｜验证、文档和继承（90 分钟）

1. 只使用程序生成合成 MIDI 或明确测试 fixture 做端到端；不处理真实歌曲。
2. 生成 canonical JSON、MusicXML、PDF、SVG、manifest、roundtrip report。
3. 两个全新目录双运行；规范化语义一致，非确定性 PDF 元数据单独说明。
4. 运行新增测试、相关 Core 回归、CLI help/smoke、Ruff；记录未运行项。
5. `BACKEND_CAPABILITY_MATRIX.md` 冻结 MuseScore/Verovio/LilyPond/OSMD 能力、
   格式、许可证和下一接入顺序，不在本任务实现后三者。
6. 更新架构、`PROGRESS.md`、`VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、
   `LICENSE_INTEGRATION_NOTE.md`、`HANDOFF.md`。

## 8. P0 门禁与停止条件

必须成立：内部模型不依赖 `.mscz`；源 MIDI 不变；外部进程隔离；无路径
越界/覆盖；缺失 MuseScore 可解释降级；MusicXML 可解析；round-trip 差异
可见；旧 CLI 不回归；许可证归属不混淆。

立即停止：008 无 HANDOFF、Stage 0 未 PASS 即编码、需要复制 MuseScore 源码、
需要安装/下载第三方组件、范围外写入、真实音乐被处理或覆盖、关键语义损失
被隐藏、为追求一致而修改原 MIDI、现有用户修改被还原。

最终状态只能为 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。DeepSeek 完成
HANDOFF 后停止，由 Codex 给出 `ACCEPT / REWORK / HOLD`。


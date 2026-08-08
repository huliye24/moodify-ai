# Moodify Score Engine Architecture

**Status:** v0.1 implemented (DSK-MFY-SCORE-ENGINE-009, 2026-08-02)

## 原点原则

Moodify 持有曲谱语义、来源、置信度、修订和后端证据；外部引擎只承担成熟
排版、渲染、播放或人工编辑能力。`.mscz` 不是内部事实源，MusicXML 也不
承载 Moodify 全部证据。

```text
MIDI / MusicXML
       ↓
MoodifyScore v0.1   ← 内部事实源（canonical JSON）
       ↓
ScoreBackend        ← 稳定适配层（Protocol + 能力位）
├── MuseScoreBackend   已实现（外部 GPLv3 进程）
├── VerovioBackend     能力位冻结
├── LilyPondBackend    能力位冻结
└── OSMDBackend        能力位冻结
       ↓
MusicXML / PDF / SVG / PNG + evidence
```

## 模块

| 模块 | 职责 |
|---|---|
| `score_engine/model.py` | MoodifyScore v0.1 严格类型模型（SCHEMA_VERSION `moodifyscore/0.1`） |
| `score_engine/midi_ingest.py` | SMF 0/1 解析：raw tick、track/channel/program、tempo/拍号/调号；measure 推断（有时间签名时，status=inferred）；源 SHA-256 |
| `score_engine/serialization.py` | canonical JSON（键排序、无时间戳/绝对路径、稳定 ID、未知键拒绝） |
| `score_engine/musicxml_exporter.py` | MusicXML 4.0 partwise 导出：part/measure/voice/note/rest/duration/tie/tempo/time/key |
| `score_engine/backend.py` | ScoreBackend Protocol、BackendCapabilities、注册表、BackendInfo |
| `score_engine/musescore_backend.py` | 探测（显式路径 > `MUSESCORE_BIN` > 默认候选 > PATH）、argv 数组进程、超时/退出码/哈希 evidence、PDF/SVG |
| `score_engine/roundtrip.py` | MusicXML 重解析 + part/measure/note/pitch/duration/tempo 对比 → `roundtrip_report.json` |
| `score_engine/cli.py` | `moodify score import-midi / export / backends` |

## 数据流（export 全链路）

```text
source.mid ──ingest──> MoodifyScore ──dumps──> score.json (canonical)
                          │
                          └──export_musicxml──> score.musicxml
                                                     │
                                      MuseScore4.exe -o out.pdf  (独立进程)
                                      MuseScore4.exe -o out.svg
                                                     │
                          └──重解析──> roundtrip_report.json (verdict PASS/WARNINGS/FAIL)
```

## 关键决策

1. **严格分层**：原始演奏事实（tick/pitch）→ 曲谱解释（measure 推断）→ 视觉排版（后端），三层分离保存。
2. **推断不冒充事实**：`status = raw | inferred | confirmed`；无人工输入时永远不出现 `confirmed`。
3. **进程隔离**：MuseScore 只通过 argv 数组调用；不复制/修改其源码、site-packages、声音库、字体。
4. **输出隔离**：输出目录必须全新/为空；拒绝覆盖与路径逃逸；源 MIDI 只读且哈希入 evidence。
5. **确定性**：canonical JSON 双运行字节一致；`score_id` 由内容派生（SHA-256 前 16 hex）。
6. **round-trip 可见性**：关键字段损失必须写入报告并影响 verdict，禁止"成功导出"掩盖差异。

## 限制（G-Boundary）

- 无真实歌曲 ground truth；准确率声明禁止，直到独立 benchmark 任务提供证据。
- 无调号推断：MIDI 无调号事件时 `key_known=false`，MusicXML 不输出 key。
- 无 voice 划分启发式：每 part 单 voice；多 voice 是后续工作。
- 无 `.mscz` 往返、无人工编辑、无音频播放。
- 8 GB 约束：无并行 MuseScore 进程。

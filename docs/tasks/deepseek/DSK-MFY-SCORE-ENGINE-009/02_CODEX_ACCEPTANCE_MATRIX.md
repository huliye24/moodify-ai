# DSK-MFY-SCORE-ENGINE-009｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 008 HANDOFF 存在且依赖边界明确 | HOLD |
| Q0-02 | P0 | 编码前冻结内部模型、后端与损失合同 | HOLD |
| Q0-03 | P0 | dirty/只读哈希和许可证边界被记录 | HOLD |
| Q1-01 | P0 | MoodifyScore 不依赖 `.mscz` 或具体渲染器 | HOLD |
| Q1-02 | P0 | 原始 tick/source/status/confidence 可追溯 | HOLD |
| Q1-03 | P0 | MusicXML 可解析且不覆盖源 MIDI | HOLD |
| Q1-04 | P1 | 多轨、tempo/time、rest/tie/Unicode 被测试 | REWORK |
| Q1-05 | P1 | canonical JSON 双运行语义一致 | REWORK |
| Q2-01 | P0 | MuseScore 仅通过安全独立进程调用 | HOLD |
| Q2-02 | P0 | 输出隔离，无覆盖、越界或命令注入 | HOLD |
| Q2-03 | P0 | 缺失/失败/超时均可见且无伪成功 | HOLD |
| Q2-04 | P0 | round-trip 关键语义差异没有被隐藏 | HOLD |
| Q2-05 | P1 | PDF/SVG/MusicXML/manifest 证据完整 | REWORK |
| Q2-06 | P1 | 旧 CLI 与既有转录测试无回归 | REWORK |
| Q3-01 | P0 | 未实现后端没有伪装成可用能力 | HOLD |
| Q3-02 | P0 | Apache/GPL 归属和分发边界没有混淆 | HOLD |
| Q3-03 | P1 | 合成 E2E、双运行、失败矩阵可复现 | REWORK |
| Q3-04 | P1 | 能力矩阵与第二后端路线清晰 | REWORK |
| Q3-05 | P1 | 测试、CLI smoke、Ruff 和文档通过 | REWORK |

Codex 将独立执行：非法/损坏 MIDI、Unicode、tempo/time 变化、输出已存在、
伪 MuseScore 路径、超时、失败退出码、路径逃逸、命令参数注入、round-trip
篡改、双运行、源哈希、许可证清单和旧 CLI 回归。


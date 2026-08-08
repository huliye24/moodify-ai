# DSK-MFY-SCORE-ENGINE-009｜许可证集成说明

**日期：** 2026-08-02 UTC

## 1. 归属边界（不混淆）

| 组件 | 许可证 | 说明 |
|---|---|---|
| Moodify 包（`moodify-core-package`） | Apache-2.0 | 本项目代码保持 Apache-2.0 |
| MuseScore 4.5.1（`C:\Program Files\MuseScore 4\bin\MuseScore4.exe`） | GPLv3 | **外部独立程序**；本任务不复制其源码、site-packages、声音库、字体，不修改其安装 |
| 本任务生成的 canonical JSON / MusicXML / PDF / SVG / manifest | Apache-2.0（Moodify 产物） | 由 Moodify 代码生成；PDF/SVG 是渲染产物 |
| Verovio / LilyPond / OSMD | LGPL-3.0 / GPL-3.0 / MIT | 本任务未调用，仅能力位声明 |

## 2. 调用方式（GPL 边界）

- MuseScore 只通过参数数组独立进程调用（`MuseScore4.exe -o out in.musicxml`）。
- Moodify 与 MuseScore 以进程边界交换文件（MIDI/MusicXML 输入、PDF/SVG 输出），
  无链接、无嵌入、无源码派生——保持 Apache-2.0 与 GPLv3 的进程隔离。
- 未引入新的第三方 Python 依赖；`pyproject.toml` 未修改（无需新依赖）。

## 3. 分发边界

- 仓库不包含 MuseScore 二进制、其源码或模型。
- 若未来打包分发需要 MuseScore 支持，必须让用户自行安装（独立 GPLv3 程序），
  不得捆绑 GPL 程序进入 Apache-2.0 发行物，除非经过专门的法务评审。

## 4. 版本记录

- MuseScore: `MuseScore4 4.5.1`（`--version` 输出，探测记录于 export evidence）。

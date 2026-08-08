# Backend Capability Matrix（Stage 3 冻结）

**冻结日期：** 2026-08-02  
**范围：** 本任务只实现 MuseScoreBackend；Verovio/LilyPond/OSMD 只冻结能力位，不实现。

| 后端 | 状态 | MusicXML 导入 | PDF | SVG | PNG | 音频 | 人工编辑 | 许可证 | 接入顺序 |
|---|---|---|---|---|---|---|---|---|---|
| MuseScore | ✅ 已实现 (4.5.1) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | GPLv3（外部进程） | 当前 |
| Verovio | 能力位 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | LGPL-3.0 | 2（轻量 SVG 渲染） |
| LilyPond | 能力位 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | GPL-3.0 | 3（高质量排版） |
| OSMD | 能力位 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | MIT | 4（网页交互） |

## 接入规则

1. 未实现后端 `available()` 恒为 `False`，CLI 显示 `capability-bit only`，**不得创建可调用但误导用户的假实现**。
2. 接入新后端必须：实现 `ScoreBackend` Protocol → 测试探测/导出/失败 → 更新本矩阵 → Codex 验收。
3. 本任务不实现可视化编辑器、不重新实现排版算法。

## 实际探测结果（2026-08-02）

```text
musescore    available            GPLv3 (external process) vMuseScore4 4.5.1
verovio      capability-bit only  LGPL-3.0
lilypond     capability-bit only  GPL-3.0
osmd         capability-bit only  MIT
```

- MuseScore 路径：`C:\Program Files\MuseScore 4\bin\MuseScore4.exe`
- 调用方式：`MuseScore4.exe -o <out> <in.musicxml>`（argv 数组，无 shell 拼接；一次一个 `-o`）
- 多页 SVG 输出自动带页码后缀（如 `score-1.svg`），已按 glob 收集。

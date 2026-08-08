# DSK-MFY-SCORE-ENGINE-009｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | 测试 | fixture builder 生成重复 MThd header | `TrackBuilder.build()` 自己拼 header 且 `build_midi()` 又拼一遍 | 拆分：`build()` 只返回 MTrk，`build_midi()` 统一 header；40 项 ingest/serialization 测试从失败转通过 |
| 2 | 测试 | `NoteOn` 无 `tick_start` 属性 | 字段名不一致（`tick` vs `tick_start`） | 统一使用 `note.tick`；删除残留 `tick_end` 引用修正 |
| 3 | Stage 2 | 真实 MuseScore 导出 exit != 0 | MuseScore 4.5.1 不支持 `-I musicxml` 参数；且一次只接受一个 `-o` | 去掉 `-I`；PDF 与 SVG 分两次 argv 调用 |
| 4 | Stage 2 | SVG 产物未被收集 | MuseScore 多页 SVG 自动加页码后缀（`score-1.svg`） | 收集时 glob `stem-*.svg` |
| 5 | 测试 | roundtrip `FileExistsError` | `build_roundtrip_report` 重复导出已存在的 MusicXML | 改为只重解析既有文件；该文件由 backend 导出产生 |
| 6 | 测试 | `MoodifyScore` 无 `staves` 属性 | `_compare` 传错对象（score 而非 part） | `_part_note_summary(part)` 在循环中逐 part 调用 |
| 7 | 测试 | 伪路径测试仍可用 | 显式路径失败后回退到默认候选探测到真实 MuseScore | 测试中 mock `DEFAULT_CANDIDATES=()` 与 `shutil.which=None` |
| 8 | 测试 | tempo 断言 140.00014000014 != 140.0 | MIDI tempo 以整数 micros/beat 存储，140 BPM 有 1e-4 级固有精度差 | 断言用 `pytest.approx(rel=1e-4)`；保留原始值不四舍五入 |
| 9 | 验证 | round-trip 把"守恒"误报为 WARNING | `_compare` 将 preserved 状态也 append 进 warnings | 守恒只反映在 comparison 字段；warnings 只留真实允许损失；round-trip 输出 PASS |
| 10 | 验证 | 重跑 stage3_e2e 双运行失败 | 脚本输出目录复用已非空的 run_1/run_2（backend 按合同正确拒绝） | 脚本非幂等是验证脚本问题，非产品缺陷；重跑前清理自身验证产物即可。产品行为正确：非空输出目录拒绝有测试 |

## 未复现/边界

- SMPTE division MIDI 明确不支持（返回 MidiParseError）——不是隐藏失败，是能力边界。
- 未发生：源 MIDI 被修改、路径逃逸、输出覆盖、shell 注入（全部有防护并有测试）。

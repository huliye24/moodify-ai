# Moodify 明日任务编排｜2026-08-02

## 1. 明日主线

明日新增正式跃迁任务：

> `DSK-MFY-SCORE-ENGINE-009｜Moodify Score Engine 原点与 MuseScore Backend`

但必须保持串行依赖：008 未交付可读 HANDOFF，009 不启动编码。原周计划的
内部盲听、WSE-01 和 MSE-01 不删除；009 吸收 MSE-01 的“曲谱资产映射”目标，
盲听/WSE 若与工程窗口冲突则顺延并记录，不用隐性并行制造完成假象。

## 2. 严格执行顺序

### Gate A｜恢复上下文与 008 状态（30 分钟）

1. 检查 008 `PROGRESS.md`、`HANDOFF.md`、dirty diff 和测试结果。
2. 若 008 未完成：继续 008，009 状态 HOLD/PENDING，不并行修改共享 CLI/pyproject。
3. 若 008 为 READY_FOR_CODEX_REVIEW：先由 Codex 独立验收关键 P0。
4. 只有 008 ACCEPT，或 Codex 明确批准“接口稳定、可开始 009”，才开放 Gate B。

### Gate B｜009 Stage 0（60 分钟）

冻结 MoodifyScore、ScoreBackend、round-trip 损失和许可证合同。只形成事实与
合同，不先写实现。Stage 0 未 PASS，当天停止在 HOLD/REWORK。

### Gate C｜009 最小垂直闭环（150 分钟）

按顺序实现：

```text
合成多轨 MIDI
  -> MoodifyScore canonical JSON
  -> MusicXML
  -> MuseScoreBackend
  -> PDF + SVG
  -> roundtrip_report + manifest
```

优先级顺序：内部模型 > MusicXML 可解析 > MuseScore 安全调用 > PDF/SVG；
若时间不足，宁可保留明确未完成项，也不创建假后端或隐藏语义损失。

### Gate D｜验证与封口（60 分钟）

1. 新增测试、相关回归、CLI help/smoke、Ruff。
2. 源 MIDI 哈希复核、输出隔离、失败注入和许可证清单。
3. 更新 PROGRESS/VALIDATION/HANDOFF。
4. DeepSeek 停在 READY_FOR_CODEX_REVIEW；Codex 再独立验收。

## 3. 明日资源冲突规则

- 008 与 009 都可能修改 `moodify.cli`、`pyproject.toml`，严禁并行执行。
- MuseScore 只调用本机已安装版本；不联网下载、不修改第三方程序。
- 明日不接 Verovio/LilyPond/OSMD，它们只进入能力矩阵和后续队列。
- 明日不开发可视化编辑器，不处理真实歌曲，不重新实现排版算法。
- 原计划盲听属于独立生产验证线；没有额外时间则顺延，不与工程任务混跑。

## 4. 明日完成定义

最低完成：Stage 0 合同 PASS，内部模型和后端接口可被独立审查。  
目标完成：合成 MIDI 到 PDF/SVG 的最小闭环通过，round-trip 差异可见。  
禁止宣称：完整替代 MuseScore、专业出版质量已经验证、四后端已经完成。

任务入口：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-SCORE-ENGINE-009\01_DEEPSEEK_EXECUTION_COMMAND.txt
```


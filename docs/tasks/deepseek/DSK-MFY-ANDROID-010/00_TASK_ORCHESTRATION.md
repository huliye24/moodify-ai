# DSK-MFY-ANDROID-010｜本地音频试听与 A/B 比较

**计划日期：** 2026-08-02  
**目标完成日期：** 2026-08-02  
**依赖：** ANDROID-009 ACCEPT  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**执行时限：** 120 分钟  
**任务状态：** PLANNED

## 1. 目标

005 只做了 A/B 结构占位。本包让用户在手机上真正试听原始/处理版本并做选择：这是"艺术判断"在移动端的落点——App 提供判断工具，但**最终决定权属于人**（ADR-001：Moodify 不是自动混音，人工保留最终责任）。

## 2. 当前基线

- 009 已交付作品库：本地持久化 + 同步地基；
- 处理版本 WAV 已存 App 沙箱（007 起），但无播放器；
- A/B 页为占位结构。

## 3. 允许范围

```text
apps/android/app/src/main/
apps/android/app/src/test/
apps/android/app/src/androidTest/
apps/android/docs/
docs/tasks/deepseek/DSK-MFY-ANDROID-010/
outputs/deepseek_validation/DSK-MFY-ANDROID-010/
```

禁止：修改电脑端代码、引入重型播放引擎（Media3 若已在依赖中可用）、
自动评分替代人工判断、Git 危险操作。

## 4. 执行阶段

### Stage A｜播放器

- 使用 Media3 ExoPlayer（若已在依赖中）或系统 MediaPlayer；
- 支持本地沙箱文件播放、暂停、seek、播放完成回调；
- 播放状态（Playing/Paused/Completed/Error）进入 UiState。

### Stage B｜A/B 试听页

- 同一作品原始 vs 处理版本并排切换试听；
- 支持"盲试听"模式（隐藏标签，试听后才揭晓，对齐 ADR-004 证据原则）；
- 播放位置同步：切换版本时保持时间位置（能力允许时）；
- 记录试听动作（时长、切换次数）为审计事件，不采集个人行为细节。

### Stage C｜版本决策

- 用户可对每个版本选择"保留/淘汰/待定"；
- 决策写入作品库 version record（带 decision + reason + timestamp）；
- 决策不自动同步为最终交付：标记 PENDING_SYNC，等待电脑端确认；
- 无决策分数自动化：不显示"AI 认为哪个更好"。

### Stage D｜真机验证

- 原始/处理双版本试听、盲听模式、决策写入在真机跑通；
- 播放失败、文件缺失、沙箱清理三个场景有明确 UiState；
- 001-009 门禁全绿。

## 5. P0 门槛

- 双版本本地试听流畅（无 ANR/卡顿）；
- 盲听模式真实隐藏标签；
- 决策写入作品库且带时间戳，无自动最终化；
- 播放错误可审计（不静默）；
- 前序门禁全绿；交付四件套。

## 6. 停止条件

若需要引入重型依赖、需修改电脑端决策模型、或超时，HOLD + SCOPE_CHANGE_REQUEST.md。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

# 干预实验室（DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001）

## 定义

干预实验室是 Moodify 对既有处理能力的**重新定位**：EQ、压缩、限幅、
去噪、立体声处理、相位修复、音色平衡、瞬态工作、插件链、Audacity
操作、既有 DSP 路径、候选生成。

这些能力**不是**产品身份的权威来源——它们是用于检验假设、产生候选、
生成可对比证据的受控干预手段。

## 干预记录

每次干预写入 `InterventionRecord`：

- intervention_id / case_id / candidate_id
- parent_audio_sha256 / output_audio_sha256
- producing_application / version / execution_mode
- operator / hypothesis / intended_goals / operations / guardrails
- started_at / completed_at / status / evidence_refs

执行模式：EXTERNAL_GUI_PROCESSING、MOODIFY_DSP、SCRIPTED_TOOL、
MANUAL_ENGINEER、UNKNOWN_LEGACY。

**Audacity 的 GUI 处理可被表示**，无需宏、无需 CLI 自动化。

## 候选

候选注册包含 case_id、candidate_id、路径、SHA-256、产生应用、
处理方式、笔记与父源哈希。接受与拒绝候选都按策略保留为学习证据。

## 边界

- 本任务不自动化 Audacity、不要求宏、不成为 DAW；
- 不删除处理模块（只重分类，不迁移无兼容导入）；
- 干预失败/过度处理是合法结果，不是流程错误。

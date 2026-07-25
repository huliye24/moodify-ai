# Moodify v2 黄金验收样本 WSA_20260724_001

## 登记结论

当前两轨歌曲已登记为 Moodify Studio Workspace v2 的第一个端到端黄金路径样本。

- 样本 ID：`WSA_20260724_001`
- 类型：人声 + 伴奏两轨
- 用途：本地产品开发与 MVP 端到端验收
- 机器清单：`data/workspace_v2/acceptance_samples/WSA_20260724_001.json`
- 注册表：`data/workspace_v2/acceptance_samples/registry.jsonl`

## 固定输入

输入根目录：

`pre-music/2026-07-24_1441_split_by_lalalai`

固定输入包括：

1. `Japprends à te recevoir maladroitement_no_vocals_split_by_lalalai.wav`
2. `Japprends à te recevoir maladroitement_vocals_split_by_lalalai.wav`

两轨均为 48 kHz、双声道、16-bit、131.48 秒。清单内保存文件长度和 SHA-256，用于判断素材是否被替换或损坏。

## 基线产物

基线目录：

`pre-music/2026-07-24_1441_split_by_lalalai/moodify_post_v1`

已知基线：

- 伴奏 `clean_master`：质量门通过。
- 人声 `warm_vocal`：需要复核，存在动态损失风险。
- 最终交付：`-14.0 LUFS`、LRA `6.2 LU`、True Peak `-3.1 dBFS`。
- 完整 MRS 引擎当时不可用，使用 `mrs_proxy_v01`。
- `moodify_post_v1/vocals` 是早期误匹配产物，不得用于验收；正确路径为 `vocals_corrected`。

## MVP 验收目标

该样本用于证明系统能够：

1. 创建长期 AudioProject 并登记两个原始资产。
2. 保存 Creative Brief。
3. 持久化 Producer、Analyst、Designer、Worker、Judge、Archive 六类线程结果。
4. 产生至少两个具有父子血缘的候选版本。
5. 对版本执行技术质量审查，并明确披露评分降级。
6. 阻止 Judge 拒绝的版本成为 Final。
7. 只有存在人工 ApprovalDecision 时才允许 Final。
8. 归档原始资产引用、方案、参数、版本、审查、审批和最终音频。

## 使用规则

- 不把音频复制进测试代码目录，避免重复占用空间。
- 自动测试使用相对路径和 SHA-256 校验输入完整性。
- 历史音频不可覆盖；每次处理产生新版本路径。
- 该样本只代表首个黄金路径，不代表所有流派和人声类型。
- 未确认对外发布权利前，不允许把素材上传或公开分发。

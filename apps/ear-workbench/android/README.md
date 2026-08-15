# Moodify Ear — Android 内部代码（不公开）

归档自公开 app `apps/android`（2026-08-15，MFY-PLAYER-UNIFY-001）。

**性质**：Moodify Ear 后处理/创作模块的 Android 侧代码。Ear 是内部工具，
不公开、不构建、不进入任何公开发布产物。

**内容**：

- `data/` — DemoProcessRepository（后处理管线仓库）、WorkLibrary（处理产物本地库）
- `ui/screens/` — Upload→Processing 管线、Works 作品库、发布、版权中心、协作中心、
  创作者中心、数据中心、通知中心、作品详情（A/B 处理前后对比）
- `res/raw/` — case_*.wav 演示音频（Ear 案例）
- `res/drawable/` — report_*.png 后处理报告图

**公开 app（Moodify）不含任何以上模块**。如需恢复，需重新评估归属。

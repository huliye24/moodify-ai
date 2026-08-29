# 06 — Conflicts / Unknowns / Blockers

## Authority Conflicts（权威冲突）

| # | 冲突 | 双方 | 证据 | 裁决权 |
|---|---|---|---|---|
| C1 | 产品身份 | GitHub main：The Ear of AI（产品身份） vs 本地宪法 v1.0：Reconstruction-first（Ear 内部化，Supersedes 旧表述） | git show origin/main:README.md；docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md Article I | W01-P01 |
| C2 | 仓库权威 | main（fa88b0b9，2026-08-08 冻结） vs 本地分支 154 未合并 commits（重建系列全部） | git rev-list origin/main..HEAD | W01-P01 |
| C3 | PR #21 定位 | 冻结协议：KEEP（canonical release carrier） vs 现实：OPEN DRAFT 未合并 + 与重建方向关系未定 | docs/PR_DISPOSITION.md；gh pr view 21 | W01-P01 |
| C4 | 状态文档 vs 代码 | REPOSITORY_STATUS.md（Ear of AI / 0b355e7） vs 当前 HEAD（reconstruction-first / 98f7b96e） | docs/REPOSITORY_STATUS.md；git log | W01-P01 |
| C5 | 内部状态机权威 | orchestration/（LEGACY）、node/（24x7）、data_factory/、reconstruction_factory/ 多套并存 | src 目录；REPOSITORY_STATUS.md | W01-P01（或后续） |
| C6 | 外部能力名实 | 「Moodify Cloud」名义（云系统） vs 实际（2 VPS + 静态站 + API 壳 + 批处理） | 黑箱调查 §34；本扫描 03 报告 | W01-P01 |

## Runtime Conflicts（运行时冲突）

- R1：CI 内 Temporal Texture Guard 持续 failure 而同一 PR 的 CI 全绿 —— 两个 workflow 对「同一代码是否健康」给出相反结论。
- R2：Deploy workflow 在 tag v1.0.0-data-foundation 上 failure，但该 tag 未用于任何线上发布（云端为 tar 手工发布）—— CI 部署通道与真实部署通道脱节。
- R3：云端部署非 git（时间戳 tar），无法验证与任何 commit 的一致性；「代码存在」与「云端运行」的映射关系只能推断。

## Data Authority Conflicts（数据权威冲突）

- D1：PolarDB（moodify_dev 19 表）vs SQLite（node.sqlite3 队列 + data_node 状态）：任务状态/队列仍以 SQLite 为实，业务 schema 在 PolarDB，两者无同步协议证据。
- D2：无统一音频 track identity：pre-music（本地曲目）、music-media（LA 播放库）、杭州 /var/lib/moodify（处理产物）三处无共享 hash 注册表（golden case 除外）。
- D3：lalalai 分轨多次重试产生同曲多版本 zip，无版本权威标记（重复资产风险）。

## Unknowns（无法确认项，全部显式 UNKNOWN）

1. PolarDB 三实例当前内容（直接核验被凭据阻塞；表/行数来自同日黑箱调查声称）。
2. 云端部署代码与仓库 commit 的精确对应关系。
3. LA moodify-music（vinext node 平台）与 music-bff 的代码来源与版本（仓库中无直接对应构建源）。
4. music-web / music-android / music-package 与线上服务的完整对应（哪些功能已在生产）。
5. 全库真实歌曲唯一总数（各音乐目录重叠情况）。
6. 07Music / music / local_audio_assets 的授权状态与播放库角色。
7. 历史补丁包 04-15、16-26、43-65 各壳对应实现的确切 commit。
8. OSS 是否已由用户手动开通（本扫描未发现任何 bucket 或凭据引用）。
9. 云端 journald 中是否有隐藏故障（未深扫日志内容）。
10. listening_test 34 文件的聆听结果（DATA_PENDING）。

## Blockers（按任务书 Stop Condition 标记）

| 项 | 阻塞原因 | 需要什么 |
|---|---|---|
| B1 PolarDB 直接只读核验 | 凭据不符（root 密码拒绝；无 polardb_admin.env 于 LA/杭州可访问路径） | 有效只读 DB 账号或授权凭据（W01-P03 前置） |
| B2 腾讯云节点扫描 | 节点已删除（2026-08-12）→ 不再适用 | 无（OBSOLETE） |
| B3 GitHub Actions 历史日志深读 | 未超出只读范围，但本次未展开 | 如需可后续单独拉取 |
| B4 云端部署对齐 | 部署为非 git 结构 | W01-P02（拓扑与角色）范围 |
| B5 全量测试重跑 | 本地 8GB 机器耗时；本扫描只读不运行 | 各包 TEST_RESULTS + CI 历史已作为证据 |

## 交接给 W01-P01 的唯一问题

> 「这是 Moodify 现在真实存在的系统。哪些现实应该被保留为 Canon，哪些应该降级、迁移、废弃或重新解释？」

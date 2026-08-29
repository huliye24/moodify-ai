# 08 — Evidence Index

> 本包所有重要结论的证据路径。优先级遵循任务书 §6（运行时 > 可重现测试/CI > 部署身份 > GitHub > canonical docs > 完成报告 > 任务书 > 对话推测）。

| # | Evidence ID | 支持的主张 | 来源 | 时间戳 | 置信度 |
|---|---|---|---|---|---|
| E01 | git-revparse-origin-main | main=fa88b0b9 | `git rev-parse origin/main` | 2026-08-17 19:46 | HIGH |
| E02 | git-revparse-HEAD | 本地 HEAD=98f7b96e，领先 154 commits | `git rev-list --count origin/main..HEAD` | 2026-08-17 19:46 | HIGH |
| E03 | git-show-origin-main-README | main 身份=The Ear of AI | `git show origin/main:README.md` | 2026-08-17 19:47 | HIGH |
| E04 | git-show-origin-main-AGENTS | main AGENTS 身份=Ear of AI | `git show origin/main:AGENTS.md` | 2026-08-17 19:47 | HIGH |
| E05 | worktree-README-AGENTS | 本地身份=reconstruction-first | 工作树 README.md / AGENTS.md | 2026-08-17 19:47 | HIGH |
| E06 | constitution-v1.0 | 宪法 Supersedes 旧身份 | docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md | 2026-08-17 19:48 | HIGH |
| E07 | gh-pr-list | 仅 #21 open（DRAFT）；#15-20 closed 处置 | `gh pr list --repo huliye24/moodify-ai` | 2026-08-17 19:49 | HIGH |
| E08 | gh-pr-view-21 | #21 head=e66cbf9d，511 文件，26 commits | `gh pr view 21` | 2026-08-17 19:49 | HIGH |
| E09 | gh-run-list | PR#21 CI success / TT Guard failure / Deploy failure | `gh run list` | 2026-08-17 19:49 | HIGH |
| E10 | git-branch-a | 远端 16 分支 + 本地 40+ 分支清单 | `git branch -a` / `gh api branches` | 2026-08-17 19:46 | HIGH |
| E11 | repo-status-doc | REPOSITORY_STATUS.md 落后（0b355e7/Ear of AI） | docs/REPOSITORY_STATUS.md | 2026-08-17 19:50 | HIGH |
| E12 | pr-disposition | #21 KEEP 协议 | docs/PR_DISPOSITION.md | 2026-08-17 19:55 | HIGH |
| E13 | raw_scan_LA | LA 节点全量只读扫描 | 审查包/W01-P00_REPORTS_2026-08-17/raw_scan/LA_103_144_246_242_scan.txt | 2026-08-17 19:52 | HIGH |
| E14 | raw_scan_HZ | 杭州节点全量只读扫描 | 审查包/W01-P00_REPORTS_2026-08-17/raw_scan/HZ_120_55_191_146_scan.txt | 2026-08-17 19:54 | HIGH |
| E15 | ssh-la-deep | LA service 定义/timers/部署非 git | `systemctl cat` / `git rev-parse`（NOGIT） | 2026-08-17 19:56 | HIGH |
| E16 | ssh-hz-deep | 杭州 service 定义/env 名/API health | `systemctl cat` / curl /health | 2026-08-17 19:57 | HIGH |
| E17 | polardb-access-denied | PolarDB 直接核验 BLOCKED | mysql SHOW DATABASES → Access denied | 2026-08-17 19:59 | HIGH |
| E18 | cloud-state-json | 黑箱调查（同日 11:00 扫描）：PolarDB 3 实例/moodify_dev 19 表/OSS 无/无 AI 推理 | MOODIFY_CLOUD_CURRENT_STATE_2026-08-17.json/.md | 2026-08-17 11:00 | MEDIUM |
| E19 | fs-audio-count | 音频资产统计（~790 文件 ~17GB） | `find`/`du` 各目录 | 2026-08-17 20:05 | HIGH |
| E20 | fs-premusic | 真实曲目 ~7 首 + lalalai split | pre-music/ 目录 | 2026-08-17 20:06 | HIGH |
| E21 | fs-outputs | data_factory 4 case + pairwise + CAD/calib | outputs/ 目录 | 2026-08-17 20:07 | HIGH |
| E22 | golden-run-out | golden_record/source_manifest/blind_mapping | moodify-core-package/golden_run_out/ | 2026-08-17 20:08 | HIGH |
| E23 | artifacts-scan | artifacts 59 子目录证据状态 | Explore agent 扫描 | 2026-08-17 20:00 | HIGH |
| E24 | patchpack-scan | 补丁包 01-73 交付状态 | Explore agent 扫描 | 2026-08-17 20:00 | MEDIUM |
| E25 | test-file-count | core 81 / music 18 / root 3 test 文件 | `find tests` | 2026-08-17 20:10 | HIGH |
| E26 | releases-list | 5 个 APK 发布（2.0.1 缺 manifest） | deliverables/releases/ | 2026-08-17 20:03 | HIGH |
| E27 | truth-schema-check | Truth Table CSV 51 行过 schema 校验 | python schema 校验 | 2026-08-17 20:16 | HIGH |

## 主要报告 → 证据映射

| 报告章节 | 关键证据 |
|---|---|
| 00 §1 主链 | E13/E14/E16/E18 |
| 00 §3 冲突 C1-C5 | E03-E06/E08/E11/E12 |
| 01 Main/PR/CI | E01-E04/E07-E10 |
| 02 任务状态 | E23-E25（+ git log 各 commit） |
| 03 云节点 | E13-E18 |
| 04 数据/外部能力 | E19-E22/E26 |
| 05 Truth Table | E01-E26（逐行引用） |
| 06 冲突/未知/阻塞 | E08/E11/E12/E17/E18 |

## 未使用的可信来源说明

- 全量 pytest 未在本扫描运行（只读、8GB 机器耗时）；测试证据以各补丁包 TEST_RESULTS（E23）+ CI 历史（E09）为准。
- 云端 journald 内容未深扫（E13/E14 未含日志细节）。
- PolarDB 内容（E18）置信度 MEDIUM：同日独立会话声称，本包未能直接复核（E17）。

# 01 — GitHub / Repository Reality

**扫描时间：** 2026-08-17 19:45–20:00 CST
**来源：** 本地 git（E:\moodify）+ GitHub API（gh CLI，huliye24 已认证）+ 只读远端读取

---

## Main

| 项 | 值 | 证据 |
|---|---|---|
| GitHub main HEAD | `fa88b0b9c41df5a57a3683712a7df4e2341d8ca5`（2026-08-08） | `git rev-parse origin/main`，与任务包锚点一致 |
| 本地 main | `0b355e77`（落后 origin/main 2 commits，PR #16/#17 未在本地 main） | `git log main..origin/main` |
| 本地 HEAD（工作分支） | `98f7b96e`（`codex/moodify-classic-reconstruction-001`，领先 origin/main 154 commits） | `git rev-list --count origin/main..HEAD` |
| Canonical identity（main） | **The Ear of AI — an Auditory Intelligence System**（产品身份） | `git show origin/main:README.md`、`git show origin/main:AGENTS.md` |
| Canonical identity（本地 HEAD） | **Reconstruction-first listening environment**（Choose→Reconstruct→Play）；Ear 为内部智力层 | 当前工作树 README.md / AGENTS.md / docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md v1.0 |
| Core package | `moodify-core-package/`（src/moodify 70+ 模块，src/moodify_experimental） | 工作树 |
| Android | `apps/android`（Ear 工作台）+ `apps/music-android`（Moodify Music 3.1） | 工作树；deliverables/releases 有 APK |
| Cloud/runtime | `ops/`、`moodify-core-package/deploy|ops`、`cloud_status.py`、`dashboard.html` | 工作树 |
| State machine authority | **多候选并存**：`orchestration/`（LEGACY 声明）、`node/`（24x7 队列 worker）、`data_factory/`（pipeline）、`reconstruction_factory/`（重建批处理）。REPOSITORY_STATUS.md 声明 v01_pipeline 为 supported mainline；docs 与代码存在多个 state machine 定义 | REPOSITORY_STATUS.md；src 目录 |
| API authority | `moodify.api`（FastAPI，本地 src/api）+ `apps/music-web`（Cloudflare）+ music BFF（moodify-music-package） | 工作树 + 云端扫描 |

## Open PRs

| PR | Branch | Head | Key capabilities | Merge status | Runtime evidence | Conflict |
|---|---|---|---|---|---|---|
| #21 (DRAFT) | codex/mfy-data-factory-001 | e66cbf9d | Phase-I data factory、serial Aliyun worker、Android changes、restart recovery、rejected-case evidence、visualization dependency（+56329/-320，511 文件，26 commits） | OPEN / DRAFT，未合并 | 数据工厂逻辑已在杭州 worker 运行（v01 管线）；PR 内 Temporal Texture Guard 持续 failure | 冻结协议裁定 KEEP（PR_DISPOSITION.md）；与 reconstruction-first 方向关系未裁决 |
| #20/#19/#18/#15/#13/#9 | 各分支 | — | 1.0 RC 收敛 / Ear 统一 / contracts / 云主线 / license / key 清理 | CLOSED（处置见 PR_DISPOSITION.md：superseded 或提取完成） | — | 已按协议处置，分支保留为 archive |

**合并历史（main 上最近）：** #17（PR15 资产提取）、#16（Ear of AI 重建）、#14（GPL-3.0）、#11（key 清理）、#10、#8–#1（历史功能）。

## Branch Reality（远端 16 个分支）

| Branch | Last commit | 用途 | Merged? | Deployed? | Canonical relevance |
|---|---|---|---|---|---|
| main | fa88b0b9 | canonical | — | 云端非 git 部署（无对应关系） | CURRENT（历史权威） |
| codex/mfy-data-factory-001 | e66cbf9d | PR #21 数据工厂 | 否（DRAFT） | 部分逻辑（杭州 worker） | UNCLEAR（协议 KEEP） |
| codex/mfy-data-foundation-001-rev2 | c807e98c | Data Foundation REV2（16 表 + API + BFF） | 否 | 部分（moodify_dev 19 表） | UNCLEAR |
| codex/moodify-1.0-release-convergence | 19d8a772 | 1.0 RC | 否（superseded） | 否 | LEGACY |
| codex/moodify-music-commercial-v1-001 | 5ef38d90 | 音乐平台商业化 | 否 | 疑似（vinext :3100） | UNCLEAR |
| codex/music-platform-listening-first | d747043a | 聆听优先平台 | 否 | 否 | EXPERIMENTAL |
| codex/moodify-ai-ear-reconstitution-001 | 8bc30a76 | Ear 重建（PR #16 前身） | 否（PR 关） | 否 | LEGACY |
| codex/auditory-intelligence-unification | 6446f75c | Ear 统一（PR #19） | 否（PR 关） | 否 | LEGACY |
| codex/mfy-mig-001-canonical-contracts | af0e1d41 | moodify.contracts（PR #18） | 否（PR 关，内容已进 #21） | 否 | 已吸收 |
| codex/pr15-asset-extraction-001 | fc995d29 | PR15 提取（#17 已合并） | 是（#17） | — | LEGACY |
| codex/mainline-cloud-dev-20260603 | 79754390 | PR #15 云主线 | 否（PR 关） | 否 | LEGACY |
| codex/cloud-mainline-dev-20260603-recovered | cfecdfec | 云主线恢复 | 否 | 否 | LEGACY |
| codex/moodify-1.0…（本地分支更多） | — | 本地 43+ 分支（含 reconstruction/3.0-external-audio/android-2.0 等 2026-08-17 活跃） | — | — | 见 Truth Table |

**本地新增分支（未推送远端）：** `codex/moodify-classic-reconstruction-001`（HEAD）、`codex/moodify-3.0-external-audio`、`codex/moodify-android-2.0`、`backup/mainline-cloud-dev-pre-github-cleanup`、`codex/github-cleanup` 等 —— 这些承载了 2026-08-09 之后的全部主要工作。

## CI / Tests / Deployment 代码

| 项 | 状态 | 证据 |
|---|---|---|
| Workflows | `ci.yml`（push main / PR main：ruff + pytest core）、`deploy.yml`、`moodify-temporal-texture.yml` | .github/workflows/ |
| CI 最近运行 | PR #21 的 CI：最近多次 **success**；**Temporal Texture Guard 持续 failure**；Deploy（tag v1.0.0-data-foundation）**failure** | gh run list（2026-08-11 起） |
| 测试规模 | core 81 个 test 文件、music 18、根 tests 3；历史全量绿记录（补丁包 TEST_RESULTS：692→869→851→816 等，来自记忆/artifact） | find tests |
| 云端部署 | 无 CI 部署链：tar + systemd 手工发布（LA /opt/moodify/releases/ 时间戳目录） | LA 扫描 |

## 关键结论

1. **GitHub main 落后本地工作 154 commits**；所有「重建优先」权威文件（宪法 v1.0、边界/身份/立体声/聆听环境策略、reconstruction 系模块）只在未合并分支。
2. **PR #21 是唯一 open PR**，协议裁定 KEEP，但未 merge；其「数据工厂/安静权威美学」与当前「重建优先」方向的关系未裁决（W01-P01 输入）。
3. **部署不可复现**：无 CI 部署、云端非 git、无法从 GitHub 重建线上状态。

# 05 — Moodify Truth Table

> 记录事实，不做架构决策。字段定义与主状态见 W01-P00_MASTER_TASK.md §3。
> CSV 版：`05_MOODIFY_TRUTH_TABLE.csv`（经 schemas/truth_table.schema.json 校验）。

## Repo 域

| id | capability | observed_state | main_status | canonical_relevance | code_ref | authority_conflict | confidence |
|---|---|---|---|---|---|---|---|
| TT-001 | GitHub main 分支 | fa88b0b9（2026-08-08），identity=Ear of AI | VERIFIED | CURRENT（历史权威） | origin/main | true | HIGH |
| TT-002 | 本地重建分支 | 98f7b96e，reconstruction-first，领先 154 commits | IMPLEMENTED_NOT_MERGED | CURRENT（新权威候选） | codex/moodify-classic-reconstruction-001 | true | HIGH |
| TT-003 | Classic Reconstruction Constitution v1.0 | docs 权威，Supersedes Ear-of-AI 产品表述 | IMPLEMENTED_NOT_MERGED | CURRENT | docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md | true | HIGH |
| TT-004 | moodify-core-package 引擎 | src/moodify 70+ 模块；tests 81 文件 | VERIFIED | CURRENT | moodify-core-package/ | false | HIGH |
| TT-005 | REPOSITORY_STATUS.md | baseline 0b355e7 / Ear of AI，落后于代码 | OBSOLETE | LEGACY | docs/REPOSITORY_STATUS.md | true | HIGH |
| TT-006 | v01_pipeline 主链 | 声明为 supported mainline；杭州 API health 报告 mode=v01 | DEPLOYED_NOT_VERIFIED | CURRENT | src/moodify/v01_pipeline.py | false | MEDIUM |
| TT-007 | orchestration/workflow_engine | LEGACY 声明 | OBSOLETE | LEGACY | src/moodify/orchestration/ | false | HIGH |
| TT-008 | data_factory 数据工厂 | Data Protocol v1 冻结；10 曲 pilot 全成功 | VERIFIED | CURRENT | src/moodify/data_factory/ | false | HIGH |
| TT-009 | node 队列 worker（moodify-node） | SQLite 队列；LA/杭州双部署 | DEPLOYED_NOT_VERIFIED | CURRENT | src/moodify/node/ | false | HIGH |
| TT-010 | reconstruction_objective v0.1 | 证据驱动目标规划，confidence-gated | IMPLEMENTED_NOT_MERGED | CURRENT | src/moodify/reconstruction_objective/ | false | HIGH |
| TT-011 | era_diagnostic v0.1 | 年代技术限制诊断 | IMPLEMENTED_NOT_MERGED | EXPERIMENTAL | src/moodify/era_diagnostic/ | false | HIGH |
| TT-012 | identity_guard v0.1 | 六维身份保护 veto | IMPLEMENTED_NOT_MERGED | CURRENT | src/moodify/identity_guard/ | false | HIGH |
| TT-013 | reconstruction_factory v0.1 | 学习记录工厂（rights-gated） | IMPLEMENTED_NOT_MERGED | EXPERIMENTAL | src/moodify/reconstruction_factory/ | false | HIGH |
| TT-014 | MAMSE-001..016 | 001-012 EXPERIMENTAL_ACCEPTED；013-016 仅结构 | VERIFIED / IMPLEMENTED_NOT_MERGED | EXPERIMENTAL | src/moodify/auditory + artifacts/mamse_* | false | HIGH |
| TT-015 | stems（lalal 集成） | 云端分离代理已部署 | DEPLOYED_NOT_VERIFIED | UNCLEAR | src/moodify/stems + 72c47c4d | false | MEDIUM |
| TT-016 | intervention 原语（3 个） | 版本化可旁路原语；负对照 5/5 旁路 | IMPLEMENTED_NOT_MERGED | EXPERIMENTAL | src/moodify/intervention/ | false | HIGH |
| TT-017 | 算法评审器 MFY-ALGO-REVIEW-001 | 确定性技术排名；10/10 pilot | VERIFIED | CURRENT | src/moodify/data_factory/algorithmic_review | false | HIGH |
| TT-018 | moodify.contracts | 四契约 | IMPLEMENTED_NOT_MERGED | CURRENT | src/moodify/contracts/ | false | HIGH |
| TT-019 | 聆听/盲听验证 | 71 candidates 冻结；人类会话跳过 | IMPLEMENTED_NOT_MERGED | EXPERIMENTAL | src/moodify/listening/ | false | HIGH |
| TT-020 | CI（ci.yml） | core 测试+ruff | VERIFIED | CURRENT | .github/workflows/ci.yml | false | HIGH |
| TT-021 | Temporal Texture Guard workflow | 持续 failure | DEPLOYED_NOT_VERIFIED | UNCLEAR | .github/workflows/moodify-temporal-texture.yml | false | HIGH |
| TT-022 | Deploy workflow | tag v1.0.0-data-foundation failure | UNKNOWN | UNCLEAR | .github/workflows/deploy.yml | false | MEDIUM |
| TT-023 | PR #21 | OPEN DRAFT，协议 KEEP 未 merge | IMPLEMENTED_NOT_MERGED | UNCLEAR | codex/mfy-data-factory-001 | true | HIGH |
| TT-024 | 补丁包 01-73 系列 | 多数已交付（artifacts+git）；部分计划壳 | VERIFIED（多数） | UNCLEAR | 补丁包/ + artifacts/ | false | MEDIUM |
| TT-025 | Android apps/android（Ear 工作台） | 设备测试 7/7 | VERIFIED | CURRENT | apps/android | false | HIGH |
| TT-026 | Moodify Music Android 3.1 | APK 3.1.0 发布；播放器设备验证 | VERIFIED | CURRENT | apps/music-android + deliverables | false | HIGH |
| TT-027 | apps/music-web（PWA） | Cloudflare 站点（wrangler 痕迹） | IMPLEMENTED_NOT_MERGED | UNCLEAR | apps/music-web | false | MEDIUM |
| TT-028 | 云端部署产物 | tar 时间戳发布，无 git 身份 | DEPLOYED_NOT_VERIFIED | UNCLEAR | /opt/moodify/releases/（LA） | false | MEDIUM |

## Cloud 域

| id | capability | observed_state | main_status | canonical_relevance | runtime_ref | authority_conflict | confidence |
|---|---|---|---|---|---|---|---|
| TT-030 | LA 节点 | 4C/8G/98G；6 服务+audiolla 容器运行 | VERIFIED | CURRENT | 103.144.246.242 | false | HIGH |
| TT-031 | 杭州节点 | 2C/1.6G；API+worker+4 timers | VERIFIED | CURRENT | 120.55.191.146 | false | HIGH |
| TT-032 | 腾讯云三台 | 2026-08-12 已删除 | OBSOLETE | LEGACY | 已不存在 | false | HIGH |
| TT-033 | PolarDB MySQL 172.27.118.106 | 空壳（黑箱调查）；直接核验 BLOCKED | BLOCKED | LEGACY | pc-bp1112f8t24wdta5t | false | MEDIUM |
| TT-034 | PolarDB MySQL 172.27.118.104 | moodify_dev 19 表 ≈0 数据；BLOCKED | BLOCKED | CURRENT | pc-bp19502y46246gv6n | false | MEDIUM |
| TT-035 | PolarDB PG 101.133.107.206 | 在线未用；BLOCKED | BLOCKED | LEGACY | pc-uf65m4xqwst72vq5a | false | LOW |
| TT-036 | OSS | NOT_PROVISIONED（无任何 bucket） | PLANNED_ONLY | UNCLEAR | — | false | HIGH |
| TT-037 | SQLite 队列 | LA 16KB 近空；杭州历史 pilot | DEPLOYED_NOT_VERIFIED | CURRENT | /var/lib/moodify/node.sqlite3 | false | HIGH |
| TT-038 | audiolla 容器 | 健康运行，无自动 pipeline | DEPLOYED_NOT_VERIFIED | EXPERIMENTAL | LA docker | false | HIGH |
| TT-039 | Cloudflare 隧道 | 运行中（LA） | VERIFIED | CURRENT | cloudflared | false | HIGH |
| TT-040 | 云端 AI 推理 | 无模型/无 GPU | PLANNED_ONLY | UNCLEAR | — | false | HIGH |

## Data / External 域

| id | capability | observed_state | main_status | canonical_relevance | evidence_ref | authority_conflict | confidence |
|---|---|---|---|---|---|---|---|
| TT-050 | 真实歌曲（pre-music） | ~7 首 owned 法语曲目 | VERIFIED | CURRENT | pre-music/ | false | HIGH |
| TT-051 | lalalai 分轨 | 多曲多次尝试 zip | VERIFIED（产物） | EXPERIMENTAL | pre-music/*/split zip | false | HIGH |
| TT-052 | data_factory cases | 4 case + pairwise + dataset summary | VERIFIED | CURRENT | outputs/data_factory/ | false | HIGH |
| TT-053 | golden_run_out | golden_record + source_manifest + blind_mapping | VERIFIED | CURRENT | moodify-core-package/golden_run_out/ | false | HIGH |
| TT-054 | artifacts 证据库 | 59 子目录，多数 FINAL_RESPONSE | VERIFIED | CURRENT | artifacts/ | false | HIGH |
| TT-055 | listening_test | 34 文件；结果 DATA_PENDING | UNKNOWN | EXPERIMENTAL | listening_test/ | false | MEDIUM |
| TT-056 | LALAL.AI | audiolla 代理已部署 | CONNECTED_UNTESTED | EXPERIMENTAL | LA 容器 | false | HIGH |
| TT-057 | FFmpeg | 杭州 8.0.1 / LA 4.4.2 | PRODUCTION_USED | CURRENT | 两节点 | false | HIGH |
| TT-058 | Demucs | 权重未下载 | UNAVAILABLE | UNCLEAR | 仓库引用 | false | HIGH |
| TT-059 | Basic Pitch | 工具代码；无运行 | EXPERIMENTAL | UNCLEAR | 仓库+LA capabilities | false | MEDIUM |
| TT-060 | 反馈学习闭环 | 不存在 | PLANNED_ONLY | UNCLEAR | — | false | HIGH |
| TT-061 | 云端完整 Ear 链路 | 仅代码，无生产流量 | PLANNED_ONLY | UNCLEAR | 黑箱调查 §5 | false | HIGH |

## 补充说明

- 冲突标记 `authority_conflict=true` 的项集中在：产品身份（TT-001/002/003）、状态文档（TT-005）、PR #21（TT-023）。
- PolarDB 三项（TT-033~035）直接核验被凭据阻塞 → BLOCKED；表/行数引用同日黑箱调查（MEDIUM）。
- 「VERIFIED」= 有可追溯证据；不自动等于人类验收（GO/盲听/Golden 定案均为 PENDING）。

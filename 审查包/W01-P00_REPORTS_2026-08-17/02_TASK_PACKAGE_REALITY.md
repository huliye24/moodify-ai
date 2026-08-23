# 02 — Task / Work Package Reality

**原则：** 区分「写过任务书」与「能力已经存在/交付」。主状态只允许 8 种；「基本完成」不算状态。
**证据源：** 补丁包/目录盘点（Explore agent）、artifacts/ 证据目录、docs/plan+audits、deliverables、git log、本会话记忆记录。

---

## 1. 补丁包系列（E:\moodify\补丁包\）

| 范围 | 主状态 | 依据 |
|---|---|---|
| 补丁包 01–03（relicense/GPL/法律文件族） | VERIFIED | 完整交付文件 + git 记录（5fea330/6514f46） |
| 补丁包 04–15 | PLANNED_ONLY（或 IMPLEMENTED_NOT_MERGED） | 单文件任务书壳；对应实现散落分支/记忆 |
| 补丁包 16–26 | PLANNED_ONLY | Codex Task Pack 模板，多数无回应 |
| 补丁包 27（aliyun node） | VERIFIED | CODEX_RESPONSE 已填 + artifacts/aliyun_node_001 + 部署在杭州 |
| 补丁包 28（24x7 数据管线） | VERIFIED | artifacts/mfy_24x7_data_pipeline_001 FINAL_RESPONSE + 杭州 4 timers 实跑 |
| 补丁包 29–42 | VERIFIED（多数） | MUSIC/EAR 系列 CODEX_RESPONSE 已填（含 30 算法评审、31 补丁、34 聆听等） |
| 补丁包 43–54（Phase 1 启动治理） | VERIFIED | 12 commits 落地（记忆 project_phase1_launch_43_54_done）+ artifacts/phase1_launch |
| 补丁包 55–65（发布门） | VERIFIED（多数） | artifacts/phase1_launch 独立验证；64A-2/64A-R2 有实际测试结果 |
| 补丁包 66–73（移动端/DSP/聆听） | VERIFIED | artifacts/mfy_*_mobile_* 6 个 execution_record（device_aware/dsp/audio_path/listening/one_play/preserve_identity）+ 73 最完整 |
| 补丁包 01–18 及 19–26 历史 | 视条目 | 记忆 project_mfy_1_0_rc_done 等；多数 IMPLEMENTED_NOT_MERGED（未进 main） |

> 注：补丁包编号与 git commit 的映射以记忆/artifacts 为准；本扫描未逐包重跑测试，全量绿数字引用各包 TEST_RESULTS 文件。

## 2. 研究/能力系列

| 任务 | 主状态 | 依据 |
|---|---|---|
| MAMSE-001~012 | VERIFIED（EXPERIMENTAL_ACCEPTED R2/R3） | artifacts/mamse_001..012 完整 benchmark+real_case |
| MAMSE-013~016 | IMPLEMENTED_NOT_MERGED（仅结构/部分） | artifacts/mamse_013..016 各 2 文件 |
| 听觉扫描 AS-001 / 听觉智能 AIR-001 | VERIFIED | git 5452ff4 / 9e622a8 |
| 时间质感波次1 DSK-MFY-TEMPORAL-TEXTURE-001 | VERIFIED | git 4a96e73 + artifacts/temporal_texture（guard_report） |
| i18n 两轮 / 歌词对齐 / Ocean 桥 | VERIFIED | git 3bfeabc / 0a54e62 / d740a3f + artifacts/ocean_bridge |
| A/B Judge / NTrack 排名 / 开放注册+CWC | VERIFIED | git 2e26fa4 / 59d0b29 / 2b83b03 + 7/7 黄金 |
| 数据工厂（补丁包26 c8971dc） | VERIFIED | Data Protocol v1 冻结 + CLI + 22 测试 |
| Data Foundation REV2（16 表+API+BFF） | IMPLEMENTED_NOT_MERGED | moodify/codex/mfy-data-foundation-001-rev2 分支 + moodify_dev 19 表 |
| Phase1 深度系列（depth-001..006） | VERIFIED | artifacts/mfy_phase1_depth_*（006 最全 22 文件） |
| 失败注入（补丁包29） | VERIFIED（8 PASS+2 FINDING） | artifacts/mfy_failure_injection_001 |
| 算法评审 + LUFS 修复（补丁包30） | VERIFIED | git 6b5592e + 10/10 pilot |
| 补丁包 43–54 全序列 / 55–65 发布门 | VERIFIED | git（8404de1..）+ artifacts/phase1_launch（EVIDENCE_INDEX + 独立验证×2） |
| 经典重建系列 MFY-CR-P01..P07 | VERIFIED（P04 由并行会话完成；P06/P07 有 golden 记录） | artifacts/mfy_classic_reconstruction_p01..07 FINAL_RESPONSE + git 12aaabae/98f7b96e 等 |
| 补丁包 68–73（移动端 6 包） | VERIFIED | git 23b13d35/db92b65b/c1f0c2d9/55bd01d0/7bf0f594/096d5f8f + artifacts execution_record |

## 3. 文档/规划层

- docs/plan：近期仅 3 份（08-11 ABSORB 外部评审吸收、08-12 CH02_NIGHT_BUILD+REPORT）；SPEC-002~006 为 5 月底历史。
- docs/audits：仅 DSK-MFY-EAR-V1-CH02-ABSORB-001。
- docs/PR_DISPOSITION.md（2026-08-11）：PR 处置协议（#21 KEEP 等）—— PLANNED_ONLY（执行未完成：无 merge、无 tag）。

## 4. 发布物（deliverables/releases）

| 发布 | 状态 |
|---|---|
| Moodify Music 1.0.0-rc.2 Android 20260815 | VERIFIED（APK+manifest+sha256） |
| Moodify Music 2.0.0 Android 20260815 | VERIFIED（含工程日志，最完整） |
| Moodify Music 2.0.1 Android 20260816 | 部分（仅 APK，**缺 manifest**） |
| Moodify Music 3.0.0 / 3.1.0 Android 20260816 | VERIFIED（APK+manifest） |

## 5. 跨领域状态汇总（唯一主状态）

| 主状态 | 代表任务 |
|---|---|
| PLANNED_ONLY | 补丁包 04-15、16-26、43-65 中未交付壳；MIG 迁移计划部分；W01 后续包（P01..P09 仅任务书） |
| IMPLEMENTED_NOT_MERGED | 全部重建系模块（objective/guard/diagnostic/factory）、Data Foundation REV2、Music 平台、MAMSE 013-016 |
| MERGED_NOT_DEPLOYED | moodify.contracts（在 #21 未 merge → 实际未达 main）—— 精确匹配项少，多数归入上/下行 |
| DEPLOYED_NOT_VERIFIED | LA music-platform/vinext、music-bff、audiolla（已部署无生产流量验证）；杭州 moodify-api/worker |
| VERIFIED | 补丁包 01-03/27/28/29-42/67-73、MAMSE-001..012、重建 P01-P07、Phase1 43-65、发布 APK、golden case |
| OBSOLETE | PR #20/#19/#18/#15/#13/#9（处置为 superseded）；orchestration/（LEGACY 声明）；腾讯云三台（已删） |
| BLOCKED | PolarDB 直接核验（凭据）、MIG-011 等依赖凭据/授权项（部分） |
| UNKNOWN | 云端部署精确 commit、music-bff/vinext 代码来源、部分历史补丁包对应关系 |

**事实边界：** 本表「VERIFIED」= 有 artifacts/test results/部署运行证据可追溯；不等于「人类已验收」。人类验收（GO 签署、盲听、Golden Song 选定）在记忆与文档中均为 PENDING / SKIPPED_PER_USER。

# Product Capability Matrix — Phase I Launch

**Document ID:** MFY-PHASE1-CAPABILITY-MATRIX-001
**Version:** 0.1
**Date:** 2026-08-14
**Package:** MFY_PHASE1_PRODUCT_LAUNCH_MASTERPLAN_001 (43)
**Status:** LIVE LEDGER — updated as packages 44–54 land

状态图例：`READY`（可上线证据充分）· `PARTIAL`（能用但缺门）· `MISSING`（未实现）·
`EXPERIMENTAL`（实验/研究性质）· `LEGACY`（历史遗留）· `BLOCKED`（被依赖阻塞）。

## 1. 官网（Official Website）

| 能力 | 状态 | 证据 | 映射包 |
|---|---|---|---|
| 官网信息架构（Ear/Music/Evidence/About/Contact） | MISSING | 蓝图已批准（docs/product-framework/02） | 46 |
| 官网内容与品牌叙事 | MISSING | 现有站点为静态壳（ops/web_origin/site/） | 46 |
| 官网部署（域名/nginx/TLS） | PARTIAL | ops/web_origin/nginx、deploy_static_origins.sh、verify_origins.sh；rongjingmusic.com / rongjingwenchuan.com | 46、53 |
| claim 成熟度模型（Concept/Experimental/Verified/Human-reviewed） | PARTIAL | 规则已冻结于 02 蓝图 §8；尚无站点应用 | 44、46 |
| 证据索引页（publish-safe 对象） | MISSING | — | 46、52 |

## 2. Moodify Ear

| 能力 | 状态 | 证据 | 映射包 |
|---|---|---|---|
| 源身份与摄入完整性（SHA-256） | READY | moodify-core-package/src/moodify/release.py、contracts | 37–42 |
| WSE 听觉表示/测量（波形/频谱/响度/动态/相位） | READY | auditory/、MAMSE-001~016、基准参考音频套件 | 17–25、37–38 |
| 测量契约与版本化 | READY | contracts/、DATA_PROTOCOL_V1.md | 35、38 |
| 受控干预实验室（候选生成） | READY | data_factory/plan_generator + intervention | 26 |
| 机器判断（限定范围） | READY | data_factory/algorithmic_review（MFY-ALGORITHMIC-REVIEW-001） | 30、41 |
| 确定性案例运行器（幂等/原子） | READY | data_factory/runner + node/worker | 39 |
| 无值守节点（队列/资源守卫/systemd） | READY | node/queue.py、ops/data_node、ops/web_origin/systemd/moodify-worker | 27、28 |
| 50-case pilot 运行器 | READY | ops/ear_batch/ear_batch.py、artifacts/ear_pilot_001/ | 42 |
| 证据图与 fail-closed 证据 | READY | evidence 图、案例清单 hash 校验 | 23、39 |
| 人工升级路径（HUMAN_REQUIRED 界面） | PARTIAL | 契约支持；产品表面未实现 | 48 |
| Ear 产品表面（工作台 UI） | PARTIAL | apps/android 4-tab（连接式）；无 web 工作台 | 47 |
| 判断权威状态 UI（等待人工/INCONCLUSIVE） | MISSING | — | 47、48 |
| Ear 公开 API 认证 | BLOCKED | api/main.py 无 auth 中间件；依赖 51 身份基线 | 51 |
| 跨产品证据桥（Music 请求 Ear 分析） | MISSING | 仅契约（docs/contracts/product-boundary.md） | 52 |

## 3. Moodify Music

| 能力 | 状态 | 证据 | 映射包 |
|---|---|---|---|
| 服务端 BFF（catalogue/creators/tracks/playlists/follows/favorites/search/intents） | READY | moodify-music-package/src/moodify_music/bff/main.py（约 40 路由） | 29–32 |
| 曲目不可变版本 | READY | api/tracks + versions；creator_lifecycle_state.md | 30 |
| Creation Passport 声明 | READY | api（passport 路由）；非认证声明 | 30 |
| 发布生命周期（draft→published→unlisted→archived） | READY | publication_state.md、api/tracks publish/unpublish | 30、32 |
| 聆听闭环（发现/播放/收藏/关注） | READY | apps/music-web（首页/发现/曲目/创作者/库）、Media3 播放 | 31、32 |
| Music Web/PWA（manifest/sw/离线页） | READY | apps/music-web/public/manifest.webmanifest + sw.js + /offline | 31、33 |
| 创作者控制台（目录/草稿恢复/收件箱） | READY | apps/music-web/app/studio、/drafts、/console、/inbox；drafts resume/abandon | 32 |
| 搜索 | READY | api/search、music-web 搜索 | 32 |
| Music Android 客户端 | EXPERIMENTAL | apps/music-android 4 个 Kotlin 文件薄壳 | 33 |
| 身份认证（正式账号体系） | PARTIAL | BFF 邀请制 HMAC session（12h TTL）；web 信任 OAuth 头 | 51 |
| 支付/结算 | PARTIAL | CWC ledger 仅在 api 层，BFF 未暴露；V1 非目标 | DEFER |
| 上传恢复（断点续传） | PARTIAL | media PUT + drafts resume；无分片续传 | 49/50 按需 |
| Ear 证据引用展示（publish-safe 门） | MISSING | 契约已冻结；无实现 | 52 |

## 4. 共享能力与生产运维

| 能力 | 状态 | 证据 | 映射包 |
|---|---|---|---|
| 域名/TLS/入口（LA + 杭州） | PARTIAL | ops/web_origin/nginx、cloudflared、deploy 脚本 | 46、53 |
| 媒体服务（Range/缓存头） | PARTIAL | nginx 配置；未做上线级验证 | 53 |
| 备份 | PARTIAL | ops/data_node/metadata_backup.py；PolarDB 备份未验证 | 53 |
| 监控/告警 | PARTIAL | daily_report.py、resource_probe.py；无告警通道 | 53 |
| 回滚 | PARTIAL | rollback_static_origin.sh；API/DB 回滚未建 | 53 |
| 灾难恢复演练 | MISSING | — | 53 |
| 身份/权限/隐私基线 | BLOCKED | 三处认证均为 PARTIAL；依赖 51 | 51 |
| 秘密/私人音频泄漏防护 | PARTIAL | 有禁止提交秘密的纪律与验证脚本；缺集中扫描 | 53 |
| 端到端上线验收 | MISSING | 契约与方法已有（36 包前身） | 54 |

## 5. 29–42 包 → 新框架映射

| 包 | 原定位 | 新框架归属 |
|---|---|---|
| 29 MFY_MUSIC_HANDOFF_BASELINE_001 | Music 服务基线 | Music 服务端（BFF 能力底子） |
| 30 MFY_MUSIC_CREATOR_LIFECYCLE_001 | 创作者生命周期 | Music Creator（版本/护照/发布） |
| 31 MFY_MUSIC_LISTENING_FIRST_WEB_001 | 聆听优先 Web | Music 聆听闭环 |
| 32 MFY_MUSIC_LIBRARY_AND_CREATOR_CONSOLE_001 | 库与控制台 | Music 库/控制台/搜索 |
| 33 MFY_MUSIC_APP_FOUNDATION_001 | 应用地基 | Music PWA + Android 壳 |
| 34 MFY_MUSIC_BETA_OPERATIONS_001 | 试用期运维 | Music 运维（并入 53） |
| 35 MFY_PRODUCT_BOUNDARY_AND_SHARED_CONTRACTS_001 | 边界与共享契约 | 44 治理冻结的前身（保持 FROZEN） |
| 36 MFY_V1_RELEASE_ACCEPTANCE_AND_HANDOFF_001 | V1 验收交接 | 54 上线验收的前身 |
| 37 MFY_EAR_SCIENTIFIC_BASELINE_001 | Ear 科学基线 | Ear 测量正确性基线 |
| 38 MFY_EAR_MEASUREMENT_CONTRACT_001 | 测量契约 | Ear 测量契约与权威 |
| 39 MFY_EAR_DETERMINISTIC_CASE_RUNNER_001 | 确定性运行器 | Ear 案例运行/失败恢复 |
| 40 MFY_EAR_SCIENTIFIC_LISTENING_STACK_001 | 科学聆听栈 | Ear 分层证据/成本档位 |
| 41 MFY_EAR_MACHINE_JUDGE_AND_CONTROLLED_VERIFY_001 | 机器判断 | Ear 限定范围机器裁决 |
| 42 MFY_EAR_50_CASE_AUTOMATED_PILOT_001 | 50-case pilot | Ear 批量 pilot 证据 |

## 6. 覆盖空洞（无产品表达的技术能力）

- **判断权威状态 UI**：契约与运行时支持 `HUMAN_REQUIRED`/`INCONCLUSIVE`，但没有任何产品表面消费它 → 包 47/48。
- **Ear 证据对外展示**：证据图/清单完备，无 publish-safe 的对外索引 → 包 46/52。
- **身份**：三处 PARTIAL 认证没有统一产品表达 → 包 51。
- **Music Android**：壳存在但无产品价值主张 → 包 49/50 按需决定留或退。

---
*维护规则：每包完成时更新本矩阵；状态变化必须带证据路径与 commit hash。*

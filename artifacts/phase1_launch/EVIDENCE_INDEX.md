# Evidence Index — Phase I Launch

**Document ID:** MFY-PHASE1-EVIDENCE-INDEX-001
**Version:** 0.1
**Date:** 2026-08-14
**Package:** MFY_PHASE1_PRODUCT_LAUNCH_MASTERPLAN_001 (43)
**Status:** LIVE LEDGER — 每包完成时登记证据路径 + commit hash

## 1. Ear 科学/研究证据（artifacts/）

| 证据包 | 内容 | 关键 commit | 状态 |
|---|---|---|---|
| artifacts/mamse_001..016 | R 轴多分辨率、CQT 几何、小波散射、相位几何、倒谱、调制频谱、PCA/SVD、NMF、RobustPCA、张量、协方差/本征空间、图信号 12 篇 + 阶段 0/1 吸收 | bfbfa6a, 2eb01b0, 5e6de72, 8e291b2, 4c92b0f, 89633c4, 6ce2635, 2bbc98a, 540b454, 6416cc5, 7369316, a0014b4 | 全 EXPERIMENTAL_ACCEPTED；595 绿 |
| artifacts/mfy_1_0_rc_001 | 1.0.0-rc.1 打包 + 10/12 门 | fdac22d..e81108d | 完成 |
| artifacts/g4_04_cross_machine_001 | 跨机器 52/52 零差异 | 6b5592e（包30） | 完成 |
| artifacts/g6_03_clean_install_001 | 干净安装验证 | 9918281 | 完成 |
| artifacts/mfy_failure_injection_001 | 失败注入 10 项 8 PASS+2 FINDING | 3783086（本地未推送） | 完成 |
| artifacts/mfy_data_factory_001_rev2 → artifacts/mfy_data_foundation_001_rev2 | 16 表落 PolarDB + 杭州 Data API + LA BFF + Web 12 步全通 | PR #2（分支 codex/mfy-data-foundation-001-rev2） | 完成；XEngine 无 FK |
| artifacts/aliyun_node_001 | node 队列/资源守卫/worker 3 case SUCCEEDED | 4a18b32（包27） | 完成 |
| artifacts/mfy_24x7_data_pipeline_001 | 10-song pilot 10/10 SUCCEEDED | c18a4f5（包28） | 完成 |
| artifacts/ear_pilot_001 | 50-case pilot（包42） | 52ae335 + 453ca14 | pilot 50/50 GO |
| artifacts/ear_batch | 批处理运行器证据 | ops/ear_batch/ | 运行中 |
| artifacts/web_origin | 官网入口部署证据 | ops/web_origin/ | 部署中 |

## 2. Music 产品证据

| 证据 | 内容 | 关键 commit | 状态 |
|---|---|---|---|
| artifacts/mfy_music_creator_lifecycle_001 | 创作者生命周期（版本/护照/发布） | 062c760 等（包30） | 完成 |
| artifacts/mfy_music_listening_first_web_001 | 聆听优先 Web 收敛 | a9e7524（包31） | 完成 |
| apps/music-web（库/控制台/搜索） | 包32 四个 checkpoint | a072e3a, 9939ae7, f3612fd, a9ab4e7 | 完成 |
| apps/music-web PWA 地基 | 包33 | 7334da9 | 完成 |
| docs/contracts/music/（6 份契约） | 身份/所有权/发布/API/生命周期/共享客户端 | ec5aac1（包35） | FROZEN |

## 3. 治理与边界证据

| 证据 | 内容 | 状态 |
|---|---|---|
| docs/product-framework/（4 份） | 宪法/官网蓝图/Ear 框架/Music 框架 | APPROVED v1.0（包44，2026-08-14 人类批准） |
| docs/product-framework/PRODUCT_AUTHORITY_INDEX.md | 文档权威索引 | 包44 |
| docs/product-framework/TERMINOLOGY_AND_CLAIMS.md | 术语表 + claim 成熟度 | 包44 |
| docs/PHASE1_CONSTITUTION.md | 仓库宪法 v1.1（判断权威修正） | 包44 修订 |
| AGENTS.md、README.md | 判断权威与公开声明修正 | 包44 修订 |
| docs/contracts/product-boundary.md | 产品边界与共享契约 | FROZEN（ec5aac1） |

## 4. 45–54 包登记

| 包 | 证据 | commit | P0 结果 |
|---|---|---|---|
| 45 设计系统 | docs/design/design_tokens_v1.md（token 单一来源）+ design_system_migration.md（KEEP/ADAPT/COMPLETE/ISOLATE）+ apps/music-web/components/ui/（6 组组件）+ app/design/ 陈列页 + tests/design-system.test.mjs（7/7）+ Android Color.kt/Theme.kt 归并 + artifacts/phase1_launch/design_system_001/ 截图（1440/390 双宽度，深色石墨 + evidence 绿 + amber 已验像素） | 06b2e6b | 7/7 测试绿；tsc 我的文件零错误 |
| 51 身份隐私 | docs/contracts/music/identity_access_privacy.md（决策/威胁模型/授权矩阵/迁移）+ models AuthSession/UserRole + api/identity.py + routes_auth.py + BFF 服务端 actor/CSRF/CORS/no-store + tests/test_identity.py + test_bff.py 更新 | a7378ae | 90 全绿（music 包）；demo 身份退出公开路径；actor 服务端解析 |
| 46 官网 | ops/web_origin/site/rongjingmusic/ 七页面（/、/ear、/music、/evidence、/about、/contact、/privacy）+ site.css（design tokens v1）+ robots/sitemap/favicon + check_site.mjs（6/6）+ artifacts/phase1_launch/official_site_001/ 截图（3 路由 × 1440/390） | 待提交 | 6/6 检查绿；无伪入口/无自动播放/无禁语声称；CTA 全部可解析 |

## 5. 登记规则

- 包 45–54 每包完成：追加一行（证据路径 + commit hash + P0 结果）。
- Gate D/E 审查时以本索引为检查清单；找不到证据的声称视为不存在。

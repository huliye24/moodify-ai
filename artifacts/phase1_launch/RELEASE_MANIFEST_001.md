# Release Manifest — MFY-PHASE1-RC-20260814-1

**Document ID:** MFY-RELEASE-MANIFEST-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_RELEASE_CANDIDATE_INTEGRITY_001 (57)
**Candidate:** MFY-PHASE1-RC-20260814-1 → **MFY-PHASE1-RC-20260814-2**（57 修正后）

## 1. 候选修正记录

| 发现 | 修正 | commit |
|---|---|---|
| ear-workbench 8 个 HTML 页面被 `*.html` gitignore 吞掉，HEAD 无页面 | .gitignore 例外 + 纳入全部 8 页 | 7d4982b |
| 部署脚本族/契约未跟踪 | 29 个文件纳入候选 | 80b3c5c |

## 2. Artifact 清单（核心可重建单元）

| Artifact | 源位置 | 构建 | 版本 |
|---|---|---|---|
| Ear API + 权威模块 | moodify-core-package/ | pytest 639（55 基线） | 1.0.0-rc.1 |
| Music Data API + BFF | moodify-music-package/ | pytest 104 | 0.1.0 |
| Ear 工作台（8 页 + assets） | apps/ear-workbench/ | node --test 7/7 | 0.1.0 |
| Music Web/PWA | apps/music-web/ | 静态检查 3 套（listening/creator-studio/design） | 0.1.0 |
| 官网静态站 | ops/web_origin/site/rongjingmusic/ | check_site 6/6 | v1 |
| 部署面 | ops/web_origin/（nginx/systemd/cloudflared/scripts） | bash -n 通过 | — |

## 3. 依赖与锁定（SBOM 摘要）

| 依赖 | 锁定文件 | 备注 |
|---|---|---|
| Python（core） | moodify-core-package/pyproject.toml | 无新依赖自 MAMSE-003 起 |
| Python（music） | moodify-music-package/pyproject.toml | fastapi/sqlalchemy/httpx/pymysql |
| Node（music-web） | apps/music-web/package-lock.json | **未提交**（用户第三方变更，55 记录）——发布前需人类决定 |
| bash 工具链 | — | GNU timeout、sha256sum（53 脚本） |

## 4. 配置变量清单（仅名称，无值）

| 变量 | 用途 | 必需 |
|---|---|---|
| MOODIFY_NODE_STATE_DIR / MOODIFY_NODE_OUTPUT_ROOT | Ear 节点 | 是 |
| MOODIFY_MAX_UPLOAD_BYTES / MOODIFY_MAX_RETAINED_JOBS | API 上限 | 否（默认） |
| MOODIFY_REVIEW_DB | 审核台账 | 是（48） |
| MOODIFY_BFF_AUTH_MODE | anonymous/invite_beta（生产禁 demo） | 是 |
| MOODIFY_BFF_SESSION_SECRET / MOODIFY_BFF_BETA_INVITES | 会话/邀请 | 是 |
| MOODIFY_BFF_CORS_ORIGINS | 精确 origin | 是 |
| MOODIFY_HANGZHOU_BASE / MOODIFY_HANGZHOU_KEY | BFF→杭州 | 是 |
| MOODIFY_INTERNAL_API_KEY | 内部服务密钥 | 是 |
| MOODIFY_DB_* | PolarDB 连接（R06） | 是（58 解除） |
| MOODIFY_BFF_MEDIA_ROOT / MOODIFY_BFF_TIMEOUT | 媒体/超时 | 否（默认） |
| MOODIFY_BACKUP_ROOT / MOODIFY_EAR_CASES / MOODIFY_REVIEW_DB | 备份 | 是 |

## 5. 干净环境验证（57 包）

| 项 | 结果 |
|---|---|
| 干净 checkout（无工作区残留） | 通过：全部 release-relevant 文件在 HEAD 中 |
| 部署脚本语法 | bash -n 全过（6 脚本 + ear_batch remote） |
| Python 编译 | ear_batch 模块 py_compile 过 |
| 工作台检查（干净环境） | 7/7 通过 |
| core authority 测试（干净环境） | 15/15 通过 |
| 关键文件存在性 | 全 OK（含修复后的 8 个 HTML 页） |

## 6. 事实边界

- 云端 CLOUD_VALIDATION 干净环境构建归 60/65（需部署授权）。
- package-lock.json 未提交：57 不处理用户第三方变更（57 禁止项），发布前需人类决定。
- 本 manifest 随 57 之后的修正更新（58–65 可能再改候选 → RC-3…）。

# Release Manifest — MFY-PHASE1-RC-20260814-1

**Document ID:** MFY-RELEASE-MANIFEST-001
**Version:** 1.1（57 全量重建验证后更新）
**Date:** 2026-08-14
**Package:** MFY_RELEASE_CANDIDATE_INTEGRITY_001 (57)
**Candidate:** MFY-PHASE1-RC-20260814-1 → **MFY-PHASE1-RC-20260814-2**（57 修正后）→ RC-3（55 v1.1 更新后）

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

## 3. 依赖与锁定（SBOM 摘要，v1.1 干净安装验证）

| 依赖 | 锁定文件 | 干净安装命令 | 验证 |
|---|---|---|---|
| Python（core） | moodify-core-package/pyproject.toml | `pip install -e ".[dev]"`（dev 组含 pytest/httpx） | 干净 venv 安装中（librosa 链大依赖） |
| Python（music） | moodify-music-package/pyproject.toml | `pip install -e ".[test]"`（test 组含 pytest） | **干净 venv 108/108 PASS** |
| Node（music-web） | apps/music-web/package-lock.json | `npm ci`（网络抖动需 `--fetch-retries=5`） | 首跑 ECONNRESET（瞬时），宽容参数重试中 |
| bash 工具链 | — | GNU timeout、sha256sum | 语法已验证 |

**教训（v1.1）**：干净环境必须按可选组安装测试依赖（`.[dev]` / `.[test]`）；裸 `pip install -e .` 装不出 pytest。npm ci 对本机网络抖动敏感，重试参数缓解。

## 4. 配置变量清单（仅名称，无值）

| 变量 | 用途 | 必需 |
|---|---|---|
| MOODIFY_NODE_STATE_DIR / MOODIFY_NODE_OUTPUT_ROOT | Ear 节点 | 是 |
| MOODIFY_MAX_UPLOAD_BYTES / MOODIFY_MAX_RETAINED_JOBS | API 上限 | 否（默认） |
| MOODIFY_REVIEW_DB | 审核台账 | 是（48） |
| MOODIFY_BFF_AUTH_MODE | anonymous/invite_beta（生产禁 demo） | 是 |
| MOODIFY_BFF_CORS_ORIGINS | 精确 origin | 是 |
| MOODIFY_HANGZHOU_BASE / MOODIFY_HANGZHOU_KEY | BFF→杭州 | 是 |
| MOODIFY_INTERNAL_API_KEY | 内部服务密钥 | 是 |
| MOODIFY_DB_* | PolarDB 连接（R06） | 是（58 解除） |
| MOODIFY_BFF_MEDIA_ROOT / MOODIFY_BFF_TIMEOUT | 媒体/超时 | 否（默认） |
| MOODIFY_BACKUP_ROOT / MOODIFY_EAR_CASES / MOODIFY_REVIEW_DB | 备份 | 是 |

## 5. 干净环境验证（57 包，v1.1 全量重建）

| 项 | 结果 |
|---|---|
| 干净 checkout（无工作区残留） | 通过：1518 个 tracked 文件清单与主工作区**完全一致**；关键文件 hash 5/5 一致 |
| 锁定依赖安装 | music `.[test]` 干净 venv 成功；core `.[dev]` 干净 venv 成功（librosa 链完整）；npm ci 506 包（抖动需 `--fetch-retries=5`） |
| **core 全量测试（干净 venv）** | **639 passed / 5 skipped**（5:41） |
| **music 全量测试（干净 venv）** | **108/108 PASS** |
| schema/migration dry-run | **21 表 + 关键列全验证**（schema_dry_run.py：SQL 8641 字符/21 CREATE TABLE，零库触碰；工具抓到我清单两处错误已修） |
| music-web build（干净环境） | vinext 构建产物生成（"Build complete"）；收尾在本地 Node 崩于 `cloudflare:` 平台协议（**已知**——rendered-html.test.mjs 已有同款容错；真机构建在 Cloudflare 部署环境完成，60/65） |
| **workerd 平台包缺口（干净环境发现）** | npm ci 在抖动时静默跳过 optional 平台包 `@cloudflare/workerd-windows-64` → build 崩；**已修**：build-verified.sh 加 fail-fast 预检 + 修复命令 |
| 主工作区 build 失败 | **环境问题**（陈旧 node_modules 缺 lightningcss 平台二进制布局）；干净 npm ci 无此问题，不视为候选缺陷 |
| 部署脚本语法 | bash -n 全过（6 脚本 + ear_batch remote） |
| 工作台/官网检查（干净环境） | 7/7 + 6/6 通过 |
| 关键文件存在性 | 全 OK（含修复后的 8 HTML + 7 HTML 页） |

## 6. 事实边界

- 云端 CLOUD_VALIDATION 干净环境构建归 60/65（需部署授权）。
- package-lock.json 未提交：57 不处理用户第三方变更（57 禁止项），发布前需人类决定。
- 本 manifest 随 57 之后的修正更新（58–65 可能再改候选 → RC-3…）。

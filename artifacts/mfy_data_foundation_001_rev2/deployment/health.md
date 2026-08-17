# Deployment & Health — MFY-DATA-FOUNDATION-001-REV2 Phase K

## 已部署（运行中）

| 组件 | 位置 | 状态 |
|---|---|---|
| PolarDB MySQL B moodify_dev | 杭州（16 表，utf8mb4，head 003） | ✓（alembic current = head） |
| 杭州 moodify-api (:8000) | Ear + Music `/internal/v1/music` 同进程 | active |
| 杭州 moodify-music-data-api (:8001) | 已停用（路由挂 8000 后冗余；回滚：`systemctl enable --now`） | stopped |
| LA moodify-music-bff (:8100) | /api/v1/music → 杭州 | active |
| nginx | rongjinwenchuan.xyz /api/v1/music/ → 8100 | reloaded（备份 moodify-sites.bak-20260813-bff） |
| LA music-web release | current → 20260813T231000Z-data-foundation（并行 self-hosted 版） | active, HTTP 200 |
| moodify-music-bff-release | 20260813T080000Z-bff（本任务构建，含 12 步页面；启动失败已回滚，问题=worker 模式 vite.config 差异） | 保留未启用 |

## 健康检查（2026-08-13 07:2x）

- https://rongjinwenchuan.xyz/ → 200
- https://rongjinwenchuan.xyz/api/v1/music/catalogue → 200（BFF→杭州→PolarDB 全链路）
- 杭州 :8000 health 200（Ear 端点未受影响）
- 3 域名全部 200

## Web 部署说明（诚实记录）
- 本任务构建的 Web release（含 BFF 改造页面）在 vinext start 时失败
  （ERR_UNSUPPORTED_ESM_URL_SCHEME cloudflare:）——原因：并行会话已将
  music-web 构建链切为 Cloudflare Worker 模式（vite.config.ts/worker/index.ts
  在 git 1b6b6d6/6e73678 中），本任务构建基于旧配置。
- **线上保持用户并行部署的 data-foundation release（200 正常）**。
- 合并路径：以 git HEAD（含双方工作）为源重新构建（worker 模式）→ 新 release。
  该操作需用户确认后执行（涉及线上切换）。

## 回滚
- music-web：`ln -sfn /opt/moodify/music/releases/<previous> /opt/moodify/music/current && systemctl restart moodify-music`
- BFF：`systemctl restart moodify-music-bff`（代码在 /opt/moodify/music-bff/）
- 杭州：恢复 main.py.bak-music-20260813 / unit .bak-music-20260813
- 数据库：Alembic downgrade（空库阶段安全）

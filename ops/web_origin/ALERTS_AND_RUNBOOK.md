# P0 Alerts & Runbook — Phase I

**Document ID:** MFY-ALERTS-RUNBOOK-001
**Version:** 1.0
**Date:** 2026-08-14
**Status:** LIVE — package MFY_PRODUCTION_OPERATIONS_OBSERVABILITY_001 (53)

## 1. P0 告警表

| # | 告警 | threshold | 持续时间 | owner | 用户影响 | 第一检查 | 降级 | 回滚 |
|---|---|---|---|---|---|---|---|---|
| A1 | 全站不可用（官网/Ear/Music 任一 5xx 率高） | >5% | 5min | huliye24 | 无法访问 | verify_origins.sh + nginx -t + systemd status | 静态回滚 / 只读页 | 切旧 release |
| A2 | 登录失败率异常 | >10% | 10min | huliye24 | 无法登录 | BFF 日志 session 错误；auth_sessions 查询 | 保持匿名只读 | 51 包会话代码前版 |
| A3 | Music 无法播放（Range 5xx） | >2% | 10min | huliye24 | 播放失败 | /audio Range 探测 + nginx log | 换源提示 | 媒体根引用恢复 |
| A4 | 发布写失败 | 任何 | 即时 | huliye24 | 无法发布 | 幂等冲突日志；PolarDB 状态 | 关闭发布写 | forward-fix + restore |
| A5 | Ear 队列停滞（job age 超限） | >30min | 15min | huliye24 | 案例不完成 | worker 心跳 + queue 表 | worker 重启（幂等） | 恢复中断 job |
| A6 | 磁盘逼近满 | >85% | 30min | huliye24 | 上传失败 | df + 媒体/证据增长 | 清理临时上传 | — |
| A7 | 数据库失败 | 连接失败 | 即时 | huliye24 | 全部 Music 写失效 | PolarDB 状态 + 连接池 | 只读降级 | restore |
| A8 | 证书临期 | <14天 | 每日 | huliye24 | HTTPS 告警 | cloudflared cert 检查 | 重签 | manage_cert_dns.py |
| A9 | 备份过期 | >24h | 每日 | huliye24 | 恢复风险 | 备份清单时间戳 | 立即补备份 | — |
| A10 | 人工审核积压（Ear） | pending >5 | 每日 | huliye24 | 案例悬置 | /api/v1/auditory/reviews | 通知 reviewer | — |

## 2. 运行手册（非作者按步骤执行验证）

### R1 全站不可用（A1）
1. `bash ops/web_origin/verify_origins.sh` — 定位失败域；
2. `ssh root@103.144.246.242 "systemctl status moodify-api moodify-music moodify-worker nginx"`；
3. `nginx -t && systemctl reload nginx`；
4. 若静态 origin 故障：`bash ops/web_origin/rollback_static_origin.sh <previous-release>`；
5. 记录 incident：时间、影响面、根因、恢复动作。

### R2 播放失败（A3）
1. `curl -H "Range: bytes=0-1023" https://rongjinwenchuan.xyz/audio/...` 期望 206；
2. 期望非 206 → 查 nginx log + 媒体根引用；
3. 引用缺失 → 从备份引用清单恢复（不重编码媒体）。

### R3 备份恢复演练
1. 取最新备份（含 Music DB dump、媒体清单、Ear case manifest）；
2. 在隔离环境导入；校验 users/track/version 计数、媒体 SHA-256、case manifest hash；
3. 任一 hash 漂移即恢复失败 → 上报 No-Go 项。

## 3. 日志与指标纪律

- 统一 request ID（BFF 转发 X-Request-Id；Ear API 生成 request_id）；
- 日志脱敏：无 cookie/token/invite/私人路径/音频正文；
- 指标不含音频正文或敏感声明；
- 保留期：应用日志 30 天，备份按 RPO/RTO 定义（见备份脚本）。

## 4. 可观测性清单（已具备 / 待建）

| 指标 | 现状 |
|---|---|
| 网站/API 可用性与错误率 | verify_origins.sh（探测）+ nginx log（待聚合） |
| P50/P95/P99 延迟 | 待建（nginx log 分析脚本） |
| Music playback/Range 失败 | A3 探测脚本（待建为 cron） |
| upload/publish 失败与幂等冲突 | BFF 日志（结构化为待办） |
| Ear queue depth/job age/stage failure/human-required backlog | /health queue + /reviews（47/48 已具） |
| database connections/storage | PolarDB 控制台 + A6/A7 |
| media/evidence disk capacity | resource_probe.py（data_node） |
| certificate expiry / backup age | A8/A9 检查脚本 |

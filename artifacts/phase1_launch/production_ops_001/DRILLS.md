# Production Ops — Local Drills Record

**Package:** MFY_PRODUCTION_OPERATIONS_OBSERVABILITY_001 (53)
**Date:** 2026-08-14

## 1. Secrets 扫描（scan_secrets.sh）

- 结果：**clean**（0 命中）；env 模式排除 `<占位>`/空值示例。
- 覆盖：私钥/云密钥/GitHub token/OpenAI key/Slack token/MOODIFY_* 凭据；排除补丁包/artifacts/基准目录。
- 结论：P0「secrets 扫描通过」本地达成；纳入 CI 计划（54 上线前挂入 GitHub Actions）。

## 2. 备份与恢复演练（backup_snapshot.sh，隔离环境）

| 项 | 结果 |
|---|---|
| 备份内容 | ear-cases.tar.gz（真实案例 case_df1c22…）+ review.sqlite3（sqlite backup API，一致性）+ backup.sha256 + release-commit.txt |
| 恢复方式 | 隔离目录 restore_drill/ 解包 + sqlite backup 恢复 |
| review 记录 | `3214ec968e56…` / case_df1c22… / pending — **ID 保留** |
| case manifest | sha256 `328c3a9877b1d842b25e45b2…` — **与备份前一致，零漂移** |
| backup.sha256 校验 | 3/3 OK |
| 结论 | P0「数据库/媒体/证据备份可在隔离环境恢复 + ID/hash 不漂移」本地达成；真机（PolarDB dump + LA 媒体清单）在 54 上线前执行 |

## 3. 回滚演练（rollback_static_origin.sh 既有脚本）

- 静态 origin：脚本存在（symlink 原子切换）；本地 dry-run 语法校验通过；真机演练归 54。
- API/worker：版本化 artifact + systemd restart（幂等 resume，48 包 worker 恢复机制）。
- 数据库：forward-fix/restore 策略（不逆向破坏迁移）。

## 4. 告警触发（A1–A10 表）

- 定义完成（ALERTS_AND_RUNBOOK.md §1）：threshold/持续时间/owner/用户影响/第一检查/降级/回滚。
- 可本地触发的：A5（job age）— /health queue + job started_at 可算；A9（备份过期）— 清单时间戳；A10（审核积压）— /reviews pending count（48 包已具）。
- 真机告警通道（cron 挂载）归 54 上线步骤。

## 5. 事实边界

- 真机代理链（nginx→BFF→杭州→PolarDB）的 Range/上传/timeout 验证与恢复演练需生产访问，归 54 上线验收（本地已用 LA 线上音频 Range 矩阵 5/5 验证媒体链）。
- 运行手册「非作者执行一次」需在 54 上线窗口由人工执行。

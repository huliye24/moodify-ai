# PRECHANGE_STATE.md — MFY-INFRA-FOUNDATION-001

任务开始前的完整状态快照（2026-08-13 05:56 CST）。本文件是后续所有写操作的回滚基准。

## 1. LA 生产基线（103.144.246.242）

| 项 | 状态 |
|---|---|
| music current symlink | `/opt/moodify/music/current` → `releases/20260813T050100Z` |
| moodify-music 进程 | PID 41057，启动 2026-08-13 05:03:05 CST，运行中（enabled） |
| systemd ExecStart | `/opt/node22/bin/node node_modules/vinext/dist/cli.js start --hostname 127.0.0.1 --port 3100` |
| 源码指纹 | 38 个源码/配置文件 + 5 个 wav 音频资产（255MB tar） |
| manifest | `la_music_manifest.sha256`（38 项） |
| 排除项 | node_modules/.next/dist/.wrangler/.sites-runtime/.openai（`excluded_files.txt`） |
| 敏感扫描 | 干净（.npmrc 无 token；无 ghp_/sk-/AKIA/LTAI/密码匹配） |
| 部署方式 | tar + symlink release（无 git） |

## 2. 杭州 ECS API（120.55.191.146）

| 项 | 状态 |
|---|---|
| bind | `0.0.0.0:8000`（uvicorn pid 1332） |
| 鉴权 | 无（任何公网来源可访问） |
| health | `{"status":"ok","version":"0.1.0","mode":"v01","mainline":"v01_pipeline"}` |
| systemd | moodify-api.service：WorkingDirectory=/root，PYTHONPATH=/root/moodify-runtime:/root/moodify-core-package/src |
| 代码位置 | /root/moodify-core-package/src/moodify/api/main.py（11983B，2026-08-08） |
| 其他服务 | moodify-data-worker（User=moodify）+ 4 timers |

## 3. PolarDB MySQL B（pc-bp19502y46246gv6n）

| 项 | 状态 |
|---|---|
| 引擎 | PolarDB MySQL 8.0.18（私网 172.27.118.104:3306） |
| 业务库 | moodify_dev（utf8mb4/utf8mb4_unicode_ci），表数 0 |
| 运行账号 | 无（尚无应用连接） |
| 管理账号 | mylab2@% — 全实例管理员（`*.*` ALL + CREATE USER + GRANT OPTION）⚠️ |
| 凭据复用 | mylab2/mylab 密码与 ECS root 复用 ⚠️ |

## 4. 网络状态

- LA → 杭州：ping 0% 丢包，170.5-170.8ms；TCP 8000 p50 0.17s；HTTP /health p50 0.35s
- 杭州 ECS → MySQL B：VPC 对等私网直连，DNS/TCP 3306/认证全部通过
- 3 域名：全部 Cloudflare proxy → 隧道 → LA nginx

## 5. 回滚路径（对应 06_ROLLBACK_PLAN.md）

| 改动 | 回滚 |
|---|---|
| Git baseline | Draft PR 不 merge，删除分支即恢复 |
| 杭州鉴权 | 备份 systemd unit/env → 失败恢复旧配置 + 重启 + 验证 health |
| 安全组 | 修改前记录 inbound rules → 误封即恢复 |
| moodify_app 账号 | 新建不动现有账号；权限错误只修正不提升 |
| 管理员密码轮换 | 未确认依赖前暂缓（BLOCKED_PENDING_CREDENTIAL_DEPENDENCY_CONFIRMATION） |

## 6. 本轮不处理（08 模板 C8 范围）

fail2ban / 监控 / CF SSL Mode / PG timezone / OSS / LA SQLite backup / 数据仓库 / Redis。

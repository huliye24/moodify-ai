# 03 — Secret Ownership Matrix

**规则（任务书 §2.8）:** 只定义 Secret 应该在哪里，不写入真实 Secret。禁止：Git、Android 包、任务包、完整 DSN 入报告。以下只记录**变量名/位置类/关系**，不含任何值。

| # | Secret | Owner | Consumer | Storage location class（现状） | Target location class | Rotation owner | Exposure boundary | Forbidden locations | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| S-01 | MOODIFY_DB_PASSWORD（PolarDB/MySQL） | 数据平面 | 杭州 moodify-api/worker | 杭州 /root/moodify-app-db.env（0600） | 同地 env + 权限收紧；目标：Secret Manager | 数据平面负责人 | 杭州本机 | Git、Android、任务包、报告 | current | E16（变量名） |
| S-02 | MOODIFY_INTERNAL_API_KEY（service-key） | 控制面 | LA BFF → 杭州 API | 杭州 /root/moodify-api.env（0600） | 同地；目标：轮换机制 | 控制面负责人 | 杭州本机 + LA BFF 侧对应配置 | Git、Android、报告 | current | E16 |
| S-03 | PolarDB admin 凭据（polardb_admin 类） | 数据平面 | 运维/Codex | 本地 0600 文件（路径未确认，BLOCKED） | 本地 + 轮换；目标：Secret Manager | 数据平面负责人 | 运维本机 | Git、服务器公网目录、报告 | BLOCKED 核验 | E17/E18 |
| S-04 | SSH 密钥（LA moodify_cloud） | 运维 | Codex/用户 | ~/.ssh/moodify_cloud（本机） | 保持 | 用户 | 本机 | 服务器其他账户、Git | current | E15 |
| S-05 | SSH 密码（杭州 root） | 运维 | Codex/用户 | 用户记忆 + 会话临时文件 | **目标：改密钥认证，废止密码** | 用户 | 会话 | 报告、日志 | current（风险项） | E14 |
| S-06 | LALAL.AI / audiolla API 凭据 | 外部服务 | audiolla 容器 | 容器/LA 配置 | 容器环境变量 | 外部服务负责人 | LA 本机 | Git、Android、报告 | current（值未核验） | E13/E18 |
| S-07 | Android signing key | 产品面 | 构建机 | 本机构建环境 | 保持（不上 Git） | 产品面负责人 | 构建机 | Git | current | E26 |
| S-08 | Cloudflare 隧道凭据 | 公网边界 | cloudflared | /root/.cloudflared/config.yml（LA） | 保持 | 运维 | LA 本机 | Git、报告 | current | E15 |
| S-09 | OSS AccessKey / STS | —（未开通） | — | NOT_PROVISIONED | 开通后：RAM 角色/STS，**不落服务器长期 env** | 数据平面负责人 | 服务端仅 | Android、Git | planned（P03） | TT-036 |

## 禁止清单（R7 + §2.8）

- [x] Secret 不进入 Git（现状核查：仓库无凭据文件——P00 扫描未发现；杭州 env 在服务器）
- [x] Secret 不进入 Android 包（Android 只持公开 URL；无任何云凭据）
- [x] Secret 不进入任务包/报告（本报告只含变量名与位置类）
- [x] 完整 DSN 不写入报告（本报告无 DSN）

## 风险记录（不修复，仅记录）

1. S-05：杭州 root 使用密码认证（ssh config `PasswordAuthentication yes`）——目标迁移密钥认证。
2. S-01：DB 密码曾在扫描调试中暴露于会话（W01-P00 记录），建议用户评估轮换。
3. S-03：PolarDB 凭据路径未知（BLOCKED），存在单点丢失风险。

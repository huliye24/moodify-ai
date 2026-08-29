# Database Preflight — MFY-DATA-FOUNDATION-001-REV2 Phase A5

| 项 | 值 |
|---|---|
| 实例 | PolarDB MySQL B：pc-bp19502y46246gv6n.rwlb.rds.aliyuncs.com:3306（私网 172.27.118.104） |
| 数据库 | moodify_dev（utf8mb4 / utf8mb4_unicode_ci） |
| 当前表数 | 0（空库，最新复核 2026-08-13） |
| 运行时身份 | moodify_app@172.21.10.9（仅 moodify_dev DML，凭据本地 0600 polardb_app.env） |
| 管理身份 | mylab2@%（已轮换独立密码，本地 0600 polardb_admin.env） |
| 连接路径 | VPC 对等私网（杭州 ECS 172.21.10.9 → 172.27.118.104） |
| server 级字符集 | utf8（库级 utf8mb4 覆盖；migration 必须显式 mysql_charset=utf8mb4） |
| 时间策略 | UTC（本任务所有业务表 DATETIME/时间列存 UTC） |

**migration 身份**：moodify_app 无 DDL 权限。将新建 `moodify_migration@172.21.10.9`（moodify_dev.* 的 CREATE/ALTER/DROP/INDEX/REFERENCES + DML），仅用于 Alembic 迁移；运行时仍用 moodify_app。

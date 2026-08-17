# Schema Review — MFY-DATA-FOUNDATION-001-REV2 Phase C

## 结论
- 16 张业务表全部落地 PolarDB MySQL B（moodify_dev），engine=XENGINE，charset=utf8mb4/utf8mb4_unicode_ci
- Alembic revision 链：001_identity_creator_catalog → 002_relationships_intents → 003_cwc_idempotency_audit (head)
- 本地 + 杭州均完成 upgrade head → downgrade base → upgrade head 全链验证，最终 head

## 表清单（16）
users / creator_profiles / tracks / track_versions / creation_passports / albums / album_tracks / follows / favorites / play_events / license_intents / support_intents / cwc_accounts / cwc_ledger / idempotency_keys / audit_events

## 关键设计
- 所有 ID 为应用层 UUID 字符串（varchar 36）
- 金额 BigInteger minor unit + CHAR(3) currency（无 float）
- CWC 整数单位（非货币）
- support_intents 状态仅 expressed/contact_requested/cancelled（无 paid/settled）
- license_intents 状态 submitted/reviewing/contacted/accepted/declined/closed
- 时间列 UTC：应用层 datetime(UTC) 写入 + 连接会话 time_zone='+00:00' + CURRENT_TIMESTAMP 默认值

## 平台决策记录
1. **PolarDB XEngine 不支持 FOREIGN KEY（errno 1235）** → 全部 FK 移除，引用完整性由应用层 ownership service 强制（与 Rev.2 04 契约一致）。保留 UNIQUE/INDEX/CHECK。
2. **PolarDB 不支持函数表达式默认值（errno 3774）** → server_default 统一用 CURRENT_TIMESTAMP（非 UTC_TIMESTAMP() 表达式），配合会话时区 UTC。
3. server 级字符集为 utf8，但库/表均为 utf8mb4（迁移显式指定 mysql_charset/collate）。

## 验证
- 16 表 XENGINE + utf8mb4_unicode_ci（information_schema 确认）
- moodify_app（运行时身份）INSERT/SELECT/DELETE 冒烟 PASS
- 单元测试 14 项全绿（唯一约束/状态/幂等/审计/金额）

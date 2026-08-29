# Foreign Key Inventory — MFY-DATA-FOUNDATION-001-REV2

## 结论
**0 个 FOREIGN KEY 约束。**

## 原因（平台决策）
PolarDB MySQL B 使用 **XEngine 存储引擎，不支持外键约束**（errno 1235
"XEngine currently doesn't support foreign key constraints"，2026-08-13 实测）。

## 决策
- 引用完整性由应用层强制（ownership service checks、domain validation）——
  与 Rev.2 `04_IDENTITY_OWNERSHIP_CONTRACT.md` 一致（"修改/发布 Track 必须经过明确
  actor/ownership service check"）。
- 保留的数据库级约束：UNIQUE（handle/email/auth_subject/user_id/复合键）、
  INDEX、CHECK（状态枚举）。
- 逻辑外键关系（设计层）：
  creator_profiles.user_id → users.id
  tracks.creator_id → creator_profiles.id；tracks.created_by_user_id → users.id
  track_versions.track_id → tracks.id；creation_passports.track_id → tracks.id
  albums.creator_id → creator_profiles.id
  follows.user_id → users.id；follows.creator_id → creator_profiles.id
  favorites.user_id → users.id；favorites.track_id → tracks.id
  play_events.track_id → tracks.id；license_intents.creator_id/track_id
  support_intents.creator_id/track_id；cwc_ledger.account_id → cwc_accounts.id

## 未来选项
若需要数据库级完整性，可评估 PolarDB InnoDB 引擎表（PolarDB 双引擎），
本阶段不做。

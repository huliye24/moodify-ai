# W02 Migration Rules

仅当 W01 结论为 `MIGRATE` 时启用。

## 1. Migration 必须具备

- from schema
- to schema
- version
- detection
- idempotency
- backup / rollback
- verification
- user data preservation

## 2. 禁止

- 启动时 silent reset
- schema mismatch → clear all
- duplicate Track → 直接删“看起来重复”的数据
- path missing → 自动删 Track
- playlist relation 无迁移计划
- migration 中顺手重构 UI

## 3. Recommended pattern

```text
detect old version
→ backup / snapshot
→ migrate
→ validate counts / relations
→ mark version
→ continue
```

如果迁移失败：

```text
fail safe
→ preserve old data
→ surface internal blocker
```

不要半迁移继续运行。

## 4. Migration Report

`artifacts/windows/w02/migration-report.md`

必须包含：

```text
MIGRATION_REQUIRED = YES | NO
OLD_SCHEMA =
NEW_SCHEMA =
ROWS / RECORDS BEFORE =
ROWS / RECORDS AFTER =
RELATION CHECK =
ROLLBACK =
RESULT =
```

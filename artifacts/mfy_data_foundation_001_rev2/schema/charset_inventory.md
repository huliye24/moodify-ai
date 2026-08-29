# Charset Inventory — moodify_dev

| 层级 | 值 |
|---|---|
| Database | utf8mb4 / utf8mb4_unicode_ci |
| Tables (16) | utf8mb4 / utf8mb4_unicode_ci（information_schema 确认） |
| Server default | utf8 / utf8_general_ci（PolarDB 实例级默认，业务表显式 utf8mb4 覆盖） |
| Migration 声明 | 每个 create_table 显式 `mysql_charset='utf8mb4', mysql_collate='utf8mb4_unicode_ci'` |
| 连接 | DSN `charset=utf8mb4` |

## 时间策略（UTC）
- 应用层写入 `datetime.now(timezone.utc).replace(tzinfo=None)`（models.utcnow）
- 每个连接 `SET time_zone='+00:00'`（db.py event + alembic env.py init_command）
- 默认值 CURRENT_TIMESTAMP 在 UTC 会话下产生 UTC

## 多语言支持
utf8mb4 完整覆盖中文/英文/法语/日语/韩语/emoji/歌词。

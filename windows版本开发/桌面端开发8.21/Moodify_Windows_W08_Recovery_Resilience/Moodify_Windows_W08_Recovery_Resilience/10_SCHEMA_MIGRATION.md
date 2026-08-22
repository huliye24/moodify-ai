# Recovery Schema Migration

## Required

```text
schema_version
```

## Cases

### Current Version
直接 validate + restore。

### Old Version
```text
detect
→ migrate
→ validate
→ persist current version
```

### Missing Version
按 legacy v0 处理或 safe fallback，必须明确。

### Future Version
不能尝试错误 downgrade。

推荐：
```text
ignore unsupported session snapshot
start safe session
preserve durable user data
```

## Migration Rules

- idempotent
- testable
- no destructive Library reset
- no Playlist reset
- no Track identity rewrite unless separately authorized

# Corruption Recovery

## Corruption Types

- empty snapshot
- truncated file
- invalid JSON/record
- wrong field types
- invalid enum
- impossible position
- malformed QueueItem
- invalid window coordinates
- unsupported schema version

## Goal

```text
App starts
Durable data remains
Valid session parts may recover
Invalid parts safely default
```

## Strategy

推荐优先级：

```text
current valid snapshot
→ last-known-good
→ partial repair
→ safe empty session
```

## Important

Safe empty session 只代表：

```text
no current playback/queue restore
```

不代表清空 Library / Playlist / Favorite / History。

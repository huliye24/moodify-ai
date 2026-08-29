# Cache & Storage Policy

## Cache Taxonomy

可能包括：

```text
metadata cache
thumbnail/artwork cache
cloud temporary upload/download
prepared-source cache
temporary conversion files
```

## Durable User Data

绝不是 cache：

```text
Track identity
Library membership
Playlist
Favorite
History
CloudPreparation identity
Original Music Files
```

## Clear Cache

必须做到：

```text
identify cache-only assets
→ release active handles
→ delete
→ verify
→ recalc usage
```

不能删除 durable data。

## Storage Location

优先只允许移动：
```text
cache
```

不建议 W11 暴露 core DB relocation。

## Migration

```text
validate target
→ writable test
→ copy/move
→ checksum/count verify
→ switch
→ cleanup old
```

失败：
```text
rollback
```

## Original User Music

Moodify 不移动用户原始音频文件作为“存储位置迁移”。

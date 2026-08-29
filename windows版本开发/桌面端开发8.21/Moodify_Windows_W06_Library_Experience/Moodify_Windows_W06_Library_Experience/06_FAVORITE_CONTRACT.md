# Favorite Contract

## Model

```text
Favorite
- track_id
- created_at
```

## Invariants

重复 favorite 必须 idempotent。

```text
favorite(T1)
favorite(T1)
→ one relation
```

Unfavorite 只删除 relation。

Unavailable Track 可保留 Favorite。

Remove from Library 时服从 W02 Track lifecycle。

禁止复制 Track metadata 形成 favoriteTrack truth。

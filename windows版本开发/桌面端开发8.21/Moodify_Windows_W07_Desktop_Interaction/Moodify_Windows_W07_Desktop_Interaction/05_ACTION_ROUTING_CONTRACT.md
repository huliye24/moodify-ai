# Unified Action Routing Contract

W07 应尽量让所有 Track view 使用统一 action model。

## Candidate Actions

```text
PLAY
PLAY_NEXT
ADD_TO_QUEUE
ADD_TO_PLAYLIST
FAVORITE
UNFAVORITE
REVEAL_IN_EXPLORER
REMOVE_FROM_LIBRARY
```

## Route

```text
UI action
→ interaction adapter
→ existing use-case
→ result
→ UI feedback
```

禁止：

```text
UI action
→ mutate store internals directly
```

## View-specific Actions

Playlist Item:
```text
REMOVE_FROM_PLAYLIST
```

Queue Item:
```text
REMOVE_FROM_QUEUE
```

Playlist:
```text
RENAME_PLAYLIST
DELETE_PLAYLIST
```

所有 destructive actions 必须明确作用域。

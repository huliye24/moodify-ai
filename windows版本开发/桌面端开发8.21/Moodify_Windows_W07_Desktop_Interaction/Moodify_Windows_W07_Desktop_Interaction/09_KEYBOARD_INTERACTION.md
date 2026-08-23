# Keyboard Interaction Contract

W07 只做局部快捷键，不做系统级/global hotkeys。

## Candidate

```text
Enter      play focused item
Space      play/pause when safe
Ctrl+A     select current view
Escape     clear selection / close menu
Delete     scoped remove with confirmation
Backspace  same only if platform convention safe
```

## Input Safety

当 focus 在：

```text
input
textarea
contenteditable
dialog form
```

播放器和 list shortcut 不得抢键。

## Delete Semantics

不同 view：

### Playlist
```text
Delete → remove from playlist
```

### Queue
```text
Delete → remove from queue
```

### Library
```text
Delete → remove from library
```

必须通过上下文确定，且不可删除原始文件。

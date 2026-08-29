# Drag & Drop Contract

## A. Explorer Files → Window

```text
Dropped file handles/paths
→ validate
→ W02 import
```

结果：
```text
IMPORTED
ALREADY_EXISTS
UNSUPPORTED
INVALID
FAILED
```

## B. Track → Playlist

```text
drag Track IDs
→ target Playlist ID
→ W03 add
```

## C. Track → Queue

W07 不强制实现视觉 drop-to-queue。
若当前 UI 有明确 Queue target，可接 W05 append。
否则 context menu 即可。

## D. Security

- no unrestricted shell
- no arbitrary path execution
- normalize dropped paths
- reject unsupported sources safely
- do not auto-recursively scan folders unless explicitly supported

## E. Feedback

允许：
- target highlight
- count badge
- not-allowed cursor/state
- success/failure summary

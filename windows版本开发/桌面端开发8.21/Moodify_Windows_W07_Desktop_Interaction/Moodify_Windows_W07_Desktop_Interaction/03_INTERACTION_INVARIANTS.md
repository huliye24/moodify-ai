# Desktop Interaction Invariants

## I-01 Interaction ≠ Authority
右键、拖拽、多选、键盘都是 command/input layer。

## I-02 Selection Is Ephemeral
Selection 只是 UI state，不是 Library/Playlist/Queue。

## I-03 File Drop Reuses Import
```text
Drop File → W02 Import
```

## I-04 Playlist Drop Reuses Playlist Use Case
```text
Drop Track → W03 Add Track
```

## I-05 Queue Action Reuses Queue
```text
Play Next / Add to Queue → W05
```

## I-06 Double Click Reuses Playback
不直接 new audio element。

## I-07 Stable IDs Over DOM Indices
多选、拖拽、batch 都按稳定 ID。

## I-08 Destructive Semantics Are Explicit
“移出歌单”“从音乐库移除”不能都写“删除”。

## I-09 Original File Deletion Forbidden
W07 不删除用户音频源文件。

## I-10 Native Bridge Must Stay Narrow
不得为了 Reveal/Drag 开放任意 shell/filesystem 权限。

## I-11 View Changes Cannot Corrupt Selection
selection policy 必须固定。

## I-12 No Visual Rebuild
W07 改交互，不改产品视觉语言。

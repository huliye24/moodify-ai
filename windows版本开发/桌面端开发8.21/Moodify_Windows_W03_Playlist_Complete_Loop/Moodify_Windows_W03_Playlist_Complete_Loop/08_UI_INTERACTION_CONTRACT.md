# W03 UI Interaction Contract

```text
VISUAL_REDESIGN = FORBIDDEN
```

## Sidebar

当前 `我的歌单 +` 保留。

点击 `+`：

```text
minimal create dialog
```

创建后出现在 sidebar。

## Playlist Detail

保持轻量：

```text
Playlist Name
Track Count

Track rows...
```

不做 dashboard。

## Track Context Menu

新增：

```text
播放
下一首播放（如果当前已有能力，否则不在 W03 新建）
────────
添加到歌单 >
────────
从音乐库移除
```

本包只实现与 Playlist 相关项。

## Playlist Item Context Menu

允许：

```text
播放
────────
从歌单移除
```

## Reorder

优先 drag-and-drop。

若当前技术栈不适合：
可临时使用 move up/down，前提是视觉噪声最小。

## Delete Playlist

需要确认。

## Empty Playlist

建议极简：

```text
这个歌单还没有音乐
从音乐库添加歌曲
```

不要增加大量引导卡片。

## Unavailable Track

最小状态：

```text
无法找到本地文件
```

不暴露内部错误栈。

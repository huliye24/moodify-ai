# Reset Settings Contract

## Action

```text
恢复默认设置
```

需要确认。

## Reset Scope

只重置：

```text
Settings authority
```

## Must Preserve

```text
Library
Tracks
Playlists
Favorites
History
CloudPreparation records
Original music files
```

Queue/Playback session 是否重置：
默认不因“重置设置”而立即清除当前播放会话。

## After Reset

应用安全默认：

```text
System Default output
Restore Volume ON
No autoplay
Close = Quit
Launch At Startup OFF
Cloud Preparation MANUAL
Fallback Local ON
```

不要求重启，除非某些 setting 的 apply semantics 是 NEXT_LAUNCH。

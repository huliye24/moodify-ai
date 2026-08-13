# Moodify Music — Platform Capability Notes (v1)

MFY_MUSIC_APP_FOUNDATION_001 Checkpoint B 证据记录。如实记录平台能力，不承诺不支持行为。

## 已实现（Web/PWA 层）

- Media Session metadata（title/artist/artwork）+ play/pause/prev/next handlers（page.tsx）。
- 播放状态与曲目行/黑胶/底部播放器同步；Media Session playbackState 同步。
- 播放失败/网络错误显示可恢复提示（audio onError 由现有 player 流程覆盖）。
- PWA：manifest + theme-color + Service Worker（仅缓存应用壳；API/私人页/音频 network-only）。

## 平台限制（实测/已知，未验证项标注）

| 平台 | 后台播放 | 锁屏控制 | 说明 |
|---|---|---|---|
| Android Chrome（PWA） | 有限支持（需用户会话活跃；长期后台受系统策略限制） | Media Session 锁屏控件 | 需测试确认 |
| iOS Safari（PWA） | **不支持**（Safari 无 Web 后台音频） | 锁屏 Media 控件部分支持 | 平台限制，不承诺 |
| Android 原生（music-android） | ExoPlayer 可后台（需前台服务策略，V1 最小壳未实现前台服务） | MediaSession 可接入 | 33D 壳未接 MediaSession（最小切片） |

## 未验证/阻塞

- iOS/Android 真机能力记录：**BLOCKED（无真机设备）**——不得宣称通过（33 号包 04 验收要求）。
- 耳机拔出/音频焦点丢失行为：依赖系统默认（Android 焦点策略），未专项测试。

## 结论

- 后台/锁屏播放是客户端能力，不产生第二套曲库状态（队列以 track ID 对齐服务器事实）。
- 离线只缓存应用壳；无离线曲库下载（V1 默认不做）。

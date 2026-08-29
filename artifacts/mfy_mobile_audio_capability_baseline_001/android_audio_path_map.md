# Android 3.1 音频路径图 — MFY_MOBILE_AUDIO_CAPABILITY_BASELINE_001

**审计对象**: `E:\moodify-worktrees\moodify-3.0-external-audio` HEAD `f6316612`
**性质**: 只读;路径均来自真实源码

## 1. 播放链路总览

```text
本地音频(content:// / file:// URI)
  或 云端音频(https://rongjinwenchuan.xyz/audio/{key} 或 /api/v1 路径)
        │
        ▼
PlaybackManager (data/PlaybackManager.kt:58, Media3 ExoPlayer 1.10.1 单例)
  ├─ resolveUrl (L215-222): http(s) 直连 / <base>/api/v1 + Bearer / content:file URI 原样
  ├─ DefaultHttpDataSource.setDefaultRequestProperties 动态 Bearer (L274-279)
  ├─ DefaultLoadControl: 20s/90s buffer, 100ms/250ms, 5s back-buffer, 时间优先 (L91-100)
  └─ CacheDataSource + SimpleCache 512MB LRU (PlaybackAudioCache.kt:19-55)
        │
        ▼
ExoPlayer 默认 AudioSink  (无任何自定义 AudioTrack/Equalizer/offload/AudioSink)
        │
        ▼
系统 mixer → 设备输出
```

## 2. 本地文件入口(MainActivity)

- `handleExternalAudio`(MainActivity.kt:65-80),singleTop + onNewIntent
- VIEW/SEND/SEND_MULTIPLE intent-filter(Manifest,content/file scheme,audio/* + application/ogg),EXTRA_STREAM + ClipData 多文件(L82-101)
- `takePersistableUriPermission`(FLAG_GRANT_PERSISTABLE_URI_PERMISSION,L72-78)确保持续访问
- 标题从 OpenableColumns.DISPLAY_NAME 读取(L103-120)
- **无 SAF 文件选择器 UI;无文件复制到应用目录(直接以 URI 播放)**
- **无格式枚举/转码/采样率协商**:格式支持完全依赖 ExoPlayer 默认 codec

## 3. 格式转换点

| 位置 | 是否转换 | 说明 |
|---|---|---|
| 输入 URI → ExoPlayer | 无 | 原样传入,无 re-encode |
| 缓存层 | 无 | SimpleCache 缓存原始字节流,不做格式处理 |
| 输出 | 无 | 纯 ExoPlayer 默认 AudioSink,无 AudioProcessor |
| 处理侧(core) | 有 | data_factory/intervention.py 输出 24-bit PCM WAV(离线路经,未接播放) |

## 4. 系统 mixer / offload / AudioTrack / MediaSession

- **AudioTrack / AudioSink / AudioProcessor / AudioEffect / Equalizer / offload / AudioManager**:全部 NONE,零代码存在。输出完全委托 ExoPlayer 默认栈。
- **MediaSession**:READY — `MediaSession.Builder`(PlaybackManager.kt:141)+ `MediaSessionService`(PlaybackService.kt:12)+ startForegroundService(L144-147),Manifest `foregroundServiceType="mediaPlayback"`;锁屏控制/蓝牙 media button 由系统通知默认支持(无自定义 MediaButtonReceiver)。
- **后台播放**:READY — 前台服务 + POST_NOTIFICATIONS 运行时申请(MainActivity.kt:123-129)。

## 5. 缓存边界

- `PlaybackAudioCache.kt`:SimpleCache `cacheDir/moodify_playback_v2`,LRU 512MB,FLAG_IGNORE_CACHE_ON_ERROR
- prefetch:队列后续最多 10 首 × 2MB,单线程 daemon executor,generation 失效取消(L29-50)
- cache key = 完整 URL/URI 字符串(PlaybackManager.kt:226);**content:// 本地 URI 也走同一缓存**

## 6. UI 结构

- `MoodifyApp.kt`:ModalNavigationDrawer + AnimatedContent,4 目的地 PLAYER/PLAYLISTS/FAVOURITES/PROFILE(L87,117-141)
- `HomeScreen.kt`:VerticalPager 全屏播放页(曲名/播放/收藏/加歌单/黑胶动画/进度条);启动拉 CatalogueClient 目录并自动 loadQueue;AUDIO_BASE=https://rongjinwenchuan.xyz/audio/(L76)
- **死代码(未接线但完整)**:NowPlayingScreen.kt(A/B 双按钮 L105-115)、components/MiniPlayer.kt(完整拖拽手势)、components/PlaybackBar.kt
- 实际 UI 无 MiniPlayer——音频页即主屏 Pager

## 7. 数据层

- PersonalLibraryStore.kt:收藏+歌单,SharedPreferences JSON(仅存 QueueItem 元数据)
- MoodifyApiClient.kt:HttpURLConnection + org.json 零依赖客户端
- TokenStore.kt:Android Keystore AES/GCM 加密 token
- BaseUrlStore.kt:基于 BuildConfig

## 8. 测试覆盖(音频路径缺口)

| 测试 | 覆盖 |
|---|---|
| MoodifyApiClientTest / MiniPlayerGestureLogicTest / LocaleKitTest / StringKeyParityTest | 协议、手势、i18n |
| androidTest: MiniPlayerGestureTest / LanguageSwitchTest | Compose 手势、i18n |
| **PlaybackManager / ExoPlayer / 缓存 / MediaSession / Service / 本地 URI 播放** | **零覆盖** |

## 9. 对 68-73 的关键边界含义

1. **输出路径是干净的委托栈**——移动端听觉计算层可整块插入为自定义 AudioProcessor/DataSource,无历史包袱
2. **A/B 对比机制已存在**(isOriginal 标记 + 相邻入队),是 71/73 的直接基础
3. **本地 URI 即播即用,无副本**——68 的 bit-transparent 基线需在此之上加"输入字节校验"观测点
4. **缓存 key 是 URL/URI 字符串**——重建结果与原始文件必须区分缓存命名空间(避免命中错文件)
5. **无转码/采样率协商**——69 的 DSP Runtime 若要处理 44.1k/96k 混合作业,需定义 resample 策略(不盲目升采样)

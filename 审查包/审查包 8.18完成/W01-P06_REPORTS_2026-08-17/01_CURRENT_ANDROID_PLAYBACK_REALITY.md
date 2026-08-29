# 01 — Current Android Playback Reality

**W01-P06 · 2026-08-17 · GATE P06-2 输出 · 只读扫描（未改动任何 Android 文件）**

> 扫描对象：`apps/music-android`（Canon 对外产品面，包名 `com.moodify.music`，`rootProject.name = "MoodifyMusic"`）。
> 对照对象：`apps/android`（包名 `com.moodify.app`，功能更全的**遗留/内部 demo 面**，非 Canon 产品面）。
> 证据为仓库内真实文件路径 + 行号。本报告只记录现状，不做重写。

## 0. 两个 Android 工程的关系（先讲清）

| 工程 | 包名 | 定位 | 关键差异 |
|---|---|---|---|
| `apps/music-android` | `com.moodify.music` | **Canon 对外产品面**（本包对象） | 纯前台单 ExoPlayer，无 Service/Session |
| `apps/android` | `com.moodify.app` | 遗留 demo（v2.0.0, versionCode 20） | 有 `MediaSessionService`、前台通知、Bearer auth、队列预取、Compose Navigation |

- 引入提交：`7334da9e feat(music): app foundation — PWA, Media Session, shared contract, Android shell (MFY_MUSIC_APP_FOUNDATION_001)`。
- ⚠️ **版本口径不一致（事实记录）**：仓库内 `app/build.gradle.kts:15-16` 为 `versionCode = 3, versionName = "2.0.1"`；Canon/REPOSITORY_STATUS 称「music-android 3.1」。仓库中无 3.1 版本标记 → 记 `HUMAN_DECISION_REQUIRED`（口径对齐），不阻断 P06。

## 1. Player Engine

- framework：**Media3 ExoPlayer（仅 exoplayer 模块）**，`androidx.media3:media3-exoplayer:1.10.1`（`app/build.gradle.kts:34`）。
- **未引入** `media3-session` / `media3-ui` / `media3-datasource-*`。
- version：Media3 1.10.1；AGP 8.11.1；Kotlin 2.2.20；compileSdk/targetSdk 36；minSdk 26。
- source types：本地 `content://`/`file://` Uri（外部分享/打开 intent）+ 远程 HTTPS URL。
- local/remote：混合（见 §3）。
- seek support：有（`seekTo`，`PlaybackController.kt:88-91`；UI Slider `MoodifyMusicApp.kt`）。
- buffering：有（`STATE_BUFFERING → isLoading`，`PlaybackController.kt:42`）。
- background：**不支持**（无前台 Service / 无 wake lock / 无 MediaSession）。
- audio focus：**未处理**（全仓无 `setAudioAttributes(handleAudioFocus=)` / `OnAudioFocusChangeListener`）。
- notification：**无**（无 MediaSession → 无 MediaStyle 通知；无 `POST_NOTIFICATIONS`）。
- lifecycle：播放器随 `MainActivity` 生死（`onCreate` 建，`onDestroy` `release()`，`MainActivity.kt:27,99-102`）。

## 2. Data Layer

- Track model：`data/Dto.kt:19-48`（`Track`，`audioAssetKey` 取自 `version.audio_asset_key`）。
- repository：**无 Repository/DataSource 分层**；UI 层直接调 client（`MoodifyMusicApp.kt:80`）。
- API client：`data/BffClient.kt`（手写 `HttpURLConnection`，无 Retrofit/OkHttp/Ktor；连接 10s / 读 15s）。
- local cache：无（`SecureStore.kt` 预留 Keystore AES 存 session token，**当前无人调用**，V1 匿名收听）。
- queue model：自管理队列（`PlaybackUiState.queue/index`），不用 ExoPlayer 原生队列；`move(delta)` 循环切歌（`PlaybackController.kt:101-107`）。

## 3. Current Cloud Playback（最关键）

`PlaybackController.resolvePlaybackUri()`（`PlaybackController.kt:110-122`）三级优先：

1. `track.externalUri != null` → 本地 Uri（外部音频）。
2. `audioAssetKey != null && delivery != null` → `deliveryClient.resolve(track.id).playbackUri`（**W01-P06 契约路径**）。
3. 兜底：**写死静态 CDN** `https://rongjinwenchuan.xyz/audio/{audioAssetKey}`（`:118,121` 出现两次）。

- **endpoint**：BFF `https://rongjinwenchuan.xyz/api/v1/music`（硬编码 `BffClient.kt:11`）；音频 host `https://rongjinwenchuan.xyz/audio/...`（硬编码）。
- **auth**：无（匿名收听）。
- **URL model**：现状 = 客户端用 `audioAssetKey` **拼静态 CDN URL**（NW-03 current：无鉴权静态 URL）。
- **expiry handling**：无（静态 URL 无过期）。
- **failure handling**：`onPlayerError` → 统一文案「暂时无法播放，请稍后重试」（`PlaybackController.kt:49`）。
- ⚠️ **关键事实**：第 2 条（Delivery 契约）路径**当前永远不会走**——`MainActivity.kt:27` 是 `PlaybackController(this)`，未传 `delivery`；`PlaybackDeliveryClient` 全仓仅在测试里被实例化。生产远端播放 100% 走静态 CDN 兜底。

## 4. Current UI

- PLAY/PAUSE：`toggle()`（`PlaybackController.kt:80-83`）+ `NowPlaying`/`MiniPlayer`。
- next/previous：`next()/previous()`（自管理索引循环）。
- swipe：**无垂直滑动切歌**（产品面无手势系统；遗留 `apps/android` 有 `MiniPlayerGesture*`）。
- loading：`isLoading` → UI loading 态。
- error：`error` 字段 → UI 文案。

## 5. Current Tests

- unit（JVM）：仅 `app/src/test/.../player/PlaybackDeliveryClientTest.kt`（6 用例，JUnit4 + org.json，注入假 `fetcher` 测 `PlaybackDeliveryClient` 纯逻辑）。**无针对 `PlaybackController`/ExoPlayer/UI 的测试。**
- instrumentation：**无 `src/androidTest` 目录。**
- device/manual：无记录。

## 6. 安全现状（供 11 号报告）

- APK/源码扫描：**无 OSS AccessKey、无 DB 凭证、无处理 API key、无私钥、无长期 bearer token**。
- 唯一硬编码 = 两个公开 URL（BFF base + CDN host）。`usesCleartextTraffic="false"`（仅 HTTPS）。
- 无 signingConfig；release `isMinifyEnabled=false`，无混淆。

## 7. Decision（reuse / wrap / remove / human-decision）

- **reuse**：Media3 ExoPlayer 引擎（不重写解码器/不换框架，符合任务书 §9）。
- **reuse**：`PlaybackDeliveryClient` + `PlaybackMetadata` + `DeliveryFailure` 契约（已存在且可注入，JVM 可测）。
- **wrap**：`PlaybackController` 已具 delivery-first 逻辑（`resolvePlaybackUri`），接线的唯一缺口是**生产注入一个真实 `fetcher`（打 BFF `/tracks/{id}/playback`）**——该端点未部署（见 02/06 报告，BLOCKED）。
- **remove later**：静态 CDN 兜底路径（NW-03 target 要求演进为 BFF 签发限时 URL）——**本包不删除**，因真实签发端点未上线，删除会弄断现有 PLAY。
- **human decision required**：
  1. 版本口径（2.0.1 vs 3.1）。
  2. 是否/何时引入 MediaSessionService + 前台通知 + 音频焦点（现状全无；属 P06 §22「禁止无关 UI/能力扩张」边界外，需人类裁决是否纳入 PLAY 基线）。

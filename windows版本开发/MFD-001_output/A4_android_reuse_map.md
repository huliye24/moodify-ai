# MFD-001 Android 可复用资产映射

**生成时间:** 2026-08-20
**任务:** MFD-001 阶段 A4 — Android 资产盘点

---

## 1. Android 当前位置

| 组件 | 路径 | 状态 |
|---|---|---|
| 主应用 | `apps/music-android/` | ✅ ACTIVE |
| 源码根 | `apps/music-android/app/src/main/java/com/moodify/music/` | ✅ PRESENT |
| 构建配置 | `apps/music-android/app/build.gradle.kts` | ✅ PRESENT |

## 2. 产品层资产 (可复用)

| 资产 | Android 位置 | Desktop 复用方式 | 复用价值 |
|---|---|---|---|
| **BFF API 端点定义** | `data/BffClient.kt` | ✅ 直接复用 URL 和数据模型 | **高** — 同一 BFF |
| **Bootstrap 数据模型** | `data/BffClient.kt:Bootstrap` | ✅ 复用字段结构 | 高 |
| **Catalogue 数据模型** | `data/BffClient.kt:Catalogue` | ✅ 复用字段结构 | 高 |
| **Track 数据模型** | `data/BffClient.kt:Track` | ✅ 复用字段结构（含 audioAssetKey） | **高** — 核心播放实体 |
| **API Error 模型** | `data/BffClient.kt:ApiError` | ✅ 复用错误码 | 中 |
| **播放状态机概念** | `player/PlaybackController.kt` | ⚠️ 参考逻辑，不移植代码 | 中 |
| **MediaSession 集成模式** | `player/MoodifyMediaSessionService.kt` | ⚠️ 概念参考，Desktop 用不同 API | 低-中 |

## 3. API Contract 可复用性

### 完全可复用 (同一 BFF)

```typescript
// Desktop 将使用相同的 HTTP API
interface PlayerAPI {
  bootstrap(): Promise<Bootstrap>
  catalogue(): Promise<Catalogue>
  track(id: string): Promise<Track>
}
```

### Android BFF Client 关键代码参考

```kotlin
// 基础 URL (硬编码在 Android，Desktop 应配置化)
baseUrl = "https://rongjinwenchuan.xyz/api/v1/music"

// 核心端点
GET /bootstrap     → 应用配置
GET /catalogue    → 曲目列表
GET /tracks/{id}  → 单曲详情 (含 audioAssetKey 用于播放)
```

### Track 模型关键字段 (从 Android 代码推断)

```typescript
interface Track {
  id: string
  title: string
  artist?: string
  album?: string
  duration_ms?: number
  audioAssetKey: string|null   // 播放资源键
  playbackStatus?: string
  version?: string
}
```

## 4. 不应直接移植到 Desktop 的资产

| 资产 | 原因 |
|---|---|
| Jetpack Compose UI | 平台特定 |
| ExoPlayer/Media3 实现 | Android 特定；Desktop 用 Chromium `<audio>` 或 Web Audio API |
| Android Activity/Fragment 生命周期 | 平台特定 |
| Android Notification | 平台特定；Desktop 用系统 Tray |
| AudioFocusManager (Android) | 平台特定；Desktop 有不同机制 |
| Android Intent 处理 | 平台特定 |
| gradle 构建系统 | 平台特定 |
| Kotlin 代码 | Desktop 用 TypeScript |

## 5. 认证现状

| 问题 | 回答 |
|---|---|
| Android 是否使用公开用户级认证？ | ⚠️ **当前看起来是公开接口** (无 token 参数) |
| 是否依赖内部 service key? | ❌ 否 — BffClient 明确注释 "Never holds internal service keys" |
| 能否作为 Desktop 协议设计参考? | ✅ **能** — 最佳参考实现 |
| 是否有共享 schema/types? | ⚠️ 无独立 schema 包，但 API 响应结构清晰 |

## 6. 结论

### 可直接复用
1. **BFF 端点 URL 结构** — 完全相同
2. **数据模型字段** — Bootstrap/Catalogue/Track
3. **错误处理模式** — ApiError 结构

### 需要适配
1. **认证** — Alpha 阶段可能延续公开访问，后续添加用户认证
2. **媒体交付** — audioAssetKey 如何转换为实际播放 URL 需确认
3. **PlaybackManifest** — 可能需要新接口或扩展 Track 响应

### Android 作为协议参考的价值: **高**

Android 的 `BffClient.kt` 是目前最完整的 BFF 消费端实现，Desktop 应遵循相同的 API 边界。

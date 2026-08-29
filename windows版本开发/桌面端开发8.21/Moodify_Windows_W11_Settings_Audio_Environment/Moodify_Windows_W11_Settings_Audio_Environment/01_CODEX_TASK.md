# Codex 执行任务书 — MFY-WIN-W11-SETTINGS-AUDIO-ENV-001

## 0. 执行模式

```text
PACKAGE = W11
FOCUS = SETTINGS_AUDIO_ENVIRONMENT
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W12 = NO
```

W11 必须建立一个小而稳定的 Settings layer。

---

## 1. Phase 0 — Preflight

读取：

```text
artifacts/windows/w10/W10_IMPLEMENTATION_REPORT.md
artifacts/windows/w10/W11_HANDOFF.md
artifacts/windows/w09/W09_IMPLEMENTATION_REPORT.md
artifacts/windows/w08/W08_IMPLEMENTATION_REPORT.md
```

输出：

`artifacts/windows/w11/preflight.md`

至少：

```text
W10_STATUS =
W11_GATE =
SETTINGS_CURRENT_REALITY =
APP_STATE_AUTHORITY =
AUDIO_OUTPUT_CAPABILITY =
TRAY_CAPABILITY =
STARTUP_CAPABILITY =
CACHE_CURRENT_REALITY =
STORAGE_CURRENT_REALITY =
CLOUD_PREFERENCE_REALITY =
```

若 `W11_GATE != PASS`，停止。

---

## 2. Phase 1 — Audit Existing Settings

先找：

- settings page / route
- preferences store
- AppState
- localStorage/JSON/SQLite preferences
- playback preferences
- tray behavior flag
- startup flag
- cache settings
- storage paths
- cloud config
- developer/internal settings
- duplicated settings stores

输出：

`artifacts/windows/w11/current-settings-reality.md`

标：

```text
WORKING
PARTIAL
PLACEHOLDER
BROKEN
MISSING
UNKNOWN
```

---

## 3. Phase 2 — Establish Settings Authority

建立/修复唯一 Settings authority。

推荐：

```text
Settings {
  schema_version

  playback {
    preferred_output_device
    restore_volume
    autoplay_policy
  }

  app {
    close_behavior
    launch_at_startup
  }

  storage {
    cache_policy
    cache_location
    data_location?
  }

  cloud {
    preparation_trigger
    fallback_to_local
    network_policy
  }
}
```

具体字段只实现真实可支持项。

### 规则

- Settings 只保存用户偏好。
- Playback session state 继续归 W04/W08。
- Queue/Playlist/Track 不进入 Settings。
- 系统能力不支持的字段不要假装可配置。

输出：

`artifacts/windows/w11/settings-authority.md`

---

## 4. Phase 3 — Schema / Defaults / Migration

必须有：

```text
settings_schema_version
```

并明确：

- defaults
- validation
- missing fields
- old version migration
- future version safe fallback
- corrupted settings fallback

### Corruption

Settings 损坏时：

```text
fallback safe defaults
```

不能清空 Library/Playlist/History。

---

## 5. Phase 4 — Audio Output Capability Audit

先审计真实 runtime：

```text
ENUMERATE_OUTPUTS
SELECT_OUTPUT
HOTPLUG_EVENTS
PERSIST_DEVICE_ID
DEFAULT_DEVICE_FOLLOW
```

标：

```text
SUPPORTED
PARTIAL
UNSUPPORTED
UNKNOWN
```

输出：

`artifacts/windows/w11/audio-output-capability.md`

### P0

没有真实切换能力：

```text
do not render functional selector
```

---

## 6. Phase 5 — Output Device Selection

若真实支持：

```text
System Default
Device A
Device B
...
```

设置：

```text
preferred_output_device_id
```

### Apply

优先：

```text
Settings
→ Playback/Audio Engine adapter
```

不得让 Settings 自己创建播放器。

### Missing Device

如果保存的 device 下次不存在：

```text
fallback System Default
keep preference or mark unavailable
```

必须明确。

推荐：

```text
fallback System Default
remember preferred device ID
if device returns, do not auto-switch mid-track unless product policy says so
```

---

## 7. Phase 6 — Device Hotplug

至少测试：

```text
Bluetooth headset appears
Bluetooth headset disappears
USB DAC appears
USB DAC disappears
default device changes
```

如果当前 runtime 无 hotplug event：
使用可行的 refresh seam。

### Safety

设备失效时：

```text
no crash
no hung Playback
fallback or pause safely
```

真实行为取决于 audio engine。

---

## 8. Phase 7 — Volume Policy

W08 已负责 volume restore。

W11 只决定用户偏好：

```text
restore_volume = ON/OFF
```

如果 OFF：
定义启动默认 volume。

推荐：

```text
system/application safe default
```

不要强制 100%。

### Never

不要因为切换 output device：
- 突然跳到 100%
- 自动播放
- 保存无效 NaN/范围外值

---

## 9. Phase 8 — Autoplay Policy

必须拆开语义。

### App Launch

默认：

```text
AUTO_PLAY_ON_LAUNCH = OFF
```

这是 W08 invariant 的延续。

### Explicit Open With

用户双击文件：

可以继续按 W09 policy：

```text
explicit open → play
```

### Playlist Click

显式按播放：
自然播放。

### Cloud Ready

W10 cloud preparation READY：

默认：

```text
do not suddenly start if user is not already waiting in playback flow
```

不要把“云准备完成”当成无条件 autoplay trigger。

输出：

`artifacts/windows/w11/autoplay-policy.md`

---

## 10. Phase 9 — Close / Tray Behavior

W09 已提供 tray capability 时，W11 才允许设置：

```text
关闭窗口时：
- 退出 Moodify
- 最小化到托盘
```

默认：

```text
退出 Moodify
```

如果 tray unsupported：
不显示该选项。

### Quit

显式退出必须：
- W08 flush
- playback teardown
- tray teardown
- single-instance release

---

## 11. Phase 10 — Launch At Startup

只在真实 runtime / installer capability 支持时开放：

```text
开机启动 Moodify
```

默认 OFF。

### Important

开机启动：

```text
launch app
but do not auto-play audio
```

如果注册必须由 installer 完成：
W11 只做 settings seam，W12 完成注册。

输出：

`artifacts/windows/w11/startup-policy.md`

---

## 12. Phase 11 — Cache Taxonomy

先明确什么是 cache。

推荐区分：

```text
THUMBNAIL/METADATA CACHE
CLOUD TEMP CACHE
PREPARED SOURCE CACHE
DOWNLOAD TEMP
```

以及：

```text
DURABLE USER DATA
```

### Durable ≠ Cache

以下不能被“清理缓存”删除：

- Library Track identity
- Playlist
- Favorite
- History
- Queue/recovery schema data（可重建 session除外）
- 用户原始音乐文件

输出：

`artifacts/windows/w11/cache-taxonomy.md`

---

## 13. Phase 12 — Cache Size & Clear

如果有实际 cache：

设置页可显示：

```text
缓存占用：X MB / GB
清理缓存
```

### Clear Cache

必须：

```text
stop/release active cached file safely
delete cache-only assets
recalculate size
```

不能：
- 删除 original source
- 删除 Track
- 删除 Playlist
- 破坏 cloud mapping identity

如果当前没有 cache：

```text
CACHE = NOT_IMPLEMENTED
```

不要显示假的 0 MB 功能。

---

## 14. Phase 13 — Storage Location

必须先区分：

```text
App Data
Cache
Downloaded/Prepared Assets
Original User Music
```

### Original User Music

Moodify 不应“移动用户原始音乐”作为 settings storage migration。

### Cache Location

如果支持修改：

```text
old cache
→ validate target
→ ensure writable
→ migrate/copy
→ verify
→ switch authority
→ cleanup old cache
```

失败则 rollback。

### App Data Location

W11 不建议允许普通用户移动 Library DB / core data，除非现有架构已经安全支持。

高风险项可以标：

```text
DEFERRED
```

输出：

`artifacts/windows/w11/storage-location-policy.md`

---

## 15. Phase 14 — Cloud Preference

只能基于 W10 已验证能力。

候选：

```text
Cloud Preparation:
- Manual
- Auto on import (only if explicitly supported and approved)
```

W11 推荐默认：

```text
Manual
```

### Fallback

```text
Cloud unavailable:
- Use local source
```

默认 ON，且建议不允许关闭，除非产品有明确需要。

### No Internal Controls

不提供：
- worker
- model
- stem
- provider
- retry count engineering knobs
- endpoint editor

---

## 16. Phase 15 — Network Policy

Windows 桌面端通常没有移动端 Wi-Fi/蜂窝语义。

只实现真实有意义项。

可能包括：

```text
Allow cloud preparation on metered connection
Background status refresh
Download/cache prepared source
```

但必须先审计 Windows/runtime 是否可识别 metered network。

如果不能：

```text
do not expose fake “仅 Wi-Fi”
```

输出：

`artifacts/windows/w11/network-policy.md`

---

## 17. Phase 16 — Reset Settings

提供：

```text
恢复默认设置
```

只能 reset Settings。

必须明确不删除：

```text
Library
Playlist
Favorites
History
Original Files
Cloud Preparation records
```

Reset 后：

- settings defaults reapply
- safe output device
- close behavior default
- autoplay off

需要确认对话框。

---

## 18. Phase 17 — Settings UI

W11 UI 要克制。

建议只做一个 secondary Settings 页面。

分组：

```text
播放
应用
存储
Moodify Cloud
```

只显示当前 build 真正支持的项目。

### Progressive Disclosure

不支持的 capability：

```text
hide
```

而不是放一个 disabled 控件写“开发中”。

### Avoid

- 30+ settings
- developer flags
- internal endpoint
- logs viewer
- DSP controls
- engineering terminology

---

## 19. Phase 18 — Apply Semantics

每个 setting 必须标：

```text
APPLY_IMMEDIATELY
APPLY_NEXT_TRACK
APPLY_NEXT_LAUNCH
INSTALLER_REQUIRED
```

例如：

- output device：immediate / next track，按真实能力
- close behavior：immediate
- launch at startup：immediate if supported
- cache location：migration then apply
- autoplay launch：next launch

输出：

`artifacts/windows/w11/settings-apply-matrix.md`

---

## 20. Phase 19 — Settings Persistence

必须：

- atomic/transaction-safe
- schema-versioned
- restart stable
- invalid enum fallback
- invalid device ID fallback
- invalid path fallback
- no secret storage

Settings file/DB 不能保存 service-key。

---

## 21. Phase 20 — Tests

### Settings
- defaults
- set/get
- restart
- invalid value
- old schema
- corruption
- reset

### Output
- select
- unavailable device
- hotplug
- system default
- restart

### Volume
- restore on/off
- clamp
- device change

### Autoplay
- normal launch never auto-plays
- explicit open still follows W09
- cloud-ready does not surprise-play

### Tray/Close
- quit
- minimize to tray if enabled/supported
- explicit quit
- recovery flush

### Cache
- size
- clear
- active file
- no durable data loss

### Storage
- target invalid
- no permission
- migration success
- migration rollback

### Cloud
- manual default
- verified options only
- offline local fallback

### Regression
- W02-W10 all main flows
- no new business authority
- no Canon change

---

## 22. Required Outputs

写入：

`artifacts/windows/w11/`

至少：

1. `W11_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `current-settings-reality.md`
4. `settings-authority.md`
5. `settings-schema.md`
6. `audio-output-capability.md`
7. `audio-output-policy.md`
8. `autoplay-policy.md`
9. `close-tray-policy.md`
10. `startup-policy.md`
11. `cache-taxonomy.md`
12. `storage-location-policy.md`
13. `cloud-preference-policy.md`
14. `network-policy.md`
15. `settings-apply-matrix.md`
16. `settings-test-report.md`
17. `evidence-manifest.json`
18. `W12_HANDOFF.md`

---

## 23. Definition of Done

必须证明：

```text
Settings
→ validated
→ applied to existing subsystem
→ persisted
→ restart stable
```

同时：

```text
unsupported capability
→ not faked in UI
```

以及：

```text
Reset/Clear Cache
→ never destroys durable user data
```

最后：

```text
W11_STATUS = PASS | PARTIAL | BLOCKED
W12_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

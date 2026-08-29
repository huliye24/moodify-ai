# MFD-004 — Playback Vertical Slice
## Codex 正式执行任务书

**任务编号：** MFD-004  
**执行对象：** Codex  
**执行模式：** 真实纵向贯通 / 最小播放引擎 / 证据驱动  
**前置条件：** MFD-003 = GO

---

# 0. 核心目标

不要开始“做播放器产品”。

本包只做一条纵向切片：

```text
Session
→ Track
→ PlaybackManifest
→ Media URL
→ PlaybackEngine
→ Audio Output
```

如果这条链路没有真实贯通，其他 UI、产品化和设计工作都没有意义。

---

# 1. 阶段 A — Preflight

开始前确认：

- MFD-003 = GO；
- Desktop repo clean；
- Player API 可访问；
- 有至少 1 首真实 READY track；
- PlaybackManifest 可取得；
- stream URL 可访问；
- Windows 测试设备存在；
- 默认音频输出设备工作正常；
- 不使用 service-key；
- 不修改 production processing pipeline。

记录：

```text
desktop branch
desktop SHA
backend version / deployment reference
test track id
playback asset version
Windows version
Electron version
```

---

# 2. Playback Domain Model

建立最小领域模型：

```text
PlaybackState =
  IDLE
  LOADING
  READY
  PLAYING
  PAUSED
  ENDED
  ERROR
```

不要把 Cloud 内部状态机复制进 Desktop。

Track 云端状态与播放本地状态必须分开：

```text
Cloud track status
!=
Desktop playback state
```

---

# 3. PlaybackEngine Interface

必须定义稳定接口，例如：

```ts
interface PlaybackEngine {
  load(source: PlaybackSource): Promise<void>
  play(): Promise<void>
  pause(): Promise<void>
  seek(positionMs: number): Promise<void>
  stop(): Promise<void>
  getState(): PlaybackState
  getPosition(): number
  getDuration(): number
  setVolume(value: number): void
  dispose(): Promise<void>
}
```

具体方法可根据工程情况调整。

要求：

> 上层 UI 不直接操纵 `<audio>` 元素。

这样未来可替换底层。

---

# 4. ChromiumPlaybackEngine

本包只实现：

```text
ChromiumPlaybackEngine
```

可基于：

- HTMLMediaElement
- Web Audio API
- 两者组合

优先选择：

> 最简单、最稳定、最少额外依赖的实现。

不要引入：

- VLC
- mpv
- FFmpeg native player
- libVLC
- PortAudio
- WASAPI addon

除非真实验证证明 Chromium 无法播放当前 Moodify 资产格式。

如发生格式兼容问题：

1. 先记录；
2. 判断是编码 / MIME / range / CORS / signed URL 问题；
3. 优先修正云端交付格式；
4. 不要直接跳到 native engine。

---

# 5. PlaybackSource

建议：

```text
PlaybackSource {
  playbackId
  trackId
  url
  mimeType
  durationMs
  expiresAt
  assetVersion
}
```

不要携带：

- service key
- raw storage credential
- internal object secret
- stems
- DSP params
- Ear judgment

---

# 6. Manifest Expiry Handling

播放 URL 是临时资源。

必须处理：

```text
manifest valid
→ load

manifest near expiry / expired
→ request new PlaybackManifest
→ reload source when safe
```

首版无需做无缝刷新。

但：

> 不允许把 expired signed URL 当成永久错误缓存。

---

# 7. Load

`load()` 必须验证：

- URL exists；
- MIME recognized；
- resource reachable；
- media metadata loaded；
- duration usable；
- error event captured。

对 range request 的支持要真实验证。

音频播放器常需要：

```text
Accept-Ranges / partial content
```

如不支持 Seek，必须记录真正原因。

---

# 8. Play / Pause

要求：

- play command 成功；
- state 更新；
- pause 后 position 保留；
- resume 从当前位置继续；
- repeated play 不创建多个实例；
- rapid click 不造成多个音轨叠加。

---

# 9. Seek

至少验证：

```text
seek to 25%
seek to 50%
seek near end
```

要求：

- state 不错乱；
- position 真实变化；
- signed URL / range 正常；
- seek 后可以继续播放。

如当前媒体交付不支持 Seek：

> MFD-004 不得标 GO，除非明确降级策略被人类批准。

---

# 10. Ended

自然播放结束时：

```text
PLAYING
→ ENDED
```

必须：

- 释放必要资源；
- position / duration 状态正确；
- 不自动无限重播；
- next hook 可以触发。

---

# 11. Next / Previous

MFD-004 只要求最小链路。

可以使用：

```text
local test queue
```

例如真实云端返回 2–3 首 track 后，在 Desktop 形成一次性 local playback order。

明确：

> local test queue 不是 Cloud canonical queue。

验证：

```text
track A → next → track B
track B → previous → track A
```

不要实现完整 playlist product。

---

# 12. Volume

首版只要求：

```text
0.0 → 1.0
```

验证：

- mute 可通过 volume=0；
- volume 不超范围；
- volume 变化不 reload track。

MFD-006 才负责持久化。

---

# 13. Minimal Debug UI

允许为了验证建立一个**工程调试页**：

```text
Track title
State
Position / Duration

[Load]
[Play]
[Pause]
[Previous]
[Next]

Seek slider
Volume slider
```

页面必须清楚标记：

> `DEVELOPMENT PLAYBACK HARNESS`

不要把它做成 Moodify 正式视觉。

MFD-005 会替换它。

---

# 14. Renderer / Main Boundary

PlaybackEngine 可以位于 renderer，因为 Chromium media API 天然在那里。

但必须保证：

- auth/session secret handling遵守 MFD-003；
- signed URL 生命周期受控；
- renderer 不获得 server secret；
- API client boundary 不被破坏。

如果架构选择 Main 获取 manifest、Renderer 接收 sanitized PlaybackSource：

> 优先。

不要为了“所有东西都放 main”而写复杂 IPC。

也不要为了方便把 auth 逻辑散在 UI。

---

# 15. Audio Asset Compatibility

对至少一首真实资源记录：

```text
container
codec
sample rate
bit depth if known
channels
duration
mime
content length
range support
```

这是事实记录，不是高保真营销。

不要宣称：

- lossless
- hi-res
- bit-perfect
- studio quality

除非有严格证据。

---

# 16. Error Model

至少处理：

```text
MANIFEST_FETCH_FAILED
PLAYBACK_URL_EXPIRED
MEDIA_NOT_FOUND
MEDIA_UNSUPPORTED
MEDIA_LOAD_FAILED
MEDIA_DECODE_FAILED
SEEK_UNSUPPORTED
NETWORK_INTERRUPTED
PLAY_REJECTED
UNKNOWN_PLAYBACK_ERROR
```

错误必须映射成 Desktop 领域错误。

禁止把 Chromium 原始错误直接当最终产品协议。

---

# 17. Network Interruption

至少人工验证：

1. 播放中断网；
2. 保持 10–30 秒；
3. 恢复网络；
4. 观察播放器行为。

MFD-004 不要求完美自动恢复。

但必须：

- 不崩溃；
- 状态变成可理解状态；
- 用户可以 retry / reload；
- 恢复网络后能够重新开始播放。

复杂 resilience 留给 MFD-006。

---

# 18. Expired URL Test

必须人工或自动模拟：

```text
expired PlaybackManifest
```

验证：

- 不无限 retry；
- 能识别过期；
- 重新获取 manifest；
- 重新 load；
- 正常播放。

---

# 19. Resource Cleanup

切歌 / stop / reload 时：

- 不残留多个 media element；
- 不产生多重 event listener；
- 不重复输出；
- 不无限增长 object / timer；
- dispose 可重复调用且安全。

---

# 20. Telemetry / Evidence

本包不引入重型 analytics。

但至少记录开发证据：

```text
playback_id
track_id
asset_version
load latency
time to first audio
play/pause/seek result
ended
error code
```

敏感 URL 必须 redacted。

---

# 21. 测试层级

## Unit

至少：

- playback state reducer / state model
- URL expiry decision
- error mapping
- queue next/previous logic

## Integration

至少：

- mock PlaybackSource load
- play/pause transition
- seek transition
- ended transition
- reload after expiry

## Real Windows Smoke

必须真实人工执行：

- 真实云端 track
- 真实 manifest
- 真实扬声器 / 耳机输出
- Play
- Pause
- Resume
- Seek
- Next
- Previous
- End / near-end
- network interruption
- retry

不能用测试通过代替真实“听到声音”。

---

# 22. Audio Verification Record

因为播放最终是听觉行为，必须有人类确认：

```text
Audible: YES / NO
Unexpected distortion: YES / NO / UNKNOWN
Unexpected speed change: YES / NO
Channel anomaly: YES / NO / UNKNOWN
Obvious truncation: YES / NO
```

这不是主观音质评分。

只是确认播放链没有明显破坏音频。

---

# 23. 禁止项

严禁：

- 正式 Moodify UI
- vinyl UI
- skin
- lyrics
- visualizer
- playlist management
- favorite
- recommendation
- tray
- media key
- global shortcut
- auto update
- installer productization
- offline library
- local music import
- upload
- DSP editor
- EQ
- compressor
- limiter
- resampling control
- WASAPI
- ASIO
- native addon
- bit-perfect claim
- hi-res claim
- complex caching
- background download
- gapless
- crossfade
- replay gain
- loudness normalization controls

---

# 24. Definition of Done

必须全部满足：

1. 真实 Player API 可用；
2. 真实 track 可用；
3. 真实 PlaybackManifest 可用；
4. ChromiumPlaybackEngine 实现；
5. Play 成功；
6. Windows 真实发声；
7. Pause / Resume 成功；
8. Seek 成功；
9. Next / Previous 最小链路成功；
10. Ended 状态正确；
11. Volume 生效；
12. expired URL 可恢复；
13. 网络中断不崩溃；
14. 没有重复播放实例；
15. 没有 server secret；
16. 没有 native audio scope creep；
17. unit / integration tests 通过；
18. Windows smoke 有真实证据；
19. human audible verification 完成；
20. evidence 文档完成。

---

# 25. 最终回报

Codex 最终报告：

1. test environment
2. test tracks
3. playback architecture
4. PlaybackEngine implementation
5. media compatibility
6. play/pause/seek results
7. next/previous result
8. expiry test
9. network interruption test
10. human audible verification
11. known limitations
12. diff summary
13. MFD-005 readiness

最后：

> `MFD-005: GO / CONDITIONAL GO / NO-GO`

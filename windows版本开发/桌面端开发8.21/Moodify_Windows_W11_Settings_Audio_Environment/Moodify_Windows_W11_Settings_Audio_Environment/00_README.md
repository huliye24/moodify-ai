# Moodify Windows Desktop Completion — W11 Settings & Audio Environment

**Package ID:** `MFY-WIN-W11-SETTINGS-AUDIO-ENV-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 11 of 12  
**任务类型：** Product Configuration / Audio Environment  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W10 `W11_GATE = PASS`  
**下一包：** W12 — Release Hardening 发布工程

---

## 1. W11 的目标

W11 不是建设“高级设置中心”，而是把前面已经稳定的能力收拢成一套克制、可恢复、不会破坏播放链路的用户设置。

目标：

```text
User Preference
→ Settings Authority
→ Validate
→ Apply to Existing Subsystem
→ Persist
→ Restart
→ Still Correct
```

重点包括：

```text
Audio Output
Playback Preferences
Close / Tray Behavior
Startup Behavior
Cache
Storage
Network / Cloud Preference
Reset / Recovery
```

---

## 2. 最重要的原则

### Settings 不是第二套业务状态

Settings 可以决定：

```text
“我希望怎样使用 Moodify”
```

但不能重新拥有：

```text
Track
Library
Playlist
Queue
Playback
CloudPreparation
```

例如：

```text
preferred_output_device
```

可以属于 Settings。

但：

```text
current_track_id
```

仍然属于 Playback/Recovery，不属于 Settings。

---

## 3. 前置门槛

执行前读取：

```text
artifacts/windows/w10/W10_IMPLEMENTATION_REPORT.md
artifacts/windows/w10/W11_HANDOFF.md
artifacts/windows/w09/W09_IMPLEMENTATION_REPORT.md
artifacts/windows/w08/W08_IMPLEMENTATION_REPORT.md
```

W10 可以是：

```text
PASS
or
PARTIAL
```

但必须：

```text
W11_GATE = PASS
```

若：

```text
W11_GATE != PASS
```

则：

```text
W11_STATUS = BLOCKED
```

---

## 4. 本包要做

- 唯一 Settings authority
- settings schema/version/defaults
- validation/migration
- audio output capability audit
- output device selector（仅真实 runtime 支持时）
- device hotplug / missing-device fallback
- volume/startup audio behavior
- autoplay policy
- close/tray behavior
- optional launch-at-startup capability seam
- cache policy
- cache clear
- cache size visibility
- storage location policy
- safe storage relocation/migration
- cloud preparation preference
- network behavior
- retry/download policy user preferences
- reset settings
- settings persistence
- tests/evidence

---

## 5. 本包不做

- EQ
- DSP 参数
- stem controls
- Ear controls
- sample-level tuning
- ASIO 独占模式，除非当前真实 runtime 已有明确、安全、稳定能力并且已有产品需求
- 音频工程高级参数面板
- developer settings
- internal API endpoint editor
- service-key input
- creator backend
- skin/community settings
- account redesign
- UI redesign

---

## 6. W11 完成后的设置应非常少

建议最终用户看到的设置大致只有：

```text
播放
- 输出设备
- 音量恢复
- 自动播放行为

应用
- 关闭窗口时
- 开机启动（仅支持时）

存储
- 缓存大小
- 清理缓存
- 数据/缓存位置（仅安全支持时）

Moodify Cloud
- 云端准备方式
- 仅 Wi-Fi / 允许移动网络（如平台有意义）
- 网络失败后的行为
```

Windows 桌面端没有“移动网络”语义时不要机械照搬。

---

## 7. 产品默认值

推荐初始默认：

```text
Output Device = System Default
Restore Volume = ON
Auto Play On App Launch = OFF
Close Window = Quit
Launch At Startup = OFF
Cloud Preparation = Manual
Cloud Failure = Fallback Local
Cache = Automatic
```

所有默认值必须记录，并可以随着未来版本 migration。

---

## 8. Audio Environment 的真实边界

如果当前 runtime 无法可靠枚举/切换 output device：

```text
OUTPUT_DEVICE_SELECTOR = UNSUPPORTED
```

不要造一个假的下拉框。

如果只支持 system default：

UI 只显示：

```text
系统默认
```

真实能力优先于“设置项数量”。

---

## 9. W11 完成后的用户体验

用户可以：

```text
选择耳机作为输出设备
→ 播放立即切换/下一次播放生效（按真实能力）
→ 拔掉耳机
→ 自动安全回到系统默认
```

以及：

```text
关闭窗口
→ 按自己的设置退出或最小化到托盘
```

以及：

```text
清理缓存
→ 不影响 Library
→ 不删除原始音乐
→ 不删除 Playlist
→ 不破坏 Track identity
```

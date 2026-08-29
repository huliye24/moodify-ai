# Codex 执行任务书 — W09 Windows Native Integration

## 0. 执行模式

```text
PACKAGE = W09
FOCUS = WINDOWS_NATIVE_INTEGRATION
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W10 = NO
```

禁止假设 Electron、Tauri、WebView2、WinUI 或其他栈。先从 W01-W08 evidence 和当前工作区确认真实 runtime。

## 1. Preflight

读取：

```text
artifacts/windows/w08/W08_IMPLEMENTATION_REPORT.md
artifacts/windows/w08/W09_HANDOFF.md
artifacts/windows/w04/playback-authority.md
artifacts/windows/w05/queue-authority.md
```

输出 `artifacts/windows/w09/preflight.md`：

```text
W08_STATUS =
W09_GATE =
DESKTOP_RUNTIME =
NATIVE_BRIDGE =
PLAYBACK_AUTHORITY =
QUEUE_AUTHORITY =
TRACK_AUTHORITY =
WINDOW_LIFECYCLE =
SINGLE_INSTANCE_REALITY =
MEDIA_CONTROL_REALITY =
TRAY_REALITY =
OPEN_FILE_REALITY =
```

若 `W09_GATE != PASS`，停止。

## 2. Windows capability audit

建立 `windows-capability-matrix.md`，对以下能力标记：

```text
SUPPORTED
SUPPORTED_WITH_ADAPTER
INSTALLER_REQUIRED
RUNTIME_BLOCKED
NOT_APPLICABLE
UNKNOWN
```

覆盖：

- media keys
- Windows System Media Transport Controls / 等价接口
- playback state projection
- title/artist/album metadata
- timeline/seek
- previous/next callbacks
- tray
- taskbar identity/integration
- single instance
- second-instance args
- open-file event
- file association registration
- lock-screen/system media metadata

只实施高价值且当前 runtime 能安全支持的能力。

## 3. Native adapter

建立窄边界，例如：

```text
WindowsNativeAdapter
- registerMediaControls
- updatePlaybackState
- updateMediaMetadata
- registerSingleInstance
- onOpenFiles
- tray
- taskbar
```

禁止 adapter 维护第二套 Track、Queue、Playback。

## 4. Media Keys / System Controls

支持：

```text
Play
Pause
Play/Pause
Previous
Next
```

如果系统可靠支持 seek，可接 `Playback.seek()`。

路由必须是：

```text
Play/Pause → W04 Playback
Previous/Next → W05 Queue → W04 Playback
```

测试 focused/background/minimized/rapid key/no current Track。

不要使用不必要的全局键盘 hook；优先原生 media API。

## 5. System metadata

Track projection：

```text
title
artist
album
duration
artwork only if already reliable
```

复用 W06 metadata fallback。

禁止向 Windows 泄露：
- 本地完整路径
- Ear / Evidence / stem 内部状态
- cloud internal IDs
- secret/token

Track 切换时更新一次 metadata；退出时清理 system media state。

## 6. Single Instance

只允许一个长期主实例。

第二实例：

```text
parse invocation
→ structured handoff
→ primary handles
→ optional window activation
→ secondary exits
```

不得允许两个实例同时写：
- Library persistence
- Playlist
- Queue snapshot
- Recovery snapshot

这是 P0。

## 7. Open File / Open With

处理等价于：

```text
Moodify.exe <audio files>
```

必须复用：

```text
W02 Import
→ Track
→ W05 Queue
→ W04 Playback
```

推荐：

单文件：
```text
import/resolve
→ play
```

多文件：
```text
按参数顺序 import
→ Queue
→ play first valid
```

坏文件不阻塞其他有效文件。

## 8. File association seam

建立 `file-association-plan.md`：

- 支持格式必须来自真实 import/decode capability
- 应用侧 open contract
- installer 注册需求
- uninstall cleanup
- upgrade behavior
- user default-app choice

不得强制抢占 Windows 默认播放器。Installer 注册可留到 W12。

## 9. Tray / Taskbar

Tray 如 runtime 安全支持，保持极简：

```text
打开 Moodify
播放/暂停
下一首
退出
```

W09 不偷偷把 Close 改成“最小化到托盘”；默认 Close=Quit 的产品语义保持不变，设置留 W11。

Tray Quit：

```text
W08 snapshot flush
→ native teardown
→ release single-instance lock
→ exit
```

Taskbar 只做真正有价值的 app identity/window activation 等，不为了数量加入无意义进度条。

## 10. Native security

必须审计：

- IPC allowlist
- payload schema
- second-instance payload
- argv parsing
- file path validation
- shell calls
- arbitrary URL/command
- renderer OS permission

禁止：

```text
eval
generic execute
cmd.exe /c <user-string>
powershell <user-string>
shell=True with user path
```

使用 runtime 自带 argv/event parser，不手工按空格 split command line。

测试中文、空格、引号、&、括号、Unicode、长路径、多文件。

## 11. State synchronization

```text
Playback changed → Windows playback state
Track changed → Windows metadata
Queue changed → previous/next availability
```

防止：
- stale title
- paused but Windows says Playing
- duplicate subscriptions
- quit 后旧 system session 残留

## 12. Tests

至少：

### Media
play/pause/next/previous/rapid/no Track/background

### Metadata
normal/missing/Unicode/track switch/quit

### Single instance
second launch/file handoff/rapid launches/minimized primary/malformed payload

### Open file
one/multiple/duplicate/unsupported/Chinese path/space path

### Security
shell metacharacters/malformed IPC/unexpected command

### Regression
W02-W08 全主链；不得新增第二套 Playback/Queue/persistence authority。

## 13. Required Outputs

写入 `artifacts/windows/w09/`：

1. `W09_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `windows-capability-matrix.md`
4. `native-adapter-boundary.md`
5. `media-control-routing.md`
6. `system-metadata-policy.md`
7. `single-instance-contract.md`
8. `open-file-contract.md`
9. `file-association-plan.md`
10. `tray-taskbar-policy.md`
11. `native-security-review.md`
12. `native-test-report.md`
13. `evidence-manifest.json`
14. `W10_HANDOFF.md`

## 14. Definition of Done

```text
Windows command
→ existing Moodify authority
```

以及：

```text
Second launch / Open With
→ primary Moodify
→ existing import/play path
→ no duplicate long-running instance
```

最后：

```text
W09_STATUS = PASS | BLOCKED
W10_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

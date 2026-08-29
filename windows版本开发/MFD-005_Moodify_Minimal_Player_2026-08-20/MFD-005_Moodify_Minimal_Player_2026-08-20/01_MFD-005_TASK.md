# MFD-005 — Moodify Minimal Player
## Codex 正式执行任务书

**任务编号：** MFD-005  
**执行对象：** Codex  
**执行模式：** 产品界面收敛 + 最小交互 + 视觉与播放状态统一  
**前置条件：** MFD-004 = GO

---

# 0. 核心目标

本包不继续扩展播放技术。

本包要把：

```text
DEVELOPMENT PLAYBACK HARNESS
```

替换成：

```text
Moodify Minimal Player
```

并保证首屏几乎只表达一个动作：

> **Play**

---

# 1. Preflight

执行前确认：

- MFD-004 = GO；
- 真实播放链路可用；
- PlaybackEngine 可复用；
- Desktop repo clean；
- 不修改 Cloud contract；
- 不修改 Ear；
- 不修改音频处理 pipeline；
- 不修改生产媒体资产。

如果 MFD-004 尚未真实发声：

> 停止本包。

不要用 UI 掩盖播放链未完成的问题。

---

# 2. UI 信息层级

首屏信息优先级必须是：

```text
1. Moodify
2. 当前曲目
3. Play / Pause
4. 切歌
5. 进度
6. 音量
```

任何低于此优先级的信息，都不应该抢视觉注意力。

---

# 3. 主界面结构

建议：

```text
App Shell
│
├── Brand
│   └── Moodify
│
├── Disc / Primary Visual
│
├── Track Identity
│   ├── title
│   └── artist
│
├── Primary Control
│   └── Play / Pause
│
├── Progress
│
└── Minimal Secondary Controls
    ├── previous
    ├── next
    └── volume
```

允许根据窗口比例调整布局，但不要增加复杂区域。

---

# 4. 黑胶 / Disc 视觉

Moodify 已经形成过一个明确视觉方向：

> 黑胶唱片 / 唱片作为播放中心视觉。

本包可以实现：

- 极简圆形唱片
- 中心标签
- 轻微旋转
- 播放时转动
- 暂停时停止或缓慢停下

禁止：

- 复杂 3D
- shader
- WebGL 重型效果
- 大量粒子
- 音频频谱动画
- 视觉噪音

视觉是陪衬。

不是产品核心。

---

# 5. Play / Pause

Play 必须是整个页面最清晰的动作。

要求：

- 空间位置稳定；
- 状态切换清楚；
- 键盘 Space 可触发；
- repeated rapid click 不产生异常；
- loading 时有明确但克制的反馈；
- error 时不让按钮进入假播放状态。

---

# 6. 切歌

至少支持：

```text
Previous
Next
```

以及：

```text
↑ / ↓
```

如果窗口/设备允许：

> 鼠标滚轮 / 触控板上下滚动可用于切歌。

但必须防止：

- 一个滚轮动作连续切 10 首；
- scroll gesture 与普通页面滚动冲突；
- 页面本身产生无意义纵向滚动。

建议做：

```text
debounce / threshold
```

---

# 7. 进度

进度条必须：

- 显示当前 position；
- 显示总 duration；
- 支持 seek；
- loading 时状态明确；
- seek 时不出现明显跳动；
- ended 后正确到终点。

首版不需要：

- waveform
- buffered range visualization
- chapter marker
- lyrics sync

---

# 8. 音量

首版音量只需要：

- slider
- mute behavior
- 0–100%

不要加入：

- dB 数值
- preamp
- gain
- limiter
- normalization
- balance
- channel control

---

# 9. Track Identity

只显示：

```text
title
artist
```

如果当前没有 artist：

可安全降级。

不要显示：

- internal track id
- asset version
- codec
- sample rate
- processing status
- preset name
- model name

---

# 10. Loading State

加载状态要非常克制。

例如：

```text
Preparing…
```

或一个轻量 spinner。

禁止：

- 把 Cloud pipeline 暴露为 10 个步骤；
- 显示内部 processing worker；
- 显示分轨状态；
- 显示 Ear 判断过程。

用户只需要知道：

> 这首歌还没准备好播放。

---

# 11. Error State

首版错误只允许表达用户可行动的信息。

例如：

```text
无法播放这首歌
[重试]
```

或者：

```text
网络连接中断
[重试]
```

不要显示：

- traceback
- signed URL
- HTTP headers
- internal error object
- service name
- storage bucket

---

# 12. Empty State

如果没有可播放曲目：

显示极简空状态：

```text
暂无可播放音乐
```

不要自动引入：

- upload page
- onboarding wizard
- marketplace
- recommendation feed

这些不是本包范围。

---

# 13. Window Behavior

本包只做主窗口。

建议：

- 可缩放；
- 定义合理最小宽高；
- 默认窗口适合桌面播放器；
- 不全屏强制；
- 不多窗口；
- 不 mini player。

不要过早做 frameless window，除非当前实现已经稳定且不影响系统行为。

---

# 14. Keyboard

至少：

```text
Space      Play / Pause
↑          Previous
↓          Next
←          seek backward optional
→          seek forward optional
```

如果使用左右 seek：

建议固定一个轻量步长。

不要做：

- 全局快捷键
- media key
- system-wide hook

MFD-007 再做。

---

# 15. Theme Tokens

本包可以第一次正式建立：

```text
theme/
├── colors
├── typography
├── spacing
├── radius
└── motion
```

但目的不是做“皮肤系统”。

目的只是：

> 让未来皮肤系统有统一设计变量入口。

禁止：

- runtime skin marketplace
- user theme package
- theme publishing
- remote theme loading

---

# 16. Visual Language

Moodify 当前视觉应强调：

- 简洁
- 克制
- 留白
- 主体明确
- 少按钮
- 少文字
- 少技术信息

不要使用：

- dashboard 风格
- 企业 SaaS 风格
- 复杂 card grid
- 多侧栏
- 巨量图标
- 彩色状态徽章
- 开发者工具风格

---

# 17. Accessibility

至少保证：

- Play 可键盘操作；
- focus 可见；
- 按钮有 accessible label；
- slider 可键盘操作；
- 不只靠颜色区分状态；
- 动画尊重 `prefers-reduced-motion`。

不要因为“极简”牺牲基本可用性。

---

# 18. Responsive

至少覆盖：

```text
compact desktop window
normal desktop window
wide desktop window
```

不要求手机响应式。

这是 Desktop。

---

# 19. Performance

首屏不应：

- 加载巨大图片；
- 引入重型动画库；
- 引入 WebGL；
- 引入大量第三方 UI framework。

如果工程已经有轻量 UI 基础，可以复用。

不要为了一个 Play 按钮引入整套重量级组件系统。

---

# 20. 状态来源

UI 状态必须来自已有领域状态。

不要重新定义第二套播放状态。

例如：

```text
PlaybackState
→ UI presentation
```

而不是：

```text
PlaybackState
+
UIPlaybackState
+
VisualPlaybackState
```

形成三套互相漂移状态。

---

# 21. Development Harness 去留

MFD-004 的 debug harness 不应继续作为正式首页。

可以：

- 移入 dev-only route；
- 移入 `tools/`；
- 保留仅开发环境可访问。

但用户默认看不到。

---

# 22. 产品模式与开发模式分离

建议：

```text
Production UI
Development Diagnostics
```

通过明确环境控制。

不要在正式 UI 底部常驻：

- FPS
- playback_id
- manifest
- endpoint
- error JSON

---

# 23. Tests

至少：

## UI unit
- play button state
- loading state
- error state
- empty state
- track identity
- progress formatting

## Interaction
- Space play/pause
- up/down next/previous
- progress seek
- volume
- wheel debounce if implemented

## Integration
- real PlaybackEngine state → UI
- error → retry
- ended → next behavior according to current queue logic

## Windows smoke
人工确认：

- UI 可理解
- Play 可见
- keyboard 可用
- resize 不破
- real track 可播放
- no debug info leak

---

# 24. 禁止项

严禁：

- playlist management product
- library browser
- search
- upload
- favorites
- social
- comments
- recommendation
- lyrics
- visualizer
- waveform
- spectrum
- EQ
- DSP panel
- preset selector
- audio settings panel
- WASAPI
- ASIO
- system tray
- media key
- auto update
- installer productization
- skin marketplace
- remote themes
- multiple windows
- mini player

---

# 25. Definition of Done

必须全部满足：

1. debug harness 不再是默认 UI；
2. Moodify Minimal Player 成为默认界面；
3. Play / Pause 清楚；
4. 当前曲目 title / artist 清楚；
5. Previous / Next 可用；
6. Space / ↑ / ↓ 可用；
7. Seek 可用；
8. Volume 可用；
9. Loading 清楚；
10. Error 可重试；
11. Empty state 存在；
12. Disc / Vinyl 视觉轻量存在或明确说明未采用原因；
13. 动画不影响性能；
14. keyboard accessibility 通过；
15. resize 通过；
16. debug info 不泄露；
17. 真实云端曲目仍可播放；
18. test 通过；
19. Windows smoke 通过；
20. 没有扩入 MFD-006 / 007 范围。

---

# 26. 最终回报

Codex 最终只报告：

1. UI structure
2. interaction map
3. visual decisions
4. playback state binding
5. accessibility
6. tests
7. Windows smoke
8. removed / hidden debug UI
9. known limitations
10. diff summary
11. MFD-006 readiness

最后：

> `MFD-006: GO / CONDITIONAL GO / NO-GO`

# Audio Output Policy

## Capability First

必须先确认：

```text
Can enumerate outputs?
Can select output?
Can observe hotplug?
Can persist a device identity?
```

## Default

```text
preferred_output_device = SYSTEM_DEFAULT
```

## Missing Device

推荐：

```text
saved device unavailable
→ fallback system default
→ mark preferred device unavailable
```

不要在播放中自动反复抢回刚恢复的蓝牙设备。

## Hotplug

设备出现/消失：
- refresh device list
- keep Playback stable
- fallback/pause according to engine reality
- no crash

## Volume

切换设备不能重置到 100%。

## Privacy

只保存 runtime 必需的 device ID/label。
不要把完整低层设备诊断暴露到 UI。

## Unsupported

如果 runtime 只能跟系统默认：
UI 只提供“系统默认”或隐藏设备选择。
